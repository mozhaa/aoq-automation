from pathlib import Path
import configparser

config = configparser.ConfigParser()
config.read((Path("files") / "config.hidden").resolve())
