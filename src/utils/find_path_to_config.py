import sys
from pathlib import Path

def find_config():
        if hasattr(sys, "_MEIPASS"):
            PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
        else:
            PROJ_ROOT = Path(r'C:\Users\A\skyView')
            
        return PROJ_ROOT / 'config.ini'