"""Read a task, validate its data, produce a result, and independently accept it."""
from __future__ import annotations
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class ContractError(Exception):
    def __init__(self, code, stage, detail, retryable=False):
        super().__init__(detail)
        self.record = dict(code=code, stage=stage, detail=detail, retryable=retryable)


def reject_constant(value):
    raise ValueError(f"JSON 不接受非有限数值：{value}")


def load_json(path, stage):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          parse_constant=reject_constant)
    except FileNotFoundError as exc:
        raise ContractError("input_missing", stage, f"文件不存在：{Path(path).name}") from exc
    except (ValueError, UnicodeDecodeError) as exc:
        raise ContractError("invalid_json", stage, "文件不是有效的 UTF-8 JSON") from exc
    except OSError as exc:
        raise ContractError("io_error", stage, type(exc).__name__) from exc


def validate(value, schema_name, stage):
    schema = load_json(ROOT / "schemas" / f"{schema_name}.schema.json", "schema")
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        path = "/" + "/".join(map(str, error.path))
        raise ContractError(f"{stage}_schema", stage, f"{path}: {error.message}")


def prepare(task_path):
    task_path = Path(task_path).resolve()
    task = load_json(task_path, "task")
    validate(task, "task", "task")
    source = (task_path.parent / task["input_path"]).resolve()
    if not source.is_relative_to(task_path.parent):
        raise ContractError("constraint_violation", "input", "input_path 必须位于任务文件目录内")
    tickets = load_json(source, "input")
    validate(tickets, "tickets", "input")
    ids = [row["id"] for row in tickets]
    if len(ids) != len(set(ids)):
        raise ContractError("invalid_input", "input", "工单 id 必须唯一")
    if len(tickets) > task["constraints"]["max_rows"]:
        raise ContractError("constraint_violation", "input", "输入行数超过 max_rows")
    return task, source, tickets


def rounded(value, digits):
    return float(value.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def calculate(task, source, tickets, run_id):
    completed = [row for row in tickets if row["status"] == task["constraints"]["included_status"]]
    if not completed:
        raise ContractError("empty_selection", "execute", "没有已完成工单，平均工时没有定义")
    total = sum((Decimal(str(row["hours"])) for row in completed), Decimal(0))
    digits = task["acceptance"]["decimal_places"]
    return dict(task_id=task["task_id"], task_version=task["version"], run_id=run_id,
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                completed_ids=sorted(row["id"] for row in completed), count=len(completed),
                total_hours=rounded(total, digits), mean_hours=rounded(total / len(completed), digits))


def accept(task, source, tickets, output, run_id):
    """Validate the saved output and recompute expected facts without calling calculate."""
    validate(output, "result", "output")
    selected = {row["id"]: Decimal(str(row["hours"])) for row in tickets
                if row["status"] == task["constraints"]["included_status"]}
    total = sum(selected.values(), Decimal(0))
    digits = task["acceptance"]["decimal_places"]
    checks = {
        "task_identity": output["task_id"] == task["task_id"] and output["task_version"] == task["version"],
        "run_identity": output["run_id"] == run_id,
        "source_digest": output["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest(),
        "exact_ids": output["completed_ids"] == sorted(selected),
        "count": output["count"] == len(selected),
        "minimum_done": len(selected) >= task["acceptance"]["min_done"],
        "total_hours": Decimal(str(output["total_hours"])) == Decimal(str(rounded(total, digits))),
        "mean_hours": bool(selected) and Decimal(str(output["mean_hours"])) == Decimal(str(rounded(total / len(selected), digits))),
    }
    return {"passed": all(checks.values()), "checks": checks}


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def execute(task_path, output_dir, mutate=None):
    """mutate is an explicit fault-injection hook, used only by the local experiment."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    run_id = "run-" + uuid4().hex
    record = dict(run_id=run_id, task_id=None, task_version=None, attempt=1,
                  status="failed", acceptance=None, error=None)
    try:
        task, source, tickets = prepare(task_path)
        record.update(task_id=task["task_id"], task_version=task["version"])
        write_json(output_dir / "task.json", task)
        (output_dir / "tickets.json").write_bytes(source.read_bytes())
        # Compute and accept against the frozen input, not a file another process can change.
        frozen_source = output_dir / "tickets.json"
        frozen_tickets = load_json(frozen_source, "input")
        output = calculate(task, frozen_source, frozen_tickets, run_id)
        if mutate is not None:
            mutate(output)
        write_json(output_dir / "result.json", output)
        saved_output = load_json(output_dir / "result.json", "output")
        acceptance = accept(task, frozen_source, frozen_tickets, saved_output, run_id)
        record["acceptance"] = acceptance
        if not acceptance["passed"]:
            failed = [key for key, passed in acceptance["checks"].items() if not passed]
            raise ContractError("acceptance_failed", "accept", ", ".join(failed))
        record["status"] = "accepted"
    except ContractError as exc:
        record["error"] = exc.record
    write_json(output_dir / "run.json", record)
    return record
