from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.session import get_db
from backend.models.customer import Customer
from backend.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)

from backend.api.auth import router as auth_router
from backend.api.chat import router as chat_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get("/customers", response_model=list[CustomerResponse])
def get_customers(
    db: Annotated[Session, Depends(get_db)],
) -> list[Customer]:
    statement = select(Customer)
    return list(db.scalars(statement).all())


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Customer:
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    return customer


@app.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=201,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Customer:
    customer = Customer(
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        email=customer_data.email,
    )

    db.add(customer)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Customer with this email already exists.",
        ) from None

    db.refresh(customer)

    return customer


@app.patch("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Customer:
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    update_data = customer_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Customer with this email already exists.",
        ) from None

    db.refresh(customer)

    return customer


@app.delete("/customers/{customer_id}", status_code=204)
def delete_customer(
    customer_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    db.delete(customer)
    db.commit()