from typing import Optional

from torch.utils.data import random_split

from pl_bolts.datasets import CIFAR10Mixed, UnlabeledImagenet
from pl_bolts.transforms.self_supervised import amdim_transforms
from pl_bolts.utils import _TORCHVISION_AVAILABLE
from pl_bolts.utils.stability import under_review
from pl_bolts.utils.warnings import warn_missing_pkg

if _TORCHVISION_AVAILABLE:
    from torchvision.datasets import STL10
else:  # pragma: no cover
    warn_missing_pkg("torchvision")


@under_review()
class AMDIMPretraining:
    """For pretraining we use the train transform for both train and val."""

    @staticmethod
    def cifar10(dataset_root, split: str = "train"):
        assert split in ("train", "val")
        return CIFAR10Mixed(
            root=dataset_root,
            split=split,
            transform=amdim_transforms.AMDIMTrainTransformsCIFAR10(),
            download=True,
        )

    @staticmethod
    def cifar10_tiny(dataset_root, split: str = "train"):
        assert split in ("train", "val")
        return CIFAR10Mixed(
            root=dataset_root,
            split=split,
            transform=amdim_transforms.AMDIMTrainTransformsCIFAR10(),
            download=True,
            num_labeled_per_class=50,
        )

    @staticmethod
    def imagenet(dataset_root, num_classes, split: str = "train"):
        assert split in ("train", "val")
        return UnlabeledImagenet(
            dataset_root,
            num_classes=num_classes,
            split=split,
            transform=amdim_transforms.AMDIMTrainTransformsImageNet128(),
        )

    @staticmethod
    def stl(dataset_root, split: Optional[str] = None):
        if not _TORCHVISION_AVAILABLE:  # pragma: no cover
            raise ModuleNotFoundError(
                "You want to use STL10 dataset loaded from `torchvision` which is not installed yet."
            )
        dataset = STL10(
            root=dataset_root, split="unlabeled", transform=amdim_transforms.AMDIMTrainTransformsSTL10(), download=True
        )
        tng_split, val_split = random_split(dataset, [95000, 5000])
        return tng_split, val_split

    @staticmethod
    def get_dataset(datamodule: str, data_dir, split: str = "train", **kwargs):
        datasets = {
            "tiny-cifar10": AMDIMPretraining.cifar10_tiny,
            "cifar10": AMDIMPretraining.cifar10,
            "stl10": AMDIMPretraining.stl,
            "imagenet2012": AMDIMPretraining.imagenet,
        }
        assert datamodule in datasets, "unrecognized dataset request"
        return datasets[datamodule](dataset_root=data_dir, split=split, **kwargs)


@under_review()
class AMDIMPatchesPretraining:
    """For pretraining we use the train transform for both train and val."""

    @staticmethod
    def cifar10(dataset_root, patch_size, patch_overlap, split: str = "train"):
        assert split in ("train", "val")
        train_transform = amdim_transforms.TransformsC10Patches(patch_size=patch_size, patch_overlap=patch_overlap)
        return CIFAR10Mixed(
            root=dataset_root,
            split=split,
            transform=train_transform,
            download=True,
        )

    @staticmethod
    def stl(dataset_root, patch_size, patch_overlap, split: Optional[str] = None):
        if not _TORCHVISION_AVAILABLE:  # pragma: no cover
            raise ModuleNotFoundError(
                "You want to use STL10 dataset loaded from `torchvision` which is not installed yet."
            )
        train_transform = amdim_transforms.TransformsSTL10Patches(patch_size=patch_size, overlap=patch_overlap)
        dataset = STL10(
            root=dataset_root,
            split="unlabeled",
            transform=train_transform,
            download=True,
        )
        tng_split, val_split = random_split(dataset, [95000, 5000])

        return tng_split, val_split

    @staticmethod
    def imagenet(dataset_root, num_classes, patch_size, patch_overlap, split: str = "train"):
        assert split in ("train", "val")
        train_transform = amdim_transforms.TransformsImageNet128Patches(patch_size=patch_size, overlap=patch_overlap)
        return UnlabeledImagenet(
            dataset_root,
            num_classes=num_classes,
            split=split,
            transform=train_transform,
        )
