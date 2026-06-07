import uuid
import re
from typing import Optional

from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, field_validator, model_validator


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

## =================================
## App Data Models (ftom template)
## =================================

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int



# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

# Generic message
class Message(SQLModel):
    message: str


## =====================
## Business Data model
## =====================

# Shared properties
class PassengerBase(SQLModel):
    # Weather Survived or not: 0 = No, 1 = Yes
    survived: int

    # Ticket class: 1 = 1st, 2 = 2nd, 3 = 3rd
    pclass: int = Field(default=None)
    
    name: str = Field(default=None)

    # The title extracted from the name
    extracted_title: Optional[str] = Field(default=None)


    sex: str = Field(default=None)
    age: int = Field(default=None)

    # Number of siblings or spouses aboard the Titanic
    sibsp: int = Field(default=None)

    # Number of parents or children aboard the Titanic
    parch: int = Field(default=None)

    # Ticket number (ex: A/5 21171)
    ticket: str = Field(default=None)

    # Passenger fare: the revenue earned from carrying passengers in regularly scheduled service. Ex. 7.25
    fare: float = Field(default=None)

    cabin: str = Field(default=None)

    # Port of Embarkation: C = Cherbourg, Q = Queenstown, S = Southampton
    embarked: str = Field(default=None)

    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

# Strict validation for API requests 
class PassengerCreate(PassengerBase):
    passenger_id: int = Field(primary_key=True)

    # Strict Field Validator for 'pclass'
    @field_validator("pclass")
    @classmethod
    def validate_pclass(cls, v: int) -> int:
        if v not in [1, 2, 3]:
            raise ValueError("Pclass must be a value between 1 and 3.")
        return v

    # Strict Field Validator for 'fare'
    @field_validator("fare")
    @classmethod
    def validate_fare(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Fare must be a strictly positive number.")
        return v

    # Strict Field Validator for 'name'
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 3 or len(cleaned) > 50:
            raise ValueError("Name must be between 3 and 50 characters.")
        return cleaned.title()
    
    @model_validator(mode="after")
    def extract_title_from_name(self) -> "PassengerCreate":
        """We don't validate the name here. We only extract the title if it exists."""
        cleaned = self.name.strip()

        # Regex Pattern:
        # ^(Mr|Mrs|Ms|Dr) -> Matches exactly these titles at the start
        # \.?              -> Matches an optional period (e.g., "Mr." or "Mr")
        # \b              -> Word boundary (ensures "Mr" doesn't match "Mister")
        title_pattern = r"\b(Mr|Mrs|Ms|Dr)\.?\b"
        
        # match = re.match(title_pattern, cleaned, re.IGNORECASE)
        match = re.search(title_pattern, cleaned, re.IGNORECASE)

        if match:
            extracted_title = match.group(1)
            extracted_title = extracted_title.capitalize()

            # Normalization: 
            # "Ms", "Mme", "Ms.", "Mme.", "Lady" => "Ms."
            # "Mr", "Mr.", "Sir" => "Mr."
            # "Ms.", "Mme.", "Lady" => "Mrs."
            # ... 

            if extracted_title in ["Ms", "Ms.", "Mme", "Mme.", "Lady"]:
                extracted_title = "Ms."
            elif extracted_title in ["Mr", "Mr.", "Sir"]:
                extracted_title = "Mr."
            elif extracted_title in ["Mrs", "Mrs."]:
                extracted_title = "Mrs."
            elif extracted_title in ["Dr", "Dr."]:
                extracted_title = "Dr."    

            self.extracted_title = extracted_title

        return self
    


# 3. Clean database table (No heavy validation logic here)
class Passenger(PassengerBase, table=True):
    passenger_id: int = Field(primary_key=True)


# Schema used for API responses
class PassengerPublic(PassengerBase):
    passenger_id: int


