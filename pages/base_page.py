from playwright.sync_api import Page

from pages.components.navbar import Navbar


class BasePage:
    path = "/"

    def __init__(self, page: Page):
        self.page = page
        self.navbar = Navbar(page)

    def open(self):
        # base_url comes from the browser context, see conftest.py
        self.page.goto(self.path)
        return self
