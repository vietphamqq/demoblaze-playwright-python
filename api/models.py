from pydantic import BaseModel


class Product(BaseModel):
    id: int
    title: str
    price: float
    cat: str
    desc: str
    img: str


class ProductPage(BaseModel):
    Items: list[Product]
    LastEvaluatedKey: dict | None = None


class CartItem(BaseModel):
    id: str
    cookie: str
    prod_id: int


class Cart(BaseModel):
    Items: list[CartItem]


class TokenInfo(BaseModel):
    token: str
    username: str
    expiration: int


class ApiError(BaseModel):
    errorMessage: str
