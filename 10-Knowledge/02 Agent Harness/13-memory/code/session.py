"""Each invocation is a new process sharing an on-disk SQLite file."""
import argparse

from memory import ROOT, MemoryStore, load_fixture, render_context, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["learn", "review", "conflict", "update", "expire", "forget"])
    parser.add_argument("--db", default="runs/manual/memory.sqlite3")
    parser.add_argument("--out", default="runs/manual")
    parser.add_argument("--task", default="task-second.json")
    parser.add_argument("--as-of", default="2026-10-02")
    parser.add_argument("--id", default="pref-language")
    args = parser.parse_args()
    store = MemoryStore(ROOT / args.db)
    output = ROOT / args.out
    try:
        sources = load_fixture("evidence.json")
        if args.action == "learn":
            statuses = {r["id"]: store.add(r, sources) for r in load_fixture("records.json")}
            save_json(output / "learn.json", statuses)
            print(f"stored={len(statuses)} active={sum(s == 'active' for s in statuses.values())}")
        elif args.action in {"conflict", "update"}:
            record = load_fixture(args.action + ".json")
            print("status=" + store.add(record, sources))
        elif args.action == "expire":
            print("expired=" + str(len(store.expire(args.as_of))))
        elif args.action == "forget":
            store.forget(args.id)
            print("forgot=" + args.id)
        else:
            task = load_fixture(args.task)
            result = store.retrieve(task, sources)
            save_json(output / "result.json", result)
            save_json(output / "context.json", render_context(result))
            english = result["effective_preferences"].get("language") == "en"
            report = "# stats release checklist\n\n" if english else "# stats 下次发布\n\n"
            report += ("| Memory | Kind | Value used in this review | Source |\n" if english else
                       "| 记忆 | 类型 | 本次采用的值 | 来源 |\n") + "|---|---|---|---|\n"
            report += "\n".join(f"| {r['id']} | {r['kind']} | {r['value']} | {r['source_id']} |" for r in result["selected"])
            report += ("\n\n| Excluded memory | Reason |\n" if english else
                       "\n\n| 未采用记忆 | 原因 |\n") + "|---|---|\n"
            report += "\n".join(f"| {r['id']} | {r['reason']} |" for r in result["excluded"])
            (output / "report.md").write_text(report + "\n", encoding="utf-8")
            print("selected=" + ",".join(r["id"] for r in result["selected"]))
            print("language=" + result["effective_preferences"].get("language", "unspecified"))
        save_json(output / "store-snapshot.json", store.rows())
    finally:
        store.close()


if __name__ == "__main__":
    main()
