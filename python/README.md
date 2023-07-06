![Magic Scissors banner](https://github.com/roboflow/magic-scissors/raw/main/assets/magic-scissors.jpg)

# Magic Scissors ✂️

[![version](https://badge.fury.io/py/magicscissors.svg?)](https://badge.fury.io/py/magicscissors)
[![downloads](https://img.shields.io/pypi/dm/magicscissors)](https://pypistats.org/packages/magicscissors)
[![license](https://img.shields.io/pypi/l/magicscissors?)](https://github.com/roboflow/magicscissors-python/blob/main/LICENSE)
[![python-version](https://img.shields.io/pypi/pyversions/magicscissors)](https://badge.fury.io/py/magicscissors)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)]()

Generate synthetic data for computer vision using copy-paste context augmentation.

Magic Scissors is available as a Python package and a [web application](https://magicscissors.app).

## Installation

To install Magic Scissors, run the following command:

```bash
pip install magicscissors
```

## Quickstart 🚀

To use Magic Scissors, you need two datasets:

1. A dataset with object of interest;
2. A dataset with backgrounds on which objects of interest can be pasted.

Both datasets should be formatted as COCO JSON. You can [convert data between formats](https://roboflow.com/formats) using Roboflow.

```python
from magic_scissors import MagicScissors

data = MagicScissors(
    dataset_size=100,
    min_objects_per_image=1,
    max_objects_per_image=3,
    min_size_variance=2,
    max_size_variance=5,
    annotate_occlusion=0,
    working_dir="./",
    upload_to_roboflow=False,
    roboflow_api_key="",
    roboflow_workspace="",
    roboflow_project="",
)

# load data from COCO JSON files
data.load_backgrounds_from_coco()
data.load_objects_of_interest_from_coco()

# load data from Roboflow
data.download_objects_of_interest_from_roboflow(
    dataset_url=""
)
data.download_backgrounds_from_roboflow(
    dataset_url=""
)

# generate dataset and save to directory
data.generate_dataset()
```

## Contributing 🏆

We would love your help improving Magic Scissors! Please see our [contributing guide](https://github.com/roboflow/magic-scissors/blob/main/CONTRIBUTING.md) to get started. Thank you 🙏 to all our contributors!

## License

This project is licensed under an MIT license.