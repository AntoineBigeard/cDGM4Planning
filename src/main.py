import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint


from src.data.datamodule.datamodule import MyDataModule
from src.model.model.pretrained_model import PretrainedTorchModel
from src.model.lit_model.lit_model import MyLitModel
from src.utils import read_yaml_config_file

from src.utils import transforms_data, categories

import argparse
import os
import yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path_config",
        help="config path that contains config for data, models, training.",
        default="/home/ec2-user/repo/team_b/config/config.yaml",
        required=False,
    )
    parser.add_argument(
        "--mode",
        help="mode fit, test or predict",
        default="fit",
        required=False,
    )

    args = parser.parse_args()

    path_config = args.path_config
    mode = args.mode

    config = read_yaml_config_file(path_config)
    checkpoint_path = config.get("checkpoint_path")
    conf_datamodule = config.get("datamodule")
    conf_model = config.get("model")
    conf_pretrained_model = config.get("pretrained_model")
    conf_lit_model = config.get("lit_model")
    conf_trainer = config.get("trainer")
    name_exp = config.get("name_experiment")
    conf_ts_board = config.get("tensorboard_logs")
    conf_checkpoint_callback = config.get("checkpoint_callback")

    tsboard_logger = TensorBoardLogger(
        conf_ts_board["save_dir"],
        conf_ts_board["name"],
    )

    logs_folder = os.path.join(tsboard_logger.save_dir, tsboard_logger.name, f"version_{tsboard_logger.version}")
    os.makedirs(logs_folder, exist_ok=True)

    datamodule = MyDataModule(
        transforms_img=transforms_data,
        transform_window={},
        transforms_meta=None,
        categories=categories,
        path_logs=logs_folder,
        **conf_datamodule,
    )

    num_classes = len(datamodule.selected_categories)

    if conf_lit_model["use_torch_model"]:
        model = PretrainedTorchModel(**conf_pretrained_model, num_classes=num_classes)

    lit_model = MyLitModel(
        model=model,
        learning_rate=conf_lit_model["learning_rate"],
    )

    if checkpoint_path is not None:
        lit_model.load_from_checkpoint(checkpoint_path)

    with open(os.path.join(logs_folder, 'config.yaml'), 'w') as dst:
        yaml.dump(config, dst)

    early_stop_callback = EarlyStopping(
        monitor="train/loss",
        min_delta=0.01,
        patience=10,
        verbose=False,
        mode="min",
    )

    checkpoint_callback = ModelCheckpoint(
        dirpath=os.path.join(logs_folder, "checkpoints"),
        verbose=True,
        **conf_checkpoint_callback,
    )

    trainer = pl.Trainer(
        logger=tsboard_logger,
        callbacks=[early_stop_callback],
        **conf_trainer,
        enable_progress_bar=True,
    )

    if mode == "fit":
        trainer.fit(lit_model, datamodule)

    elif mode == "test":
        trainer.test(lit_model, datamodule)
        
    elif mode == "predict":
        trainer.predict(lit_model, datamodule)

    else:
        raise ValueError("Please give a valid mode: fit, test or predict")