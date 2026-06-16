# NLLC_GLAI_Maize

Data and model files for estimating green maize leaf area index (GLAI) from upward-looking maize LAI observations through phenology-constrained modeling of non-photosynthetic leaf components.

This repository provides a review dataset and model files associated with the manuscript submitted to *Plant Phenomics*. It includes a representative subset of maize leaf images collected in 2023, pixel-level training data for leaf component classification, a trained Random Forest classifier, and scripts for testing or retraining the model.

## Repository contents

```text
NLLC_GLAI_Maize/
├── README.md
├── data/
│   ├── 2023_leaf_images/                 # Representative subset of 149 maize leaf images from 2023
│   └── training_pixels/
│       └── 3GreenandYellow.csv           # Pixel-level training samples for RF classification
├── model/
│   └── 3GreenandYellow.pkl               # Trained Random Forest leaf component classifier
└── scripts/
    ├── train_rf_leaf_component_classifier.py
    └── batch_leaf_component_classification.py
```

## Shared data scope

The shared image dataset contains a representative subset of 149 maize leaf images collected in 2023 at the Jingyuetan Remote Sensing Test Site (JYT). These images are provided for model testing and review purposes.

The shared training dataset `data/training_pixels/3GreenandYellow.csv` contains pixel-level samples used for Random Forest leaf component classification. The file includes 800 labelled pixels, with 200 samples for each class.

Because the field campaign is part of an ongoing research project, the complete multi-year raw image archive, full field sensor records, and complete plot-level datasets are not publicly released at this stage. The shared images, pixel-level training data, trained model, and scripts are sufficient for testing and retraining the image-based leaf component classifier described in the manuscript.

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

## Campaign code and day of year

For the shared 2023 dataset, the campaign codes correspond to the following day of year (DOY):

| Campaign code | DOY |
|---|---:|
| KS4 | 202 |
| KS5 | 220 |
| KS6 | 236 |
| KS7 | 243 |
| KS8 | 250 |
| KS9 | 263 |
| KS10 | 269 |

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

The training file is provided as:

```text
data/training_pixels/3GreenandYellow.csv
```

The file contains the following columns:

| Column | Description |
|---|---|
| R | Red channel value |
| G | Green channel value |
| B | Blue channel value |
| TYPE | Pixel class label |

The class labels are:

| Class label | Class name | Number of training pixels |
|---:|---|---:|
| 1 | White background | 200 |
| 2 | Red reference square | 200 |
| 3 | Green photosynthetic leaf component | 200 |
| 4 | Yellow non-photosynthetic leaf component | 200 |

## Leaf component classes

The trained Random Forest model classifies each image pixel into one of four classes:

| Class label | Class name |
|---:|---|
| 1 | White background |
| 2 | Red reference square |
| 3 | Green photosynthetic leaf component |
| 4 | Yellow non-photosynthetic leaf component |

The red reference square has a known physical area of 4 cm × 4 cm, or 16 cm². It is used to convert pixel counts into physical leaf area.

For each image, the component area can be calculated as:

```text
Component area = component pixel count / red reference pixel count × 16 cm²
```

## Model file

The trained classifier is provided as:

```text
model/3GreenandYellow.pkl
```

This file is a trained Random Forest classifier saved using `joblib`. It is used by the batch classification script to classify the shared maize leaf images.

## Python environment

The scripts were prepared for Python 3.8 or later. Install the required packages using:

```bash
pip install opencv-python numpy pandas scikit-learn joblib
```

If the pretrained `.pkl` file cannot be loaded because of local package version differences, retrain the Random Forest classifier using the provided pixel-level training CSV file.

## Option 1: Test the pretrained model on the shared images

Run the batch classification script from the root directory of the repository:

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images \
  --model model/3GreenandYellow.pkl \
  --output-dir outputs/classified_images \
  --output-csv outputs/pixel_count_results.csv
```

If the images are organized in subfolders, add the `--recursive` option:

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images \
  --model model/3GreenandYellow.pkl \
  --output-dir outputs/classified_images \
  --output-csv outputs/pixel_count_results.csv \
  --recursive
```

The script does not overwrite the original images. Classified masks are saved to the output directory, and pixel counts are written to the output CSV file.

## Option 2: Retrain the Random Forest classifier

The training script can be used to retrain the Random Forest classifier using the shared pixel-level training data:

```bash
python scripts/train_rf_leaf_component_classifier.py \
  --training-csv data/training_pixels/3GreenandYellow.csv \
  --model-out model/3GreenandYellow_retrained.pkl \
  --metrics-out outputs/rf_cross_validation_metrics.csv
```

The script performs five-fold cross-validation and saves the retrained model. The retrained model can then be used for batch classification:

```bash
python scripts/batch_leaf_component_classification.py \
  --input-dir data/2023_leaf_images \
  --model model/3GreenandYellow_retrained.pkl \
  --output-dir outputs/classified_images_retrained \
  --output-csv outputs/pixel_count_results_retrained.csv
```

## Output columns

The output CSV from the batch classification script includes the following columns:

| Column | Description |
|---|---|
| filename | Image filename |
| background_pixels | Number of pixels classified as white background |
| red_pixels | Number of pixels classified as red reference square |
| green_pixels | Number of pixels classified as green photosynthetic leaf component |
| yellow_pixels | Number of pixels classified as yellow non-photosynthetic leaf component |
| total_pixels | Total number of pixels in the image |
| green_area_cm2 | Estimated green leaf area in cm² |
| yellow_area_cm2 | Estimated yellow leaf area in cm² |
| total_leaf_area_cm2 | Estimated total leaf area in cm² |

The output CSV from the training script includes five-fold cross-validation metrics, including accuracy, macro precision, and macro recall.

## Data availability note

A representative subset of 149 maize leaf images collected in 2023, the pixel-level training data, the trained Random Forest classifier, and testing scripts are provided in this repository for review and model testing. The complete multi-year raw image archive and full field sensor records are part of an ongoing research project and are not publicly released at this stage. Additional processed data supporting the main results are available from the corresponding author upon reasonable request.

## Contact

For questions about the shared dataset or model files, please contact the corresponding author listed in the manuscript.
