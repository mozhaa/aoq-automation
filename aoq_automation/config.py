from pathlib import Path

with (Path("files") / "token.hidden").open("r") as f:
    token = f.read()
