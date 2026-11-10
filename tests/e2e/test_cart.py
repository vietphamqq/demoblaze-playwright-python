import allure
import pytest
from playwright.sync_api import expect


@allure.title("Verify adding a product to the cart on {browser_name}")
@pytest.mark.smoke
def test_add_product_to_cart(logged_in, product_page, cart_page, api, token):
    product = api.get_product(1)
    product_page.open_product(product.id)
    expect(product_page.title).to_have_text(product.title)

    message = product_page.add_to_cart()

    assert message == "Product added."
    cart_page.open()
    expect(cart_page.rows).to_have_count(1)
    expect(cart_page.row(product.title)).to_contain_text(f"{product.price:g}")
    expect(cart_page.total).to_have_text(f"{product.price:g}")
    # and the backend agrees
    assert [i.prod_id for i in api.get_cart(token).Items] == [product.id]


@allure.title("Verify adding the same product twice on {browser_name}")
def test_add_same_product_twice(logged_in, product_page, cart_page, api):
    product = api.get_product(2)
    product_page.open_product(product.id)
    expect(product_page.title).to_have_text(product.title)

    product_page.add_to_cart()
    product_page.add_to_cart()

    cart_page.open()
    expect(cart_page.rows).to_have_count(2)
    expect(cart_page.total).to_have_text(f"{product.price * 2:g}")
