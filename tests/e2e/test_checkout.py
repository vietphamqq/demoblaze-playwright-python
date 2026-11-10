import re

import pytest
from playwright.sync_api import expect

from data.factories import new_order
from pages.components.modals import PurchaseConfirmation
from utils.wait import wait_until


@pytest.fixture
def cart_with_product(logged_in, api, token):
    product = api.get_product(1)
    api.add_to_cart(token, product.id)
    return product


@pytest.mark.smoke
def test_place_order(cart_with_product, cart_page, ui, api, token):
    order = new_order()
    cart_page.open()
    expect(cart_page.rows).to_have_count(1)

    modal = cart_page.place_order()
    expect(modal.total).to_contain_text(f"{cart_with_product.price:g}")
    modal.fill(order)
    modal.purchase()

    confirmation = PurchaseConfirmation(ui)
    expect(confirmation.title).to_have_text("Thank you for your purchase!")
    assert confirmation.detail("Amount") == f"{cart_with_product.price:g} USD"
    assert confirmation.detail("Card Number") == order.card
    assert confirmation.detail("Name") == order.name
    assert re.fullmatch(r"\d+", confirmation.detail("Id"))
    # placing the order empties the cart on the backend, but not instantly
    wait_until(lambda: api.get_cart(token).Items == [], message="cart was not emptied")

    confirmation.ok_button.click()
    # the site redirects to the home page a couple of seconds after OK
    expect(ui).to_have_url(re.compile(r"/index\.html$"))


def test_place_order_without_name_and_card(cart_with_product, cart_page):
    cart_page.open()
    expect(cart_page.rows).to_have_count(1)

    modal = cart_page.place_order()
    message = modal.purchase_expecting_alert()

    assert message == "Please fill out Name and Creditcard."
    expect(modal.root).to_be_visible()
