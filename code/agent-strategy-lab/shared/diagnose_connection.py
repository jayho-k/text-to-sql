"""Read-only network/API diagnostics; no model download or server change."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import time
from urllib.parse import urlsplit
import httpx

HOST = "jayho-macmini.tail60408a.ts.net"
BASE = "https://" + HOST


def probe(mode, path):
    start = time.monotonic()
    result = {"mode": mode, "path": path}
    try:
        with httpx.Client(trust_env=(mode == "environment_proxy"), timeout=12) as client:
            response = client.get(BASE + path, headers={"Authorization": "Bearer ollama"})
            result.update(status=response.status_code, headers=dict(response.headers),
                          body=response.text[:12000])
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
    result["elapsed_s"] = round(time.monotonic() - start, 3)
    return result


def main():
    report = {"at": datetime.now(timezone.utc).isoformat(), "host": HOST,
              "proxy_hosts": {k: urlsplit(v).hostname for k, v in os.environ.items()
                              if k.lower() in ("http_proxy", "https_proxy", "all_proxy")}}
    try:
        report["dns"] = sorted({x[4][0] for x in socket.getaddrinfo(HOST, 443, type=socket.SOCK_STREAM)})
    except OSError as exc:
        report["dns_error"] = str(exc)
    combinations = [(mode, path) for mode in ("environment_proxy", "direct")
                    for path in ("/api/version", "/api/tags", "/v1/models")]
    with ThreadPoolExecutor(max_workers=6) as pool:
        report["probes"] = list(pool.map(lambda p: probe(*p), combinations))
    root = Path(__file__).resolve().parents[1]
    directory = root / "results" / ("connection-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "diagnostics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(directory)


if __name__ == "__main__":
    main()
