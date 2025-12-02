#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计给定根目录下，每个任务子文件夹中 image_inputs 目录里的图片数量，
并计算平均图片数量。

目录结构示例：
fold1/
  ├─ task_1/
  │   └─ image_inputs/
  │       ├─ xxx.jpg
  │       └─ yyy.jpg
  ├─ task_2/
  │   └─ image_inputs/
  │       ├─ a.jpg
  │       └─ b.jpg
  └─ ...

用法：
    python stat_avg_images.py /path/to/fold1
如果不传参数，默认使用当前目录下的 "fold1"。
"""

import os
import sys

def count_images_in_task(task_dir: str) -> int:
    """
    统计单个任务目录中 image_inputs 下的 jpg 图片数量。
    """
    image_dir = os.path.join(task_dir, "image_inputs")
    if not os.path.isdir(image_dir):
        return 0

    count = 0
    for name in os.listdir(image_dir):
        if name.lower().endswith((".jpg", ".jpeg")):
            count += 1
    return count


def main(root_dir: str):
    if not os.path.isdir(root_dir):
        print(f"根目录不存在或不是目录: {root_dir}")
        return

    total_tasks = 0
    total_images = 0

    for name in os.listdir(root_dir):
        task_path = os.path.join(root_dir, name)
        if not os.path.isdir(task_path):
            continue

        total_tasks += 1
        img_count = count_images_in_task(task_path)
        total_images += img_count

        print(f"任务目录: {name}, 图片数量: {img_count}")

    if total_tasks == 0:
        print("没有找到任何任务子目录。")
        return

    avg_images = total_images / total_tasks
    print("-" * 40)
    print(f"任务总数: {total_tasks}")
    print(f"图片总数: {total_images}")
    print(f"每个任务子文件夹的平均图片数量: {avg_images:.2f}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = "fold1"

    main(root)
