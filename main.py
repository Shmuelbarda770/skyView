import flet as ft
from flet import Page

from src.GUI.gui import GUI

if __name__ == "__main__":

    def main(page: Page):
        GUI(page)

    ft.app(target=main)
