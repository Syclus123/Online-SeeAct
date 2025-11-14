#!/usr/bin/env python3
"""
reformat_dataset.py

Usage:
    python reformat_dataset.py /path/to/dataset_origin
    python reformat_dataset.py /path/to/dataset_origin --move
    python reformat_dataset.py /path/to/dataset_origin --dry-run

功能：
- 遍历 dataset_root 下的每个 task_id 文件夹
- 如果发现 image_inputs 子文件夹，将其中图片按数字前缀排序并复制/移动到 trajectory 子文件夹
- 重命名为 step_{i}_screenshot.<ext>
- 保留 task_id.log 和 result.json 不动
"""
import argparse
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}

NUM_PREFIX_RE = re.compile(r'^(\d+)')


def extract_sort_key(name: str) -> Tuple[int, str]:
    """
    尝试从文件名提取开头数字作为主排序关键字。
    返回 (prefix_int_or_large, basename) 以便稳定排序。
    """
    m = NUM_PREFIX_RE.match(name)
    if m:
        return (int(m.group(1)), name)
    # 如果没有数字前缀，放到后面（使用大数保证排在数字之后），再按名字排序
    return (10**9, name)


def gather_image_files(folder: Path) -> List[Path]:
    files = []
    for p in folder.iterdir():
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            files.append(p)
    # sort by extracted numeric prefix then by name
    files.sort(key=lambda p: extract_sort_key(p.name))
    return files


def process_task(task_folder: Path, move_files: bool, dry_run: bool):
    image_inputs = task_folder / 'image_inputs'
    if not image_inputs.exists() or not image_inputs.is_dir():
        print(f"  [skip] no image_inputs in {task_folder.name}")
        return

    trajectory = task_folder / 'trajectory'
    if not dry_run:
        trajectory.mkdir(exist_ok=True)

    images = gather_image_files(image_inputs)
    if not images:
        print(f"  [skip] image_inputs exists but no images found in {task_folder.name}")
        return

    print(f"  processing {task_folder.name}: {len(images)} image(s) -> trajectory/")
    for i, img_path in enumerate(images):
        ext = img_path.suffix.lower()
        new_name = f"step_{i}_screenshot{ext}"
        dest = trajectory / new_name

        if dry_run:
            action = "move" if move_files else "copy"
            print(f"    [dry-run] {action} {img_path.name} -> {trajectory.name}/{new_name}")
        else:
            # 如果目标已存在，先备份/覆盖（这里直接覆盖）
            if move_files:
                # use shutil.move
                try:
                    shutil.move(str(img_path), str(dest))
                except Exception as e:
                    print(f"    [error] moving {img_path} -> {dest}: {e}")
            else:
                try:
                    shutil.copy2(str(img_path), str(dest))
                except Exception as e:
                    print(f"    [error] copying {img_path} -> {dest}: {e}")

    # 可选：如果用户选择复制且想要保留 image_inputs，可不做任何事。
    # 如果选择移动且 image_inputs 为空，可以删除空目录（不强制）
    if not dry_run and move_files:
        # 如果 image_inputs 为空，则尝试删除（安全起见，只在空时删除）
        try:
            if not any(image_inputs.iterdir()):
                image_inputs.rmdir()
                print(f"    removed empty folder {image_inputs}")
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Reformat dataset: move/copy images from image_inputs -> trajectory")
    parser.add_argument("dataset_root", type=str, help="Root folder containing task_id subfolders (e.g. dataset_origin)")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying (default: copy)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without changing files")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    root = Path(args.dataset_root)
    if not root.exists() or not root.is_dir():
        print("dataset_root not found or not a directory:", root)
        return

    task_dirs = [p for p in root.iterdir() if p.is_dir()]
    if not task_dirs:
        print("No task folders found under", root)
        return

    print(f"Found {len(task_dirs)} task folder(s) under {root}")
    for task in sorted(task_dirs):
        # skip hidden dirs
        if task.name.startswith('.'):
            continue
        # Ensure we don't accidentally process top-level files like logs
        print(f"Processing task folder: {task.name}")
        process_task(task, move_files=args.move, dry_run=args.dry_run)

    print("Done.")


if __name__ == "__main__":
    main()

# python dataset_utils.py /home/ubuntu/csb/SeeAct/online_results/baseline_1113_15