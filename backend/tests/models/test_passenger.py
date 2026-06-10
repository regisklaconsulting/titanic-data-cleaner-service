import pytest
from pydantic import ValidationError

from app.models import PassengerCreate

# === HAPPY PATH TESTS ===


def test_create_valid_passenger():
    """Ensure a perfectly valid passenger is instantiated and cleaned correctly."""

    print("toto")

    # Use the PAssengerCreate model to guarantee the validators execution.
    passenger = PassengerCreate(
        passenger_id=1,
        survived=1,
        pclass=1,
        name="  my super passenger  ",  # intentionally whitespaces
        sex="M",
        age=42,
        sibsp=1,
        parch=2,
        ticket="GGD-99887",
        fare=49.99,
        cabin="G6",
        embarked="S",
    )

    assert passenger.age == 42
    assert passenger.fare == 49.99
    assert passenger.name == "My Super Passenger"  # Should be stripped and title-cased
    # etc


@pytest.mark.parametrize(
    "input_name, expected_title",
    [
        ("Mr Jone", "Mr."),
        ("mrs Jones", "Mrs."),
        ("Dr. Smith", "Dr."),
        ("  Ms Watson", "Ms."),
        ("Futrelle, Mrs. Jacques Heath (Lily May Peel)", "Mrs."),
        ("Braund, Mr. Owen Harris", "Mr."),
    ],
)
def test_extract_title_from_valid_name(input_name, expected_title):
    """Ensure valid titles at the start allow model creation."""
    passenger = PassengerCreate(passenger_id=1, name=input_name, survived=1)
    assert passenger.extracted_title == expected_title


# === EDGE CASE & INVALID DATA TESTS ===


def test_passenger_name_too_short():
    """Name should fail if under 3 characters."""
    with pytest.raises(ValidationError) as exc_info:
        PassengerCreate(passenger_id=1, survived=1, name="Ab")
    assert "Name must be between 3 and 50 characters." in str(exc_info.value)


@pytest.mark.parametrize("invalid_pclass", [4, 7])
def test_passenger_invalid_pclass(invalid_pclass):
    """Pclass should fail if not between 1 and 3."""
    with pytest.raises(ValidationError) as exc_info:
        PassengerCreate(
            passenger_id=1, name="Mr Jones", survived=1, pclass=invalid_pclass
        )
    assert "Pclass must be a value between 1 and 3." in str(exc_info.value)
