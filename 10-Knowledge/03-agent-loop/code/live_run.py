"""v1—v4 的真实 API 运行入口；核心循环保留在各版本文件中。"""
import argparse
import importlib
from artifacts import new_run, print_summary, save_run
from openai_model import OpenAIModel
from shared import check_tests

MODULES = {"v1": "v1_minimal_loop", "v2": "v2_tool_dispatch",
           "v3": "v3_controlled_loop", "v4": "v4_resilient_loop"}


def run_stage(stage, max_steps=12, manual=False):
    model = OpenAIModel.from_env()
    if max_steps < 1:
        raise ValueError("max_steps 必须至少为 1。")
    if manual:
        model.call_options = [
            {"tool_choice": {"type": "function", "function": {"name": "read_file"}}, "parallel_tool_calls": False},
            {"tool_choice": "none"},
        ]
    directory, workspace = new_run(stage + ("-manual" if manual else ""))
    before = (workspace / "stats.py").read_text(encoding="utf-8")
    module = importlib.import_module(MODULES[stage])
    try:
        if manual:
            messages = module.run_manual(model, workspace)
            result = {"status": "stopped", "reason": "manual_two_calls", "messages": messages, "trace": []}
        elif stage == "v1":
            messages = module.run_loop(model, workspace, max_steps=max_steps)
            result = {"status": "stopped", "reason": "no_tool_calls", "messages": messages, "trace": []}
        else:
            result = module.run_loop(model, workspace, max_steps=max_steps)
    except Exception as exc:
        # 保留失败请求；不把认证信息写入结果文件。
        result = {"status": "failed", "reason": type(exc).__name__, "messages": [],
                  "trace": [{"event": "run_error", "error_type": type(exc).__name__}]}
    result.update(stage=stage, execution_mode="live_api", model=model.model_name, model_calls=len(model.records))
    if stage != "v1":
        result["acceptance"] = check_tests(workspace)
    save_run(directory, result, model.records, before)
    print_summary(directory, result)
    return result, directory


def cli(stage):
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-steps", type=int, default=12)
    if stage == "v1":
        parser.add_argument("--manual", action="store_true")
    args = parser.parse_args()
    try:
        result, _ = run_stage(stage, args.max_steps, getattr(args, "manual", False))
    except (ValueError, ImportError) as exc:
        parser.exit(2, str(exc) + "\n请先安装 requirements.txt 并配置 .env。\n")
    if result["status"] == "failed":
        raise SystemExit(1)
