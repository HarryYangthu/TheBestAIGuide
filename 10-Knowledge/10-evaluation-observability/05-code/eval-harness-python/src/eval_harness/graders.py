"""确定性字段检查。禁止词仅用于教学反例，不能证明不存在语义泄漏。"""
import json


def matches(actual, expected) -> bool:
    """字典按给定字段递归包含；数组顺序/长度固定；标量类型与值均须一致。"""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(key in actual and matches(actual[key], val)
                                               for key,val in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            matches(a,b) for a,b in zip(actual,expected))
    return type(actual) is type(expected) and actual == expected


def grade(expected: dict, output: dict, state: dict) -> dict[str, bool]:
    checks = {}
    if expected.get("output"):
        for key, value in expected["output"].items():
            checks[f"output:{key}"] = key in output and matches(output[key], value)
    if expected.get("state"):
        for key,value in expected["state"].items():
            checks[f"state:{key}"] = key in state and matches(state[key],value)
    serialized = json.dumps(output, ensure_ascii=False, sort_keys=True)
    for i, forbidden in enumerate(expected.get("forbidden_strings", [])):
        checks[f"forbidden:{i}"] = forbidden not in serialized
    return checks
