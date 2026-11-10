from pages.base_page import BasePage
from pages.components.modals import OrderModal


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page):
        super().__init__(page)
        self.rows = page.locator("#tbodyid tr")
        self.total = page.locator("#totalp")
        self.place_order_button = page.get_by_role("button", name="Place Order")

    def row(self, title: str):
        return self.rows.filter(has_text=title)

    def delete(self, title: str):
        self.row(title).get_by_role("link", name="Delete").click()

    def place_order(self) -> OrderModal:
        self.place_order_button.click()
        return OrderModal(self.page)
