"""Run the project's real rayshader relief renderer without changing installed R.

Example:
  .venv/Scripts/python.exe scripts/run_environment_rayshader.py INPUT.json OUTPUT_DIR --exaggeration 8
The project-local runtime/library live in ignored work/rayshader. No API key is used.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--exaggeration", type=float, default=1.0)
    parser.add_argument("--rscript", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    runtime = root / "work" / "rayshader" / "runtime" / "app"
    rscript = args.rscript or runtime / "bin" / "x64" / "Rscript.exe"
    if not rscript.is_file():
        parser.error(f"Project-local Rscript is missing: {rscript}; supply --rscript for another runtime")
    if not args.input.is_file():
        parser.error(f"Input JSON is missing: {args.input}")
    if args.exaggeration <= 0:
        parser.error("--exaggeration must be positive")
    env = dict(os.environ)
    env.update(LC_ALL="C", LC_CTYPE="C", LANG="C", RGL_USE_NULL="TRUE")
    if args.rscript is None:
        env["R_HOME"] = str(runtime)
    command = [str(rscript), "--vanilla", str(root / "scripts" / "render_environment_rayshader.R"),
               str(args.input.resolve()), str(args.output.resolve()), str(args.exaggeration)]
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        result = subprocess.run(command, env=env, check=False, creationflags=flags,
                                capture_output=True, text=True, timeout=300)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Rayshader exceeded the 300 second rendering limit", file=sys.stderr)
        return 124


if __name__ == "__main__":
    raise SystemExit(main())
