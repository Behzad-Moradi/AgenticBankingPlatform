from dataclasses import dataclass


@dataclass
class BankingContext:
    customer_id: int | None = None
    authenticated: bool = False