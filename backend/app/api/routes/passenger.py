from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from app.api.deps import SessionDep  # active database session injection
from app.models import Passenger, PassengerCreate, PassengerPublic

router = APIRouter(prefix="/passenger", tags=["passenger"])


@router.post(
    "/clean", response_model=PassengerPublic, status_code=status.HTTP_201_CREATED
)
def create_and_clean_new_passenger(
    passenger_in: PassengerCreate, session: SessionDep
) -> Passenger:
    """Create and clean a new passenger in the database with strict incoming validation."""

    # 1. Check if a Passenger with the same id already exists
    existing_passenger = session.exec(
        select(Passenger).where(Passenger.passenger_id == passenger_in.passenger_id)
    ).first()

    if existing_passenger:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A passenger with ID = '{passenger_in.passenger_id}' already exists.",
        )

    # 2. Convert the validated API payload data into the DB Table Model instance
    db_passenger = Passenger.model_validate(passenger_in)

    # 3. Save to database
    session.add(db_passenger)
    session.commit()
    session.refresh(db_passenger)

    # 4. Return the database object (FastAPI will format it to look like PassengerPublic)
    return db_passenger


# TODO
# - update passenger
# - delete passenger
# - get all passengers
# - get one passenger
# - etc
