import argparse
from pathlib import Path
from cycle import read_json, rollback, run_active, run_cycle, write_json


def build_report(out):
    decision = read_json(out / "decision.json")
    result = {"adopted": decision["adopted"], "versions": {}, "gate": decision["checks"],
              "final_active": read_json(out / "active.json")["version"]}
    for label in ("baseline", "candidate"):
        version = decision[label]
        result["versions"][label] = {}
        for split in ("dev", "holdout"):
            rows = [read_json(p) for p in sorted((out / "evaluations" / split / version).glob("*/result.json"))]
            result["versions"][label][split] = {"accepted": sum(r["accepted"] for r in rows), "attempted": len(rows)}
    result["active_after_adopt"] = read_json(out / "after-adopt/result.json")["accepted"]
    result["active_after_rollback"] = read_json(out / "after-rollback/result.json")["accepted"]
    write_json(out / "experiment.json", result)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, label in enumerate(("baseline", "candidate")):
        scores = [result["versions"][label][s]["accepted"] / result["versions"][label][s]["attempted"] for s in ("dev", "holdout")]
        ax.bar([j + i*.35 for j in range(2)], scores, width=.35, label=label)
    ax.set_xticks([.175, 1.175], ["dev (4 tasks x 2)", "holdout (4 tasks x 2)"])
    ax.set(ylim=(0, 1.1), ylabel="Accepted / all attempted runs", title="Frozen candidate, same tasks and call budget")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "comparison.png", dpi=160)
    plt.close(fig)
    lines = ["# 失败驱动的候选与回滚实验", "", "| 版本 | dev | holdout |", "|---|---:|---:|"]
    for label, splits in result["versions"].items():
        lines.append(f"| {label} | {splits['dev']['accepted']}/{splits['dev']['attempted']} | {splits['holdout']['accepted']}/{splits['holdout']['attempted']} |")
    lines += ["", "候选由 dev 失败的受控变更规则生成；生成器不读取 holdout 预期。", "", "![comparison](comparison.png)", "",
              f"采用门禁：{decision['passed']}。采用后实际运行 whitespace：{result['active_after_adopt']}；回滚后再次运行：{result['active_after_rollback']}。", "",
              "最终 active.json 指向基线，history.jsonl 保存 initialize、adopt、rollback。示例回滚是主动演示，不表示发现了线上事故。", "", "所有尝试保留；模型成本未采集，未作成本改善声明。"]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    decision = run_cycle(args.out)
    if not decision["adopted"]:
        raise RuntimeError("candidate did not pass; inspect decision before continuing")
    run_active(args.out, "whitespace", args.out / "after-adopt")
    rollback(args.out, "explicit rollback demonstration")
    run_active(args.out, "whitespace", args.out / "after-rollback")
    result = build_report(args.out)
    for label, split in result["versions"].items():
        print(f"{label}: dev={split['dev']['accepted']}/{split['dev']['attempted']} holdout={split['holdout']['accepted']}/{split['holdout']['attempted']}")
    print(f"adopted={result['adopted']} after_adopt={result['active_after_adopt']} after_rollback={result['active_after_rollback']}")
    print(f"artifacts={args.out}")


if __name__ == "__main__":
    main()
