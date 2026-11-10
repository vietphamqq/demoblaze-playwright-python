import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_home_page_shows_first_page_of_products(home_page, api):
    expected_titles = [p.title for p in api.get_products().Items]

    home_page.open()

    expect(home_page.product_titles).to_have_text(expected_titles)


@pytest.mark.parametrize(
    "menu_item, category",
    [("Phones", "phone"), ("Laptops", "notebook"), ("Monitors", "monitor")],
)
def test_filter_by_category(home_page, api, menu_item, category):
    expected_titles = [p.title for p in api.get_by_category(category)]
    home_page.open()
    # wait for the default list first, otherwise the filter can race with it
    expect(home_page.product_titles).to_have_count(9)

    home_page.filter_by(menu_item)

    expect(home_page.product_titles).to_have_text(expected_titles)


def test_next_page(home_page, api):
    first = api.get_products()
    second = api.get_next_products(first.LastEvaluatedKey["id"])
    home_page.open()
    expect(home_page.product_titles).to_have_count(len(first.Items))

    home_page.next_button.click()

    expect(home_page.product_titles).to_have_text([p.title for p in second.Items])


def test_product_details_match_api(home_page, product_page, api):
    product = api.get_product(1)
    home_page.open()

    home_page.open_product(product.title)

    expect(product_page.title).to_have_text(product.title)
    expect(product_page.price).to_contain_text(f"${product.price:g}")
    expect(product_page.description).to_contain_text(product.desc.split("\n")[0].strip())
