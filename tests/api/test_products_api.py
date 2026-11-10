import allure
import pytest

from api.models import ApiError


@allure.title("Verify the first page returns 9 products")
@pytest.mark.smoke
def test_first_page_of_products(api):
    page = api.get_products()

    # the home page shows 9 products per page
    assert len(page.Items) == 9
    assert page.LastEvaluatedKey is not None
    assert all(p.price > 0 and p.title for p in page.Items)


@allure.title("Verify the next page returns the rest of the products without duplicates")
def test_pagination_returns_the_rest_without_duplicates(api):
    first = api.get_products()
    second = api.get_next_products(first.LastEvaluatedKey["id"])

    first_ids = {p.id for p in first.Items}
    second_ids = {p.id for p in second.Items}
    assert second_ids, "second page is empty"
    assert first_ids.isdisjoint(second_ids)


@allure.title("Verify products can be listed by category '{category}'")
@pytest.mark.parametrize("category", ["phone", "notebook", "monitor"])
def test_products_by_category(api, category):
    products = api.get_by_category(category)

    assert products, f"no products in '{category}'"
    assert {p.cat for p in products} == {category}


@allure.title("Verify category lists add up to all products")
def test_category_lists_add_up_to_all_products(api):
    all_ids = {p.id for p in api.get_all_products()}
    by_category = {
        p.id for cat in ("phone", "notebook", "monitor") for p in api.get_by_category(cat)
    }

    assert by_category == all_ids


@allure.title("Verify a single product can be fetched by id")
def test_get_single_product(api):
    expected = next(p for p in api.get_products().Items if p.id == 1)

    product = api.get_product(1)

    assert product == expected


@allure.title("Verify an unknown product returns 'Not found.'")
def test_get_unknown_product(api):
    response = api.post("/view", {"id": "999999"})

    assert ApiError(**response.json()).errorMessage == "Not found."
