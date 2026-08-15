#!/usr/bin/env python3
"""Backward-compatible entrypoint for figure generation."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("build_paper_assets.py")), run_name="__main__")
