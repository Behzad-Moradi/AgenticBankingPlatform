from pydantic import BaseModel, Field


class DriverLicenceDetails(BaseModel):
    full_name: str | None = Field(
        default=None,
        description="Full name shown on the driver licence.",
    )

    date_of_birth: str | None = Field(
        default=None,
        description="Date of birth shown on the driver licence.",
    )

    address: str | None = Field(
        default=None,
        description="Residential address shown on the driver licence.",
    )

    licence_number: str | None = Field(
        default=None,
        description="Driver licence number.",
    )