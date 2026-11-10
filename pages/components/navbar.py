import allure
from playwright.sync_api import Page

from pages.components.modals import LoginModal, SignUpModal


class Navbar:
    def __init__(self, page: Page):
        self.page = page
        self.home_link = page.locator("#navbarExample a.nav-link", has_text="Home")
        self.cart_link = page.locator("#cartur")
        self.login_link = page.locator("#login2")
        self.signup_link = page.locator("#signin2")
        self.logout_link = page.locator("#logout2")
        self.welcome_text = page.locator("#nameofuser")

    @allure.step("Open the login form")
    def open_login(self) -> LoginModal:
        self.login_link.click()
        return LoginModal(self.page)

    @allure.step("Open the sign up form")
    def open_signup(self) -> SignUpModal:
        self.signup_link.click()
        return SignUpModal(self.page)

    @allure.step("Go to the cart from the navbar")
    def go_to_cart(self):
        self.cart_link.click()

    @allure.step("Log out")
    def log_out(self):
        self.logout_link.click()
