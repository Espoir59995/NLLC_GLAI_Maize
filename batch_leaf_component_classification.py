#!/usr/bin/env python3
"""
Apply a trained Random Forest model to maize leaf images and export pixel counts.

The script loads a trained model, classifies every image in an input directory,
exports class masks, and writes a CSV table containing pixel counts for:

    1 = white background
    2 = red reference square
    3 = green photosynthetic leaf component
    4 = yellow non-photosynthetic leaf component

The red reference square is 4 cm x 4 cm in the manuscript. Therefore, if the
number of red reference pixels is available, the script can also estimate green
and yellow leaf area in cm^2 using the pixel-area conversion.

Example
-------
python scripts/batch_leaf_component_classification.py \
    --input-dir data/2023_leaf_images \
    --model model/3GreenandYellow.pkl \
    --output-dir outputs_example/classified_images \
    --output-csv outputs_example/pixel_count_results.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List

import cv2 as cv
import joblib
import numpy as np
import pandas as pd


CLASS_LABELS: Dict[int, str] = {
    1: "background",
    2: "red_reference_square",
    3: "green_photosynthetic_leaf_component",
    4: "yellow_non_photosynthetic_leaf_component",
}

# OpenCV uses BGR channel order.
MASK_COLORS_BGR: Dict[int, tuple[int, int, int]] = {
    1: (255, 255, 255),  # background: white
    2: (0, 0, 255),      # red reference square: red
    3: (0, 128, 0),      # green leaf component: green
    4: (0, 255, 255),    # yellow leaf component: yellow
}

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Batch classify maize leaf images using a trained Random Forest "
            "leaf component classifier."
        )
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Directory containing input leaf images.",
    )
    parser.add_argument(
        "--model",
        required=True,
        type=Path,
        help="Path to the trained Random Forest model (.pkl).",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("outputs_example/classified_images"),
        type=Path,
        help="Directory for classified mask images.",
    )
    parser.add_argument(
        "--output-csv",
        default=Path("outputs_example/pixel_count_results.csv"),
        type=Path,
        help="Output CSV file for pixel counts and estimated component areas.",
    )
    parser.add_argument(
        "--reference-area-cm2",
        type=float,
        default=16.0,
        help="Physical area of the red reference square in cm^2. Default: 16.0 for 4 cm x 4 cm.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search input images recursively within subdirectories.",
    )
    parser.add_argument(
        "--save-grayscale-mask",
        action="store_true",
        help="Also save grayscale class-label masks with pixel values equal to class labels.",
    )
    return parser.parse_args()


def iter_images(input_dir: Path, recursive: bool = False) -> Iterable[Path]:
    if recursive:
        candidates = input_dir.rglob("*")
    else:
        candidates = input_dir.glob("*")

    for path in sorted(candidates):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def create_color_mask(label_mask: np.ndarray) -> np.ndarray:
    color_mask = np.zeros((*label_mask.shape, 3), dtype=np.uint8)
    for class_id, color in MASK_COLORS_BGR.items():
        color_mask[label_mask == class_id] = color
    return color_mask


def estimate_area(component_pixels: int, red_pixels: int, reference_area_cm2: float) -> float:
    if red_pixels <= 0:
        return float("nan")
    return component_pixels / red_pixels * reference_area_cm2


def classify_image(
    image_path: Path,
    input_dir: Path,
    model,
    output_dir: Path,
    reference_area_cm2: float,
    save_grayscale_mask: bool,
) -> Dict[str, object]:
    img = cv.imread(str(image_path), cv.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"OpenCV could not read image: {image_path}")

    height, width, channels = img.shape
    if channels != 3:
        raise ValueError(f"Expected a 3-channel image, but got shape {img.shape}: {image_path}")

    x = img.reshape(-1, 3)  # OpenCV reads images in B, G, R order.
    pred = model.predict(x)
    label_mask = pred.reshape(height, width).astype(np.uint8)

    relative_path = image_path.relative_to(input_dir)
    safe_stem = "__".join(relative_path.with_suffix("").parts)

    output_dir.mkdir(parents=True, exist_ok=True)
    color_mask = create_color_mask(label_mask)
    color_mask_path = output_dir / f"{safe_stem}_classified.png"
    cv.imwrite(str(color_mask_path), color_mask)

    grayscale_mask_path = ""
    if save_grayscale_mask:
        grayscale_mask_path_obj = output_dir / f"{safe_stem}_labels.png"
        cv.imwrite(str(grayscale_mask_path_obj), label_mask)
        grayscale_mask_path = str(grayscale_mask_path_obj)

    counts = {class_id: int(np.sum(label_mask == class_id)) for class_id in CLASS_LABELS}
    total_pixels = int(height * width)
    red_pixels = counts[2]
    green_pixels = counts[3]
    yellow_pixels = counts[4]

    green_area_cm2 = estimate_area(green_pixels, red_pixels, reference_area_cm2)
    yellow_area_cm2 = estimate_area(yellow_pixels, red_pixels, reference_area_cm2)

    return {
        "file_name": image_path.name,
        "relative_path": str(relative_path).replace("\\", "/"),
        "width_px": width,
        "height_px": height,
        "total_pixels": total_pixels,
        "background_pixels": counts[1],
        "red_reference_pixels": red_pixels,
        "green_pixels": green_pixels,
        "yellow_pixels": yellow_pixels,
        "green_area_cm2": green_area_cm2,
        "yellow_area_cm2": yellow_area_cm2,
        "total_leaf_area_cm2": green_area_cm2 + yellow_area_cm2,
        "classified_mask": str(color_mask_path).replace("\\", "/"),
        "grayscale_mask": grayscale_mask_path.replace("\\", "/") if grayscale_mask_path else "",
    }


def main() -> None:
    args = parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {args.input_dir}")
    if not args.model.exists():
        raise FileNotFoundError(f"Model file not found: {args.model}")

    model = joblib.load(args.model)
    image_paths: List[Path] = list(iter_images(args.input_dir, recursive=args.recursive))
    if not image_paths:
        raise FileNotFoundError(
            f"No supported image files were found in {args.input_dir}. "
            f"Supported extensions: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    rows = []
    failed = []

    for idx, image_path in enumerate(image_paths, start=1):
        print(f"[{idx}/{len(image_paths)}] Processing {image_path.name}")
        try:
            rows.append(
                classify_image(
                    image_path=image_path,
                    input_dir=args.input_dir,
                    model=model,
                    output_dir=args.output_dir,
                    reference_area_cm2=args.reference_area_cm2,
                    save_grayscale_mask=args.save_grayscale_mask,
                )
            )
        except Exception as exc:  # Keep batch processing robust for review testing.
            failed.append({"file_name": image_path.name, "error": str(exc)})
            print(f"  Warning: failed to process {image_path}: {exc}")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output_csv, index=False)

    if failed:
        failed_csv = args.output_csv.with_name(args.output_csv.stem + "_failed.csv")
        pd.DataFrame(failed).to_csv(failed_csv, index=False)
        print(f"Some images failed. Details saved to: {failed_csv}")

    print("Batch classification completed.")
    print(f"Processed images: {len(rows)}")
    print(f"Failed images: {len(failed)}")
    print(f"Pixel count table saved to: {args.output_csv}")
    print(f"Classified masks saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
