import allure
import pytest

from data.factories import new_user


@allure.title("Verify products can be added to the cart")
@pytest.mark.smoke
def test_add_products_to_cart(api, token):
    api.add_to_cart(token, 1)
    api.add_to_cart(token, 3)

    cart = api.get_cart(token)

    assert sorted(item.prod_id for item in cart.Items) == [1, 3]


@allure.title("Verify a new user has an empty cart")
def test_new_user_has_empty_cart(api, token):
    assert api.get_cart(token).Items == []


@allure.title("Verify one item can be deleted from the cart")
def test_delete_one_item(api, token):
    api.add_to_cart(token, 1)
    api.add_to_cart(token, 2)
    to_delete = next(i for i in api.get_cart(token).Items if i.prod_id == 1)

    api.delete_cart_item(to_delete.id)

    assert [i.prod_id for i in api.get_cart(token).Items] == [2]


@allure.title("Verify the cart can be cleared")
def test_clear_cart(api, user, token):
    for product_id in (1, 2, 3):
        api.add_to_cart(token, product_id)

    api.clear_cart(user.username)

    assert api.get_cart(token).Items == []


@allure.title("Verify carts are separate for each user")
def test_carts_are_separate_per_user(api, token):
    other = new_user()
    api.sign_up(other.username, other.password)
    other_token = api.get_token(other.username, other.password)

    api.add_to_cart(token, 1)

    assert api.get_cart(other_token).Items == []
