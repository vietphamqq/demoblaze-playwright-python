import allure

from pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.product_cards = page.locator("#tbodyid .card")
        self.product_titles = page.locator("#tbodyid .card-title a")
        self.next_button = page.locator("#next2")
        self.prev_button = page.locator("#prev2")

    @allure.step("Filter products by {category_name}")
    def filter_by(self, category_name: str):
        """category_name as shown on the page: Phones, Laptops or Monitors."""
        self.page.locator("#contcont a.list-group-item", has_text=category_name).click()

    @allure.step("Go to the next page of products")
    def go_to_next_page(self):
        self.next_button.click()

    @allure.step("Open product {title}")
    def open_product(self, title: str):
        self.product_titles.filter(has_text=title).first.click()

    def card_price(self, title: str):
        card = self.product_cards.filter(has=self.page.get_by_role("link", name=title))
        return card.locator("h5")
