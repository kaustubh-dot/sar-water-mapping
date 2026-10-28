"""Run one frozen raw/filtered U-Net pair; see --help for inputs and caps."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from sar_water.train import main


if __name__ == '__main__':
    raise SystemExit(main())
