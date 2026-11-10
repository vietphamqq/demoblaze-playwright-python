from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext, Page, expect

from api.client import DemoblazeApi
from config.settings import Settings, load_settings
from data.factories import User, new_user
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage

TESTS_DIR = Path(__file__).parent / "tests"


def pytest_addoption(parser):
    parser.addoption("--env", default="demo", help="environment file from config/environments")
    parser.addoption("--api-url", default=None, help="override the api url from the env file")


def pytest_collection_modifyitems(items):
    # tag tests by folder so `-m api` / `-m ui` work without decorating every file
    for item in items:
        folder = Path(item.fspath).relative_to(TESTS_DIR).parts[0]
        item.add_marker(pytest.mark.api if folder == "api" else pytest.mark.ui)


# config


@pytest.fixture(scope="session")
def settings(request) -> Settings:
    return load_settings(request.config.getoption("--env"))


@pytest.fixture(scope="session")
def base_url(request, settings) -> str:
    # pytest-playwright's --base-url still works and takes priority
    return (request.config.getoption("base_url") or settings.base_url).rstrip("/")


@pytest.fixture(scope="session")
def api_url(request, settings) -> str:
    return (request.config.getoption("--api-url") or settings.api_url).rstrip("/")


@pytest.fixture(scope="session", autouse=True)
def _expect_timeout(settings):
    expect.set_options(timeout=settings.timeout_ms)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1440, "height": 900}}


# api + test data


@pytest.fixture(scope="session")
def api(api_url) -> DemoblazeApi:
    return DemoblazeApi(api_url)


@pytest.fixture
def user(api) -> User:
    """A fresh user created through the API, with an empty cart after the test."""
    user = new_user()
    response = api.sign_up(user.username, user.password)
    assert response.ok and "errorMessage" not in response.text, response.text
    yield user
    api.clear_cart(user.username)


@pytest.fixture
def token(api, user) -> str:
    return api.get_token(user.username, user.password)


@pytest.fixture
def logged_in(context: BrowserContext, base_url, user, token) -> User:
    """Skips the login form: puts the API token into the browser cookie the site reads."""
    host = base_url.split("://", 1)[-1]
    context.add_cookies([{"name": "tokenp_", "value": token, "domain": host, "path": "/"}])
    return user


# pages


@pytest.fixture
def ui(page: Page, settings) -> Page:
    page.set_default_timeout(settings.timeout_ms)
    return page


@pytest.fixture
def home_page(ui) -> HomePage:
    return HomePage(ui)


@pytest.fixture
def product_page(ui) -> ProductPage:
    return ProductPage(ui)


@pytest.fixture
def cart_page(ui) -> CartPage:
    return CartPage(ui)
