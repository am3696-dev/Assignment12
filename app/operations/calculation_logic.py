from enum import Enum
import operator

class OperationType(str, Enum):
    """
    Enum for the allowed calculation types.
    """
    ADD = "Add"
    SUBTRACT = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"

# Our "Factory" mapping
# This maps the enum to the actual Python operator function
CALCULATION_OPERATIONS = {
    OperationType.ADD: operator.add,
    OperationType.SUBTRACT: operator.sub,
    OperationType.MULTIPLY: operator.mul,
    OperationType.DIVIDE: operator.truediv,
}

def perform_calculation(a: float, b: float, type: OperationType) -> float:
    """
    Factory function to perform the correct calculation.
    
    Validates the operation type and returns the result.
    Division by zero is handled by the Pydantic schema,
    but we could add a redundant check here if desired.
    """
    operation_func = CALCULATION_OPERATIONS.get(type)
    
    if not operation_func:
        raise ValueError(f"Invalid calculation type: {type}")
        
    # We assume division by zero is already caught by the schema
    # before this function is ever called.
    
    result = operation_func(a, b)
    return result