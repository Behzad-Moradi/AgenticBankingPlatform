from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.security import create_access_token, hash_password, verify_password
from backend.db.session import get_db
from backend.models.customer import Customer
from backend.schemas.auth import Token, RegisterRequest, RegisterResponse




router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    customer = db.scalar(
        select(Customer).where(
            Customer.email == form_data.username.strip().lower()
        )
    )

    if (
        customer is None
        or customer.hashed_password is None
        or not verify_password(
            form_data.password,
            customer.hashed_password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        customer_id=customer.id
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    existing_customer = db.scalar(
        select(Customer).where(
            Customer.email == request.email
        )
    )

    if existing_customer is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    customer = Customer(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        hashed_password=hash_password(request.password),
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return RegisterResponse(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
    )