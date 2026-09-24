import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.session import get_db
from backend.models.customer import Customer


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
)


def get_current_customer(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Customer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        customer_id = int(subject)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    customer = db.get(Customer, customer_id)

    if customer is None:
        raise credentials_exception

    return customer