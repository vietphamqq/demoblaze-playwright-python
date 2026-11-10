from pages.base_page import BasePage
from utils.dialogs import accept_alert


class ProductPage(BasePage):
    path = "/prod.html"

    def __init__(self, page):
        super().__init__(page)
        self.title = page.locator("#tbodyid h2.name")
        self.price = page.locator("#tbodyid h3.price-container")
        self.description = page.locator("#more-information p")
        self.add_to_cart_button = page.get_by_role("link", name="Add to cart")

    def open_product(self, product_id: int):
        self.page.goto(f"{self.path}?idp_={product_id}")
        return self

    def add_to_cart(self) -> str:
        return accept_alert(self.page, self.add_to_cart_button.click)
