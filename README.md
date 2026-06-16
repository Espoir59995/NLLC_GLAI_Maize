# NLLC_GLAI_Maize

Data and model files for estimating green maize leaf area index (GLAI) from upward-looking maize LAI observations through phenology-constrained modeling of non-photosynthetic leaf components.

This repository provides a review dataset and model files associated with the manuscript submitted to *Plant Phenomics*. The shared dataset includes a representative subset of 149 maize leaf images collected in 2023, pixel-level training data, trained Random Forest classifiers, and scripts for testing or retraining the leaf component classification models.

## Repository contents

```text
NLLC_GLAI_Maize/
├── README.md
├── data/
│   ├── 2023_leaf_images/
│   │   ├── 2Green/                       # 77 images from KS4 to KS6
│   │   └── 3GreenandYellow/              # 72 images from KS7 to KS10
│   └── training_pixels/
│       ├── 2Green.csv                    # Pixel-level training samples for the green-only classifier
│       └── 3GreenandYellow.csv           # Pixel-level training samples for the green-and-yellow classifier
├── model/
│   ├── 2Green.pkl                        # Trained RF classifier for images before visible yellowing
│   └── 3GreenandYellow.pkl               # Trained RF classifier for images containing green and yellow components
└── scripts/
    ├── train_rf_leaf_component_classifier.py
    └── batch_leaf_component_classification.py
```

## Shared data scope

The shared image dataset contains a representative subset of 149 maize leaf images collected in 2023 at the Jingyuetan Remote Sensing Test Site (JYT). These images are provided for model testing and review purposes.

The 2023 images are divided into two subsets because two Random Forest classifiers were trained and applied for different canopy senescence conditions:

1. **Green-only image subset**: 77 images from KS4 to KS6. These images were collected before obvious yellow non-photosynthetic leaf components appeared and should be processed using the `2Green.pkl` classifier.
2. **Green-and-yellow image subset**: 72 images from KS7 to KS10. These images contain both green photosynthetic and yellow non-photosynthetic leaf components and should be processed using the `3GreenandYellow.pkl` classifier.

Because the field campaign is part of an ongoing research project, the complete multi-year raw image archive, full field sensor records, and complete plot-level datasets are not publicly released at this stage. The shared image subset, pixel-level training data, trained models, and scripts are sufficient for testing and retraining the image-based leaf component classifiers used in the manuscript.

## File naming convention

The image files are named using the following convention:

```text
YYYYKSx_Yp_c_i.jpg
```

where:

- `YYYY` indicates the sampling year.
- `KS` indicates the Jingyuetan field site.
- `x` indicates the sampling campaign number.
- `Yp` indicates the plot ID.
- `c` indicates the image group used during image collection.
- `i` indicates the image sequence number for the same sampled plant or sample set.

For example:

```text
2023KS6_Y9_3_2.jpg
```

indicates an image collected in 2023 at the KS site during campaign KS6, from plot Y9, group 3, image sequence 2.

## Campaign code and image subset

For the shared 2023 dataset, the campaign codes correspond to the following day of year (DOY) and model subset:

| Campaign code | DOY | Image subset | Model used |
|---|---:|---|---|
| KS4 | 202 | 2Green | `2Green.pkl` |
| KS5 | 220 | 2Green | `2Green.pkl` |
| KS6 | 236 | 2Green | `2Green.pkl` |
| KS7 | 243 | 3GreenandYellow | `3GreenandYellow.pkl` |
| KS8 | 250 | 3GreenandYellow | `3GreenandYellow.pkl` |
| KS9 | 263 | 3GreenandYellow | `3GreenandYellow.pkl` |
| KS10 | 269 | 3GreenandYellow | `3GreenandYellow.pkl` |

## Sample plot coordinates

The coordinates are provided in WGS84 geographic coordinates. The `plot_id` values correspond to the plot IDs used in the image filenames.

| plot_id | Longitude | Latitude |
|---|---:|---:|
| Y1 | 125.62105110 | 44.79127969 |
| Y2 | 125.60264441 | 44.80059119 |
| Y3 | 125.59435718 | 44.79624706 |
| Y4 | 125.60265166 | 44.77193898 |
| Y6 | 125.58428826 | 44.77449843 |
| Y7 | 125.57020600 | 44.77140150 |
| Y8 | 125.55786584 | 44.76751443 |
| Y9 | 125.54702958 | 44.76581032 |
| Y12 | 125.59669464 | 44.77871331 |
| Y13 | 125.61537362 | 44.78912811 |
| Y14 | 125.61933853 | 44.79216628 |

## Pixel-level training data

Two pixel-level training CSV files are provided:

```text
data/training_pixels/2Green.csv
data/training_pixels/3GreenandYellow.csv
```

Each training CSV should contain the following columns:

| Column | Description |
|---|---|
| R | Red channel value |
| G | Green channel value |
| B | Blue channel value |
| TYPE | Pixel class label |

### 2Green classifier

The `2Green.csv` file is used to train the green-only classifier. This classifier is applied to KS4 to KS6 images, where the leaves are mainly green and yellow non-photosynthetic components are not expected to be substantial.

Expected class labels for the green-only classifier are:

| Class label | Class name |
|---:|---|
| 1 | White background |
| 2 | Red reference square |
| 3 | Green photosynthetic leaf component |

