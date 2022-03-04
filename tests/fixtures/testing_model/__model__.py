from typing import Any, List
import os
from koi_core.resources.instance import Instance


def set_asset_dir(dir: str):
    f = open(os.path.join(dir, "additional_files", "sample.txt"), "r")
    print(f.read())
    f.close()


def batch_generator(instance: Instance) -> List[Any]:
    return ["batch0", "batch1"]


def initialize_training() -> None:
    ...


def train(batch: List[Any]) -> None:
    ...


def infer(batch: List[Any], result: List[Any]) -> None:
    ...


def should_create_training_data() -> bool:
    ...


def save_training_data() -> bytes:
    ...


def load_training_data(data: bytes) -> None:
    ...


def should_create_inference_data() -> bool:
    ...


def save_inference_data() -> bytes:
    ...


def load_inference_data(data: bytes) -> None:
    ...
