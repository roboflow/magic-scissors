![Magic Scissors](/assets/magic-scissors.jpg)

# Magic Scissors
Generate synthetic data for computer vision using copy/paste context-augmentation.

Try it: https://magicscissors.app

## Background
Collecting and annotating training to create performant computer
vision models is hard time-consuming work. Often, the most valuable
data to collect is of the most rare edge-cases. It is impractical and,
in some cases, impossible to wait for that data to present itself
naturally.

Creating synthetic data to augment your real-world data can be
extremely helpful in creating a robust dataset.

## Context-Augmentation
There are several ways to expand your dataset (for example,
traditional data augmentation and creating 3D-rendered scenes).
Context-augmentation is a simpler method which cuts objects of
interest from one scene and pastes them into another.

## How to Use Magic Scissors
Magic Scissors operates on [Roboflow](https://roboflow.com) datasets
using the [Roboflow API](https://docs.roboflow.com/rest-api). You'll
need [an API Key](https://docs.roboflow.com/rest-api#obtaining-your-api-key)
and three datasets in your Roboflow account:

1. `Objects of Interest` -- this should be an object detection or instance
segmentation dataset with the objects that should be cut out
[annotated with polygons](https://docs.roboflow.com/annotate/the-labeling-interface#smart-polygons).
2. `Backgrounds` -- this should be an object detection or instance
segmentation dataset with the backgrounds that objects will be pasted over.
Drop-zones should be annotated with polygons.
3. `Destination` -- this is where the new images will be stored. It should
be an object detection or instance segmentation project (and may, optionally,
be the same as your `Objects of Interest` dataset.

## Settings
There are several settings available in Magic Scissors to customize your
output:

- `Dataset Size` - the number of synthetic images to create.
- `Objects Per Image` - how many objects to place on the background in
each synthetic image (range of min to max).
- `Object Size Variance` - the amount to grow or shrink objects of interest.
This simulates objects being closer or farther away from the camera and
can be used to adjust realism if the scale of the images in
`Objects of Interest` and `Backgrounds` is not the same.

## Applying Augmentations
It can be additionally useful to vary the color, brightness, contrast,
rotation, etc of your objects of interest. You can choose these settings
on the `Objects of Interest` dataset in the Roboflow interface and Magic
Scissors will use them when isolating and exporting the objects.

## Example Outputs
Example projects will be listed below. If you create a public project
on [Roboflow Universe](https://universe.roboflow.com) with Magic Scissors,
submit a PR to add it to this list.