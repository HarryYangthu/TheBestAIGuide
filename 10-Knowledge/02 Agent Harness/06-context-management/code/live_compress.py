"""Real SDK compression candidate, validated before it can replace history."""
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from openai import OpenAI

from context import ROOT, dumps, read_fixture, save_json, validate_summary


def compress(client, model, history):
    request = {
        "model": model,
        "messages": [
            {"role": "system", "content": "将事件压缩为 JSON 对象，仅含 facts 数组；每项只含 key、value、event_id。只收录输入中带 fact 的事件，保留每个 key 的最新值及对应事件 id，不补充事实。"},
            {"role": "user", "content": dumps(history)},
        ],
        "response_format": {"type": "json_object"},
    }
    response = client.chat.completions.create(**request)
    return request, response


def main():
    import json
    load_dotenv(ROOT / ".env")
    names = ("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL")
    missing = [name for name in names if not os.getenv(name) or os.getenv(name, "").startswith("your-")]
    if missing:
        raise SystemExit("缺少真实模型配置：" + ", ".join(missing))
    history = read_fixture("history.json")
    client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"],
                    timeout=30, max_retries=0)
    request, response = compress(client, os.environ["OPENAI_MODEL"], history)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "runs" / ("live-" + stamp)
    output.mkdir(parents=True, exist_ok=False)
    save_json(output / "request.json", request)
    save_json(output / "response.json", response.model_dump())
    try:
        candidate = json.loads(response.choices[0].message.content or "")
    except (ValueError, IndexError):
        candidate = None
    verdict = validate_summary(candidate, history)
    save_json(output / "validation.json", verdict)
    save_json(output / "effective-context.json", candidate if verdict["accepted"] else history)
    print("accepted=" + str(verdict["accepted"]))
    print("effective_context=" + ("summary" if verdict["accepted"] else "original_history"))
    print("artifacts=" + str(output.relative_to(ROOT)))


if __name__ == "__main__":
    main()
