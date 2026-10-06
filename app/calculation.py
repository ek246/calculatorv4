from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict
from app.exceptions import OperationError

@dataclass
class Calculation:
    operation: str
    operand1: Decimal
    operand2: Decimal

    outcome: Decimal = field(init=False)
    timeOfCalc: datetime.datetime = field(default_factory=datetime.datetime.now, compare=False)

    def __post_init__(self):
        self.outcome = self.calculate()
    def calculate(self) -> Decimal:
        functions = {
            "addition": lambda x, y: x + y,
            "subtraction": lambda x, y: x - y,
            "multiplication": lambda x, y: x * y,
            "division": lambda x, y: x / y if y != 0 else self._raise_division_by_zero(),
            "power": lambda x, y: x ** y if y >= 0 else self._raise_neg_power(),
            "root": lambda x, y: x ** (Decimal(1) / y) if y != 0 and x >= 0 else self._raise_invalid_root(x, y)
        }

        if self.operation.lower() not in functions:
            raise OperationError("This operation is not supported")
        try:
            return functions[self.operation.lower()](self.operand1, self.operand2)
        except (InvalidOperation, ValueError, ArithmeticError) as e:
            raise OperationError(f"Error performing {self.operation}: {e}")
   
    @staticmethod
    def _raise_division_by_zero():
        raise OperationError("You cannot divide by zero")
    @staticmethod
    def _raise_neg_power():
        raise OperationError("This calculator does not support negative exponents")
    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal):
        if y == 0:
            raise OperationError("Root cannot be zero")
        if x < 0:
            raise OperationError("Cannot calculate a negative number's root")
        raise OperationError("This root operation is invalid") # pragma: no cover

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "outcome": str(self.outcome),
            "timeOfCalc": self.timeOfCalc.isoformat()
        }
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Calculation":
        try:
            output = Calculation(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"]),

            )
        except (ValueError, ArithmeticError) as e:
            raise OperationError(f"Error creating Calculation from dict: {e}")

        output.timeOfCalc = datetime.datetime.fromisoformat(data["timeOfCalc"])
        saved_result = Decimal(data["outcome"])
        if output.outcome != saved_result:
            logging.warning(f"This is a mismatch: calculated {output.outcome}, saved {saved_result}")
        return output

    def __str__(self) -> str:
        return f"Calculation(operation={self.operation}, operand1={self.operand1}, operand2={self.operand2}, outcome={self.outcome}, timeOfCalc={self.timeOfCalc})"

    def __repr__(self) -> str:
        return f"Calculation(operation={self.operation}, operand1={self.operand1}, operand2={self.operand2}, outcome={self.outcome}, " \
               f"timeOfCalc={self.timeOfCalc})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.outcome == other.outcome and
            self.timeOfCalc == other.timeOfCalc
        )
    def format_result(self, precision: int = 10) -> str:
        try:
            return str(self.outcome.quantize(Decimal(f"1.{'0'*precision}")))
        except (InvalidOperation, ArithmeticError) as e:
            return str(self.outcome)
    