"""Cart is filled through the API, then checked and changed in the UI.

Faster and less flaky than clicking through product pages just to get data in place.
"""

import pytest
from playwright.sync_api import expect

PRODUCT_IDS = [1, 9, 10]  # a phone, a laptop and a monitor


@pytest.fixture
def seeded_cart(logged_in, api, token):
    for product_id in PRODUCT_IDS:
        api.add_to_cart(token, product_id)
    return [api.get_product(pid) for pid in PRODUCT_IDS]


@pytest.mark.smoke
def test_cart_shows_seeded_products_and_total(seeded_cart, cart_page):
    cart_page.open()

    expect(cart_page.rows).to_have_count(len(seeded_cart))
    for product in seeded_cart:
        expect(cart_page.row(product.title)).to_contain_text(f"{product.price:g}")
    expect(cart_page.total).to_have_text(f"{sum(p.price for p in seeded_cart):g}")


def test_delete_from_cart_updates_backend(seeded_cart, cart_page, api, token):
    removed, *kept = seeded_cart
    cart_page.open()
    expect(cart_page.rows).to_have_count(len(seeded_cart))

    cart_page.delete(removed.title)

    expect(cart_page.rows).to_have_count(len(kept))
    expect(cart_page.row(removed.title)).to_have_count(0)
    expect(cart_page.total).to_have_text(f"{sum(p.price for p in kept):g}")
    assert sorted(i.prod_id for i in api.get_cart(token).Items) == sorted(p.id for p in kept)
