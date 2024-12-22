import flet as ft
from flet import Page
from pathlib import Path
import sys

from src.GUI.gui import GUI

if hasattr(sys, "_MEIPASS"):
        PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
else:
    PROJ_ROOT = Path(r"C:\Users\A\skyView")

if __name__ == "__main__":

    def main(page: Page):
        GUI(page)

    ft.app(target=main)
