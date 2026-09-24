from langchain.tools import tool
from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models.customer import Customer


@tool
def get_customer_by_email(email: str) -> str:
    """Get a customer's details using their email address."""

    with SessionLocal() as db:
        statement = select(Customer).where(Customer.email == email)
        customer = db.scalar(statement)

        if customer is None:
            return f"No customer found with email {email}."

        return (
            f"Customer ID: {customer.id}\n"
            f"Name: {customer.first_name} {customer.last_name}\n"
            f"Email: {customer.email}"
        )