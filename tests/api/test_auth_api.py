import pytest

from api.models import ApiError
from data.factories import new_user


@pytest.mark.smoke
def test_sign_up_new_user(api):
    user = new_user()

    response = api.sign_up(user.username, user.password)

    assert response.status_code == 200
    # success is an empty JSON string, errors come back as {"errorMessage": ...}
    assert response.json() == ""


def test_sign_up_existing_user_is_rejected(api, user):
    response = api.sign_up(user.username, "whatever123")

    assert ApiError(**response.json()).errorMessage == "This user already exist."


@pytest.mark.smoke
def test_log_in_returns_token_for_that_user(api, user):
    token = api.get_token(user.username, user.password)

    info = api.check_token(token)
    assert info.username == user.username
    assert info.token == token


@pytest.mark.parametrize(
    "case, expected",
    [
        ("wrong_password", "Wrong password."),
        ("unknown_user", "User does not exist."),
    ],
)
def test_log_in_errors(api, user, case, expected):
    if case == "wrong_password":
        response = api.log_in(user.username, "not-the-password")
    else:
        response = api.log_in(f"nobody_{user.username}", user.password)

    assert response.status_code == 200
    assert ApiError(**response.json()).errorMessage == expected
