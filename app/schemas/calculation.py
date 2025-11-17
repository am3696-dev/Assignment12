import uuid
from pydantic import BaseModel, root_validator, Field

# Import the OperationType enum from the logic file we created in Step 2
from app.operations.calculation_logic import OperationType

class CalculationBase(BaseModel):
    a: float = Field(..., description="The first operand")
    b: float = Field(..., description="The second operand")
    type: OperationType = Field(..., description="The type of calculation")


class CalculationCreate(CalculationBase):
    """
    Schema for creating a new calculation.
    This is what the API will receive.
    """
    
    @root_validator(pre=False, skip_on_failure=True)
    def check_division_by_zero(cls, values):
        """
        Validate that if the operation is 'Divide', 'b' is not zero.
        """
        if 'b' in values and 'type' in values:
            if values['type'] == OperationType.DIVIDE and values['b'] == 0:
                raise ValueError("Division by zero is not allowed")
        
        return values

class CalculationRead(CalculationBase):
    """
    Schema for returning a calculation from the API.
    This includes the ID, result, and owner ID.
    """
    id: uuid.UUID
    result: float
    owner_id: uuid.UUID

    class Config:
        from_attributes = True #