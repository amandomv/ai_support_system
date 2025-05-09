from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """
    Model for user accounts stored in the database.

    This model represents a user account with its basic information
    and authentication details.
    """

    id: int | None = Field(None, description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    password_hash: str = Field(..., description="Hashed password for the user")
    user_name: str | None = Field(None, description="User's display name")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Timestamp when the user was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Timestamp when the user was last updated",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True  # For ORM compatibility
