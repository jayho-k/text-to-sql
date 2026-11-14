"""실제 ChatOpenAI 호출과 관측 기록. 대역 모델/자동 재시도 없음."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import time
from typing import Callable

from langchain_openai import ChatOpenAI


@dataclass(frozen=True)
class ModelSettings:
    base_url: str = "https://jayho-macmini.tail60408a.ts.net/v1"
    model: str = "gemma4:26b-a4b-it-qat"
    temperature: float = 0.1
    max_tokens: int = 2028
    reasoning_effort: str = "none"
    timeout: float = 120
    max_retries: int = 0


class ModelClient:
    def __init__(self, settings=None, sink: Callable | None = None):
        self.settings = settings or ModelSettings()
        self.calls = []
        self.sink = sink
        self.llm = ChatOpenAI(api_key="ollama", **asdict(self.settings))

    def ask(self, role: str, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        record = {"index": len(self.calls), "role": role, "messages": messages,
                  "started_at": datetime.now(timezone.utc).isoformat(),
                  "usage": None, "response": None, "error": None}
        start = time.monotonic()
        try:
            response = self.llm.invoke(messages)
            record["response"] = response.model_dump(mode="json")
            record["usage"] = response.usage_metadata
            if response.response_metadata.get("finish_reason") == "length":
                raise ValueError("output_truncated: max_tokens reached")
            if not isinstance(response.content, str) or not response.content.strip():
                raise ValueError("empty_or_non_text_response")
            return response.content
        except Exception as exc:
            record["error"] = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            record["elapsed_s"] = round(time.monotonic() - start, 6)
            self.calls.append(record)
            if self.sink:
                self.sink(record)
