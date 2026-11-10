import pytest
from playwright.sync_api import expect

from data.factories import new_user


def test_sign_up_through_the_form(home_page, api):
    user = new_user()
    home_page.open()

    message = home_page.navbar.open_signup().sign_up(user.username, user.password)

    assert message == "Sign up successful."
    # double check on the backend that the account really works
    assert api.get_token(user.username, user.password)


def test_sign_up_with_taken_username(home_page, user):
    home_page.open()

    message = home_page.navbar.open_signup().sign_up(user.username, "something-else")

    assert message == "This user already exist."


@pytest.mark.smoke
def test_log_in_and_log_out(home_page, user):
    home_page.open()

    home_page.navbar.open_login().log_in(user.username, user.password)
    expect(home_page.navbar.welcome_text).to_have_text(f"Welcome {user.username}")
    expect(home_page.navbar.login_link).to_be_hidden()

    home_page.navbar.log_out()
    expect(home_page.navbar.login_link).to_be_visible()
    expect(home_page.navbar.welcome_text).to_be_hidden()


@pytest.mark.parametrize(
    "case, expected",
    [
        ("wrong_password", "Wrong password."),
        ("unknown_user", "User does not exist."),
    ],
)
def test_log_in_errors(home_page, user, case, expected):
    username = user.username if case == "wrong_password" else f"nobody_{user.username}"
    password = "not-the-password" if case == "wrong_password" else user.password
    home_page.open()

    message = home_page.navbar.open_login().log_in_expecting_alert(username, password)

    assert message == expected
    expect(home_page.navbar.welcome_text).to_be_hidden()


def test_session_from_api_token(home_page, logged_in):
    # the logged_in fixture never touches the login form
    home_page.open()

    expect(home_page.navbar.welcome_text).to_have_text(f"Welcome {logged_in.username}")
