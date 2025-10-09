#!/usr/bin/env python3

import json
import tomllib
import sys
import os
import shutil
from pathlib import Path

if __name__ == "__main__":
    assert len(sys.argv) == 2
    data = None
    with open(sys.argv[1], "rb") as f:
        data = tomllib.load(f)

    path = Path.home().joinpath(*data["ffs"]["id"].split("."))
    assert not path.exists()

    path.mkdir(parents=True, exist_ok=True)

    src = Path(data["ffs"]["state"]["path"])
    shutil.copy(src, path.joinpath("state").with_suffix(src.suffix))

    with open(path / "descriptor.json", "w") as f:
        json.dump(data, f)

    env = data["ffs"]["environment"]
    utaha_descriptor = {
        "taskdata": {
            "alias": data["ffs"]["id"],
            "comment": data["ffs"]["comment"],
        },
        "backend": {
            "type": "UtahaPosixBackendBackend",
        },
        "job": {
            "type": "UtahaJobsShellJob",
            "command": [
                "zsh", "-c",
                f"source ~/.zshrc && conda activate {env} && python3 {Path(__file__).parent.parent.joinpath('main.py')} {path}"
            ],
        },
    }

    utaha_path = path / "utaha.json"
    with open(utaha_path, "w") as f:
        json.dump(utaha_descriptor, f)

    os.system(f"utaha --load {utaha_path}")
    os.system(f"utaha --start --alias {utaha_descriptor['taskdata']['alias']}")
