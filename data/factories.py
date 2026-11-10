import uuid
from dataclasses import dataclass

from faker import Faker

fake = Faker()


@dataclass
class User:
    username: str
    password: str


@dataclass
class OrderDetails:
    name: str
    country: str
    city: str
    card: str
    month: str
    year: str


def new_user() -> User:
    # demoblaze has no way to delete users, so keep the prefix easy to spot
    return User(username=f"qa_{uuid.uuid4().hex[:12]}", password=fake.password(length=12))


def new_order() -> OrderDetails:
    return OrderDetails(
        name=fake.name(),
        country=fake.country(),
        city=fake.city(),
        card=fake.credit_card_number(card_type="visa16"),
        month=str(fake.random_int(1, 12)),
        year=str(fake.random_int(2027, 2031)),
    )
