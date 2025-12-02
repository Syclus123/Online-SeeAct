#!/usr/bin/env python3
"""
检查指定目录下的每个子目录是否包含以下内容：
- result.json 文件
- trajectory 子文件夹

默认检查项目根目录下的 desc_rag。
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="统计缺失 result.json 的任务（子目录）"
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parent / "desc_rag"),
        help="需要检查的目录（默认: 项目根目录下的 desc_rag）",
    )
    return parser.parse_args()


def collect_missing_result_json(target_dir: Path) -> list[str]:
    if not target_dir.exists():
        raise FileNotFoundError(f"目录不存在: {target_dir}")
    if not target_dir.is_dir():
        raise NotADirectoryError(f"路径不是目录: {target_dir}")

    missing = []
    for sub_dir in sorted(target_dir.iterdir()):
        if not sub_dir.is_dir():
            continue
        if not (sub_dir / "result.json").is_file():
            missing.append(sub_dir.name)
    return missing


def collect_missing_trajectory_dir(target_dir: Path) -> list[str]:
    if not target_dir.exists():
        raise FileNotFoundError(f"目录不存在: {target_dir}")
    if not target_dir.is_dir():
        raise NotADirectoryError(f"路径不是目录: {target_dir}")

    missing = []
    for sub_dir in sorted(target_dir.iterdir()):
        if not sub_dir.is_dir():
            continue
        if not (sub_dir / "trajectory").is_dir():
            missing.append(sub_dir.name)
    return missing


def main() -> None:
    args = parse_args()
    target_dir = Path(args.target_dir).expanduser().resolve()

    try:
        missing_result = collect_missing_result_json(target_dir)
        missing_trajectory = collect_missing_trajectory_dir(target_dir)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"错误: {exc}")
        return

    subfolders = [p.name for p in target_dir.iterdir() if p.is_dir()]

    print("=" * 60)
    print(f"检查目录: {target_dir}")
    print(f"子目录总数: {len(subfolders)}")
    print(f"缺失 result.json 的任务数量: {len(missing_result)}")
    print(f"缺失 trajectory 的任务数量: {len(missing_trajectory)}")
    print("=" * 60)

    if missing_result:
        print("缺失 result.json 的任务 ID：")
        for idx, task_id in enumerate(missing_result, 1):
            print(f"{idx:3d}. {task_id}")
    if missing_trajectory:
        print("缺失 trajectory 的任务 ID：")
        for idx, task_id in enumerate(missing_trajectory, 1):
            print(f"{idx:3d}. {task_id}")
    if not missing_result and not missing_trajectory:
        print("✓ 所有任务都包含 result.json 且包含 trajectory")


if __name__ == "__main__":
    main()

