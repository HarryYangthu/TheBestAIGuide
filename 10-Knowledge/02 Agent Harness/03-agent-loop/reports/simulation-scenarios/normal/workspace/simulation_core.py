"""Small deterministic signal simulation shared by the component chapters."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import runpy


def mean(values):
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)


def compute(config, mean_fn=mean):
    n, cycles, amplitude, window = (config[k] for k in ("samples", "cycles", "noise_amplitude", "window"))
    if type(n) is not int or not 8 <= n <= 10000:
        raise ValueError("samples must be an integer in [8, 10000]")
    if type(window) is not int or window < 1 or window > n or window % 2 != 1:
        raise ValueError("window must be positive, odd, and no larger than samples")
    if type(cycles) is not int or not 0 < cycles < n / 2:
        raise ValueError("cycles must be a positive integer below samples / 2")
    if type(amplitude) not in (int, float) or not math.isfinite(amplitude) or amplitude <= 0:
        raise ValueError("noise_amplitude must be finite and positive")
    clean = [math.sin(2 * math.pi * cycles * i / n) for i in range(n)]
    noisy = [value + (amplitude if i % 2 == 0 else -amplitude) for i, value in enumerate(clean)]
    radius = window // 2
    filtered = [mean_fn([noisy[(i + j) % n] for j in range(-radius, radius + 1)]) for i in range(n)]
    input_mse = mean([(a - b) ** 2 for a, b in zip(noisy, clean)])
    output_mse = mean([(a - b) ** 2 for a, b in zip(filtered, clean)])
    if not math.isfinite(output_mse) or output_mse <= 0:
        raise ValueError("output MSE must be finite and positive")
    metrics = {"samples": n, "window": window, "input_mse": input_mse,
               "output_mse": output_mse, "improvement_db": 10 * math.log10(input_mse / output_mse),
               "passed": output_mse < input_mse}
    rows = [{"index": i, "clean": a, "noisy": b, "filtered": c}
            for i, (a, b, c) in enumerate(zip(clean, noisy, filtered))]
    return metrics, rows


def run(config_path, output, mean_fn=mean, stats_path=None):
    config_path, output = Path(config_path), Path(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    metrics, rows = compute(config, mean_fn)
    # Only create the output after validating inputs and computing the result.
    output.mkdir(parents=True, exist_ok=False)
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    metrics["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
    metrics["stats_sha256"] = hashlib.sha256(Path(stats_path).read_bytes()).hexdigest() if stats_path else None
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (output / "samples.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["index", "clean", "noisy", "filtered"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# 信号去噪仿真报告", "", f"采样点：{metrics['samples']}；窗口：{metrics['window']}。", "",
             "| 指标 | 实际值 |", "|---|---:|",
             f"| 输入 MSE | {metrics['input_mse']:.6f} |",
             f"| 输出 MSE | {metrics['output_mse']:.6f} |",
             f"| 改善量（dB） | {metrics['improvement_db']:.3f} |", "",
             "结论：" + ("滤波后的 MSE 下降。" if metrics["passed"] else "滤波后的 MSE 未下降。"), "",
             "输入配置：[config.json](config.json)；完整指标：[metrics.json](metrics.json)；波形数据：[samples.csv](samples.csv)。"]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return metrics


def main(script_dir=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("simulation.json"))
    parser.add_argument("--output", type=Path, default=Path("runs/simulation"))
    args = parser.parse_args()
    stats = Path(script_dir or Path.cwd()) / "stats.py"
    mean_fn = runpy.run_path(str(stats))["mean"] if stats.is_file() else mean
    metrics = run(args.config, args.output, mean_fn, stats if stats.is_file() else None)
    print(f"samples={metrics['samples']} window={metrics['window']}")
    print(f"input_mse={metrics['input_mse']:.6f} output_mse={metrics['output_mse']:.6f}")
    print(f"improvement_db={metrics['improvement_db']:.3f} passed={metrics['passed']}")
    print(f"artifacts={args.output.as_posix()}")


if __name__ == "__main__":
    main()
