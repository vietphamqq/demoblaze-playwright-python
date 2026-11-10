import allure
from playwright.sync_api import Page

from data.factories import OrderDetails
from utils.dialogs import accept_alert


class SignUpModal:
    def __init__(self, page: Page):
        self.page = page
        self.root = page.locator("#signInModal")
        self.username = self.root.locator("#sign-username")
        self.password = self.root.locator("#sign-password")
        self.submit = self.root.get_by_role("button", name="Sign up")

    @allure.step("Sign up as {username}")
    def sign_up(self, username: str, password: str) -> str:
        """Returns the alert text."""
        self.username.fill(username)
        self.password.fill(password)
        return accept_alert(self.page, self.submit.click)


class LoginModal:
    def __init__(self, page: Page):
        self.page = page
        self.root = page.locator("#logInModal")
        self.username = self.root.locator("#loginusername")
        self.password = self.root.locator("#loginpassword")
        self.submit = self.root.get_by_role("button", name="Log in")

    @allure.step("Log in as {username}")
    def log_in(self, username: str, password: str):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()

    @allure.step("Log in as {username} and read the alert")
    def log_in_expecting_alert(self, username: str, password: str) -> str:
        self.username.fill(username)
        self.password.fill(password)
        return accept_alert(self.page, self.submit.click)


class OrderModal:
    def __init__(self, page: Page):
        self.page = page
        self.root = page.locator("#orderModal")
        self.total = self.root.locator("#totalm")
        self.name = self.root.locator("#name")
        self.country = self.root.locator("#country")
        self.city = self.root.locator("#city")
        self.card = self.root.locator("#card")
        self.month = self.root.locator("#month")
        self.year = self.root.locator("#year")
        self.purchase_button = self.root.get_by_role("button", name="Purchase")

    @allure.step("Fill the order form")
    def fill(self, order: OrderDetails):
        self.name.fill(order.name)
        self.country.fill(order.country)
        self.city.fill(order.city)
        self.card.fill(order.card)
        self.month.fill(order.month)
        self.year.fill(order.year)

    @allure.step("Click Purchase")
    def purchase(self):
        self.purchase_button.click()

    @allure.step("Click Purchase and read the alert")
    def purchase_expecting_alert(self) -> str:
        return accept_alert(self.page, self.purchase_button.click)


class PurchaseConfirmation:
    """The sweetalert popup shown after a successful order."""

    def __init__(self, page: Page):
        self.root = page.locator(".sweet-alert")
        self.title = self.root.locator("h2")
        self.details = self.root.locator("p.lead")
        self.ok_button = self.root.locator("button.confirm")

    @allure.step("Close the purchase confirmation")
    def close(self):
        self.ok_button.click()

    def detail(self, label: str) -> str:
        # details text looks like "Id: 123\nAmount: 360 USD\nCard Number: ...\nName: ..."
        for line in self.details.inner_text().splitlines():
            if line.startswith(f"{label}:"):
                return line.split(":", 1)[1].strip()
        raise AssertionError(f"'{label}' not found in confirmation: {self.details.inner_text()}")
