# demoblaze-playwright-python

[![tests](https://github.com/vietphamqq/demoblaze-playwright-python/actions/workflows/tests.yml/badge.svg)](https://github.com/vietphamqq/demoblaze-playwright-python/actions/workflows/tests.yml)

UI and API tests for [demoblaze.com](https://www.demoblaze.com) written with Playwright, Pytest and Python.

I put this together as a small example of how I usually set up a test framework: page objects for the UI, a separate API client, test data created through the API instead of the UI, and a CI pipeline that runs everything on every push and once a night.

## What's covered

| Area | API | UI |
|---|---|---|
| Sign up / log in | new user, existing user, wrong password, unknown user, token check | sign up form, log in and log out, error alerts, session from API token |
| Products | first page, pagination, categories, single product, unknown product | product list, category filter, next page, product details |
| Cart | add, view, delete one item, clear, carts are separate per user | add from product page, totals, delete from cart |
| Checkout | | place order, empty form validation |

36 tests in total. They run in about 30 seconds in parallel on my machine.

## Stack

- Python 3.11+
- Playwright with `pytest-playwright`
- Pytest, `pytest-xdist` for parallel runs, `pytest-rerunfailures`
- `requests` + `pydantic` for the API client and response models
- Faker for test data
- Allure for reports
- Ruff for linting and formatting
- GitHub Actions

## Project layout

```
api/            API client and pydantic models for api.demoblaze.com
config/         settings loader + one yaml file per environment
data/           test data factories (users, order details)
pages/          page objects, with shared navbar and modals in pages/components
utils/          small helpers (browser alerts, polling the backend)
tests/api/      API only, no browser
tests/e2e/      UI flows
tests/hybrid/   data set up through the API, then checked in the UI
conftest.py     fixtures: settings, api client, users, logged in session, pages
```

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

pytest -n auto
```

Some other ways to run it:

```bash
pytest tests/api                      # API only, no browser needed
pytest -m smoke                       # quick check of the main flows
pytest -m ui --headed --slowmo 300    # watch the browser
pytest --browser firefox              # another browser
pytest --env demo --base-url https://www.demoblaze.com
```

Allure report:

```bash
pytest -n auto --alluredir allure-results
allure serve allure-results
```

When a UI test fails, `--tracing retain-on-failure` keeps the Playwright trace in `test-results/`. Open it with `playwright show-trace <file>.zip`.

## How it's put together

**Environments.** Settings live in `config/environments/<env>.yaml` and are picked with `--env` (default `demo`). `BASE_URL`, `API_URL` and `TIMEOUT_MS` environment variables override the file, which is how CI would point the same suite at a different environment. Demoblaze only has one public environment, but adding a staging one is just another yaml file. Nothing secret is stored in the repo. If an environment needed credentials they would come from env vars or CI secrets.

**Test data.** Every test that needs a user gets a brand new one from the `user` fixture, created through the `/signup` API. Because nobody shares accounts, tests can run in parallel without stepping on each other. After the test the fixture clears that user's cart. Demoblaze has no API to delete users, so the accounts stay behind. They all start with `qa_` so they're easy to spot.

**Skipping the login form.** Only the login tests use the login form. Everything else uses the `logged_in` fixture, which logs in through the API and puts the token into the `tokenp_` cookie the site reads. It's faster and one broken login form doesn't fail the whole suite.

**API + UI together.** The hybrid tests fill the cart through the API and then check what the UI shows. Some UI tests also double check the backend afterwards, for example that placing an order really empties the cart.

**Waiting.** No sleeps. UI checks use Playwright's `expect()`, which retries until the timeout. For backend state that changes a bit later (the cart after checkout) there is a small `wait_until` helper.

**Browser alerts.** Demoblaze reports most things with `window.alert()`. `utils/dialogs.py` accepts the alert and returns its text so tests can assert on it.

## CI

`.github/workflows/tests.yml` runs on every push to main, on pull requests, every night and on demand:

1. lint with Ruff
2. API tests
3. UI tests on Chromium and Firefox in parallel
4. an Allure report built from all the results, uploaded as an artifact

Failed UI tests upload their traces and screenshots. Tests get one retry in CI because the demo site is sometimes slow. A test that only passes on retry still shows up in the report.

From the Actions tab you can also start a run by hand with a different env or a marker like `smoke`.

## Things I noticed about the site

- The login API returns the token as a plain string, `"Auth_token: <token>"`, not as JSON.
- `/deletecart` takes the username, while the other cart endpoints take the token.
- The last page of `/pagination` still returns a `LastEvaluatedKey`, and asking for the page after that gives a 500.
- One product title ("Sony vaio i7") has a trailing newline in the data.
- After a purchase the cart is emptied on the backend a moment after the confirmation pops up, not at the same time.