### 3GreenandYellow classifier

The `3GreenandYellow.csv` file is used to train the green-and-yellow classifier. This classifier is applied to KS7 to KS10 images, where yellow non-photosynthetic leaf components are visible.

Expected class labels for the green-and-yellow classifier are:

| Class label | Class name |
|---:|---|
| 1 | White background |
| 2 | Red reference square |
| 3 | Green photosynthetic leaf component |
| 4 | Yellow non-photosynthetic leaf component |

## Leaf area calculation

The red reference square has a known physical area of 4 cm × 4 cm, or 16 cm². It is used to convert pixel counts into physical leaf area.

For each image, component area can be calculated as:

```text
Component area = component pixel count / red reference pixel count × 16 cm²
```

For the `2Green` subset, the estimated leaf area is based on green photosynthetic pixels. For the `3GreenandYellow` subset, green and yellow component areas are calculated separately and can be used to derive GLAI and YLAI.

## Model files

Two trained Random Forest classifiers are provided:

```text
model/2Green.pkl
model/3GreenandYellow.pkl
```

- `2Green.pkl` is used for images collected from KS4 to KS6.
- `3GreenandYellow.pkl` is used for images collected from KS7 to KS10.

Both model files were saved using `joblib`.

## Python environment

The scripts were prepared for Python 3.8 or later. Install the required packages using:

```bash
pip install opencv-python numpy pandas scikit-learn joblib
```

If a pretrained `.pkl` file cannot be loaded because of local package version differences, retrain the corresponding Random Forest classifier using the provided pixel-level training CSV file.

## Option 1: Test the pretrained classifiers on the shared images

### Green-only subset: KS4 to KS6

Run the batch classification script from the root directory of the repository:

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images/2Green \
  --model model/2Green.pkl \
  --output-dir outputs/2Green_classified_images \
  --output-csv outputs/2Green_pixel_count_results.csv
```

### Green-and-yellow subset: KS7 to KS10

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images/3GreenandYellow \
  --model model/3GreenandYellow.pkl \
  --output-dir outputs/3GreenandYellow_classified_images \
  --output-csv outputs/3GreenandYellow_pixel_count_results.csv
```

If images are organized in nested subfolders, add the `--recursive` option.

The batch script does not overwrite the original images. Classified masks are saved to the output directory, and pixel counts are written to the output CSV file.

## Option 2: Retrain the Random Forest classifiers

### Retrain the green-only classifier

```bash
python scripts/train_rf_leaf_component_classifier.py \
  --training-csv data/training_pixels/2Green.csv \
  --model-out model/2Green_retrained.pkl \
  --metrics-out outputs/2Green_rf_cross_validation_metrics.csv
```

Then apply the retrained model:

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images/2Green \
  --model model/2Green_retrained.pkl \
  --output-dir outputs/2Green_retrained_classified_images \
  --output-csv outputs/2Green_retrained_pixel_count_results.csv
```

### Retrain the green-and-yellow classifier

```bash
python scripts/train_rf_leaf_component_classifier.py \
  --training-csv data/training_pixels/3GreenandYellow.csv \
  --model-out model/3GreenandYellow_retrained.pkl \
  --metrics-out outputs/3GreenandYellow_rf_cross_validation_metrics.csv
```

Then apply the retrained model:

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images/3GreenandYellow \
  --model model/3GreenandYellow_retrained.pkl \
  --output-dir outputs/3GreenandYellow_retrained_classified_images \
  --output-csv outputs/3GreenandYellow_retrained_pixel_count_results.csv
```

## Output columns

The output CSV from the batch classification script includes the following columns:

| Column | Description |
|---|---|
| file_name | Image filename |
| relative_path | Relative path of the image |
| width_px | Image width in pixels |
| height_px | Image height in pixels |
| total_pixels | Total number of pixels in the image |
| background_pixels | Number of pixels classified as white background |
| red_reference_pixels | Number of pixels classified as red reference square |
| green_pixels | Number of pixels classified as green photosynthetic leaf component |
| yellow_pixels | Number of pixels classified as yellow non-photosynthetic leaf component. For the `2Green` subset, this value is expected to be zero or not used. |
| green_area_cm2 | Estimated green leaf area in cm² |
| yellow_area_cm2 | Estimated yellow leaf area in cm². For the `2Green` subset, this value is expected to be zero or not used. |
| total_leaf_area_cm2 | Estimated total leaf area in cm² |
| classified_mask | Path to the saved classified color mask |
| grayscale_mask | Path to the grayscale label mask if saved |

The output CSV from the training script includes five-fold cross-validation metrics, including accuracy, macro precision, macro recall, and macro F1 score.

## Data availability note

A representative subset of 149 maize leaf images collected in 2023, pixel-level training data, trained Random Forest classifiers, and testing scripts are provided in this repository for review and model testing. The images are divided into a green-only subset and a green-and-yellow subset because different classifiers were used before and after the appearance of visible yellow non-photosynthetic leaf components. The complete multi-year raw image archive and full field sensor records are part of an ongoing research project and are not publicly released at this stage. Additional processed data supporting the main results are available from the corresponding author upon reasonable request.

## Contact

For questions about the shared dataset or model files, please contact the corresponding author listed in the manuscript.
