import base64
import uuid

import requests

from api.models import ApiError, Cart, Product, ProductPage, TokenInfo


class DemoblazeApiError(Exception):
    pass


def encode_password(password: str) -> str:
    # the site base64-encodes the password before sending it, so we do the same
    return base64.b64encode(password.encode()).decode()


class DemoblazeApi:
    """Thin wrapper around api.demoblaze.com.

    The raw `post`/`get` helpers return the response as is, which the negative
    tests use. The other methods parse the body and raise on errorMessage.
    """

    def __init__(self, api_url: str, timeout: float = 15):
        self.api_url = api_url
        self.timeout = timeout
        self.session = requests.Session()

    def post(self, path: str, payload: dict) -> requests.Response:
        return self.session.post(f"{self.api_url}{path}", json=payload, timeout=self.timeout)

    def get(self, path: str) -> requests.Response:
        return self.session.get(f"{self.api_url}{path}", timeout=self.timeout)

    @staticmethod
    def _check(response: requests.Response):
        response.raise_for_status()
        body = response.json() if response.text.strip() else None
        if isinstance(body, dict) and "errorMessage" in body:
            raise DemoblazeApiError(ApiError(**body).errorMessage)
        return body

    # auth

    def sign_up(self, username: str, password: str) -> requests.Response:
        return self.post("/signup", {"username": username, "password": encode_password(password)})

    def log_in(self, username: str, password: str) -> requests.Response:
        return self.post("/login", {"username": username, "password": encode_password(password)})

    def get_token(self, username: str, password: str) -> str:
        body = self._check(self.log_in(username, password))
        # success body is a plain string: "Auth_token: <token>"
        return body.split("Auth_token: ", 1)[1]

    def check_token(self, token: str) -> TokenInfo:
        body = self._check(self.post("/check", {"token": token}))
        return TokenInfo(**body["Item"])

    # products

    def get_products(self) -> ProductPage:
        return ProductPage(**self._check(self.get("/entries")))

    def get_next_products(self, last_id: str) -> ProductPage:
        return ProductPage(**self._check(self.post("/pagination", {"id": last_id})))

    def get_all_products(self) -> list[Product]:
        page = self.get_products()
        items = list(page.Items)
        # the last page still has a LastEvaluatedKey, it just comes back empty,
        # and after that the key is the string "None" (asking for it gives a 500)
        while page.LastEvaluatedKey and page.LastEvaluatedKey["id"] != "None":
            page = self.get_next_products(page.LastEvaluatedKey["id"])
            if not page.Items:
                break
            items.extend(page.Items)
        return items

    def get_product(self, product_id: int) -> Product:
        return Product(**self._check(self.post("/view", {"id": str(product_id)})))

    def get_by_category(self, category: str) -> list[Product]:
        return ProductPage(**self._check(self.post("/bycat", {"cat": category}))).Items

    # cart

    def add_to_cart(self, token: str, product_id: int) -> None:
        payload = {"id": str(uuid.uuid4()), "cookie": token, "prod_id": product_id, "flag": True}
        self._check(self.post("/addtocart", payload))

    def get_cart(self, token: str) -> Cart:
        return Cart(**self._check(self.post("/viewcart", {"cookie": token, "flag": True})))

    def delete_cart_item(self, item_id: str) -> None:
        self._check(self.post("/deleteitem", {"id": item_id}))

    def clear_cart(self, username: str) -> None:
        # note: deletecart takes the username, not the token
        self._check(self.post("/deletecart", {"cookie": username}))
