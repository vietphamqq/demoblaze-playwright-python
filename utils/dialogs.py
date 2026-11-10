from collections.abc import Callable

from playwright.sync_api import Page


def accept_alert(page: Page, action: Callable[[], None], timeout: float = 15000) -> str:
    """Run an action that triggers a browser alert, accept it and return its text.

    Demoblaze uses plain window.alert() for most feedback (sign up, login errors,
    add to cart), so a lot of checks go through this.
    """
    # accept straight away: some alerts fire inside the click handler itself
    # (e.g. the empty order form) and the click would hang until it is closed
    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_event("dialog", timeout=timeout) as dialog_info:
        action()
    return dialog_info.value.message
