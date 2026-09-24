from backend.db.session import SessionLocal
from backend.models.card import Card
from backend.models.customer import Customer


CUSTOMER_ID = 7


with SessionLocal() as db:
    cards = [
        Card(
            customer_id=CUSTOMER_ID,
            last_four="4821",
            card_type="debit",
            status="active",
        ),
        Card(
            customer_id=CUSTOMER_ID,
            last_four="7314",
            card_type="credit",
            status="active",
        ),
    ]

    db.add_all(cards)
    db.commit()


print("Cards created.")