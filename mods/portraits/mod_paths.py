"""Machine-specific paths are environment variables, never committed user paths."""
import os
from pathlib import Path
GAME_DATA=Path(os.environ.get('TW3K_DATA', 'C:/Program Files (x86)/Steam/steamapps/common/Total War THREE KINGDOMS/data'))
WORKSHOP=Path(os.environ.get('TW3K_WORKSHOP', str(GAME_DATA.parents[2]/'workshop/content/779340')))
SEVENZIP=Path(os.environ.get('TW3K_7ZIP', 'C:/Program Files/7-Zip/7z.exe'))
