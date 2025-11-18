import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

# --- THIS IS THE FIX ---
# Changed from app.models.user import User and app.models.calculation import Calculation
from app.models import User, Calculation
# -----------------------

from app.schemas.calculation import CalculationCreate, OperationType
from app.operations.calculation_logic import perform_calculation

# --- Unit Tests (moved from separate file) ---

def test_calculation_factory():
    """
    Unit test for the calculation logic factory.
    """
    assert perform_calculation(10, 5, OperationType.ADD) == 15
    assert perform_calculation(10, 5, OperationType.SUBTRACT) == 5
    assert perform_calculation(10, 5, OperationType.MULTIPLY) == 50
    assert perform_calculation(10, 5, OperationType.DIVIDE) == 2

def test_schema_valid_creation():
    """
    Unit test for valid Pydantic schema creation.
    """
    data = {"a": 10, "b": 5, "type": "Add"}
    calc_schema = CalculationCreate(**data)
    assert calc_schema.a == 10
    assert calc_schema.b == 5
    assert calc_schema.type == OperationType.ADD

def test_schema_division_by_zero():
    """
    Unit test to ensure Pydantic schema validation catches
    division by zero.
    """
    data = {"a": 10, "b": 0, "type": "Divide"}
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)
    
    # Check that the error message is what we expect
    assert "Division by zero is not allowed" in str(exc_info.value)

# --- Integration Test ---

def test_create_calculation_integration(db_session: Session, test_user: User):
    """
    Integration test to:
    1. Use the 'test_user' fixture.
    2. Create a CalculationCreate schema.
    3. Perform the calculation.
    4. Create a Calculation DB model.
    5. Save it to the database.
    6. Query the database to verify it was saved correctly.
    """
    
    # 1. User is created by the 'test_user' fixture
    assert test_user.id is not None
    
    # 2. Create the schema
    calc_data = CalculationCreate(a=20, b=10, type=OperationType.DIVIDE)
    
    # 3. Perform the calculation
    result = perform_calculation(calc_data.a, calc_data.b, calc_data.type)
    assert result == 2.0
    
    # 4. Create the Calculation DB model
    db_calculation = Calculation(
        a=calc_data.a,
        b=calc_data.b,
        type=calc_data.type.value, # Store the string value
        result=result,
        owner_id=test_user.id # Link to the user
    )
    
    # 5. Save to the database
    db_session.add(db_calculation)
    db_session.commit()
    db_session.refresh(db_calculation)
    
    # 6. Query to verify
    assert db_calculation.id is not None
    assert db_calculation.a == 20
    assert db_calculation.b == 10
    assert db_calculation.type == "Divide"
    assert db_calculation.result == 2.0
    assert db_calculation.owner_id == test_user.id
    
    # Verify the relationship
    assert db_calculation.owner.username == test_user.username