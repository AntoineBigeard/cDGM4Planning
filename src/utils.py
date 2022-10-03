import yaml
import numpy as np
import pandas as pd
import torch
from PIL import Image
from random import randrange


def read_yaml_config_file(path_config: str):
    with open(path_config) as conf:
        return yaml.load(conf, yaml.FullLoader)


def random_observation(shape):
    y = torch.ones(shape[0], shape[1], 2)
    y_ones_idx = [randrange(start=0, stop=shape[1]) for i in range(shape[0])]
    for i in range(shape[0]):
        single_one = torch.tensor(
            [1 if i == y_ones_idx[i] else 0 for i in range(shape[0])]
        )
        y[i, :, 0] = y[i, :, 0] * single_one
        y[i, :, 0] = torch.randn(shape[0], shape[1]) * single_one
    return y
