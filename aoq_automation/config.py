import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read((Path("files") / "config.hidden").resolve())
