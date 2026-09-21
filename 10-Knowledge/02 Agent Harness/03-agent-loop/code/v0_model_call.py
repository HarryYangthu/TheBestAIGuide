"""阶段 0：通过 OpenAI SDK 发起一次真实调用，并保存输入和响应。"""
from artifacts import new_run, print_summary, save_run
from config import load_settings, make_client


def main():
    try:
        settings = load_settings()
        client = make_client(settings)
    except (ValueError, ImportError) as exc:
        raise SystemExit(str(exc) + "\n请先安装 requirements.txt 并配置 .env。")
    directory, workspace = new_run("v0")
    messages = [{"role": "user", "content": "根据以下任务说明，列出仿真命令与验收指标，本次只生成计划。\n" + (workspace / "notes.txt").read_text(encoding="utf-8")}]
    payload = {"model": settings.model, "messages": messages.copy()}
    record = {"request": payload}
    try:
        response = client.chat.completions.create(
            model=settings.model, messages=messages,
        )
        record["response"] = response.model_dump(mode="json")
        text = response.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": text, "tool_calls": []})
        print(text)
        status, reason = "stopped", "response_received"
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__}
        status, reason = "failed", type(exc).__name__
    result = {"stage": "v0", "execution_mode": "live_api", "model": settings.model,
              "status": status, "reason": reason, "model_calls": 1,
              "messages": messages, "trace": []}
    save_run(directory, result, [record], (workspace / "stats.py").read_text(encoding="utf-8"))
    print_summary(directory, result)
    if status == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
