"""python -m evaluation.runner --limit 3 --methods direct ps ltm rar1 rar2"""
import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import time
import uuid

from shared.model_client import ModelClient, ModelSettings
from shared.prompts import PROMPT_VERSION
from experiments.baselines.strategy import run as direct
from planning.plan_and_solve.strategy import run as ps
from decomposition.least_to_most.strategy import run as ltm
from rewriting.rephrase_and_respond.strategy import run_one, run_two

METHODS = {"direct": direct, "ps": ps, "ltm": ltm, "rar1": run_one, "rar2": run_two}
ROOT = Path(__file__).resolve().parents[1]


def append_json(path, row):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_answer(text):
    lines = text.strip().splitlines()
    if not lines or not re.fullmatch(r"FINAL:\s*\S.*", lines[-1]):
        raise ValueError("answer_format: last line must be FINAL: <answer>")
    return lines[-1].split(":", 1)[1].strip()


def grade(answer, case):
    if case["kind"] == "number":
        try:
            actual, expected = Decimal(answer), Decimal(case["answer"])
            return actual.is_finite() and actual == expected
        except InvalidOperation:
            return False
    return " ".join(answer.split()) == " ".join(case["answer"].split())


def execute_case(client, method, case):
    start, offset = time.monotonic(), len(client.calls)
    row = {"case_id": case["id"], "method": method, "status": "failed", "correct": False,
           "answer": None, "output": None, "error": None}
    try:
        row["output"] = METHODS[method](client, case["question"])
        row["answer"] = parse_answer(row["output"])
        row["correct"] = grade(row["answer"], case)
        row["status"] = "success"
    except Exception as exc:
        row["error"] = {"type": type(exc).__name__, "message": str(exc)}
    calls = client.calls[offset:]
    row["call_count"] = len(calls)
    row["elapsed_s"] = round(time.monotonic() - start, 6)
    row["tokens"] = (sum(c["usage"]["total_tokens"] for c in calls)
                     if calls and all(c["usage"] and c["usage"].get("total_tokens") is not None for c in calls)
                     else None)
    return row


def summarize(rows):
    baseline = {r["case_id"]: r for r in rows if r["method"] == "direct"}
    summary = {}
    for method in dict.fromkeys(r["method"] for r in rows):
        selected = [r for r in rows if r["method"] == method]
        pairs = [r for r in selected if r["case_id"] in baseline]
        summary[method] = {
            "attempted": len(selected), "correct": sum(r["correct"] for r in selected),
            "accuracy": sum(r["correct"] for r in selected) / len(selected),
            "execution_success": sum(r["status"] == "success" for r in selected),
            "errors": dict(Counter(r["error"]["type"] for r in selected if r["error"])),
            "baseline_correct_to_wrong": sum(baseline[r["case_id"]]["correct"] and not r["correct"] for r in pairs),
            "paired_with_baseline": len(pairs),
            "call_count": sum(r["call_count"] for r in selected),
            "elapsed_s": round(sum(r["elapsed_s"] for r in selected), 6),
            "tokens": sum(r["tokens"] for r in selected) if all(r["tokens"] is not None for r in selected) else None,
        }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--dataset", type=Path, default=ROOT / "evaluation/datasets/pilot.jsonl")
    args = parser.parse_args()
    if args.limit < 1 or len(set(args.methods)) != len(args.methods):
        parser.error("limit must be positive and methods must be unique")
    data = args.dataset.read_bytes()
    cases = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()][:args.limit]
    if not cases or len({c["id"] for c in cases}) != len(cases):
        parser.error("dataset must be nonempty with unique case IDs")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    directory = ROOT / "results" / run_id
    directory.mkdir(parents=True)
    settings = ModelSettings()
    manifest = {"run_id": run_id, "settings": asdict(settings), "prompt_version": PROMPT_VERSION,
                "methods": args.methods, "dataset_sha256": hashlib.sha256(data).hexdigest(),
                "case_count": len(cases), "price": None,
                "scope": "Self-authored exploratory pilot; not paper benchmark reproduction."}
    # Snapshot executed source, lockfile and selected inputs to keep each run reviewable.
    sources = list(ROOT.glob("**/strategy.py")) + [ROOT / "shared/model_client.py", ROOT / "shared/prompts.py", Path(__file__)]
    manifest["source_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if ".venv" not in p.parts}
    lock = ROOT / "uv.lock"
    manifest["lock_sha256"] = hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None
    (directory / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "inputs.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = []
    for case in cases:
        for method in args.methods:
            def sink(call):
                append_json(directory / "calls.jsonl", {"case_id": case["id"], "method": method, **call})
            client = ModelClient(settings, sink=sink)
            row = execute_case(client, method, case)
            append_json(directory / "results.jsonl", row)
            rows.append(row)
            print(f"{case['id']} {method}: {row['status']} correct={row['correct']} calls={row['call_count']}", flush=True)
    (directory / "summary.json").write_text(json.dumps(summarize(rows), ensure_ascii=False, indent=2), encoding="utf-8")
    print(directory, flush=True)
    return 0 if all(r["status"] == "success" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
