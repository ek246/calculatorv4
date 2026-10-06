from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError, OperationError
class Operation(ABC):
    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        pass #pragma: no cover

    def validate_operands(self,a: Decimal, b: Decimal) -> None:
        pass #pragma: no cover

    def __str__(self) -> str:
        return self.__class__.__name__

class Addition(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b

class Subtraction(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b

class Multiplication(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b

class Division(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        if b == 0:
            raise OperationError("You cannot divide by zero.")
        return a / b

class Power(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative power is not allowed")
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a ** b

class Root(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a,b)
        if a < 0:
            raise ValidationError("The root cannot be negative.")
        if b == 0:
            raise ValidationError("Zero root is undefined.")
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))

class OperationFactory:
    _operations: Dict[str, type] = {
        'addition': Addition,
        'subtraction': Subtraction,
        'multiplication': Multiplication,
        'division': Division,
        'power': Power,
        'root': Root
    }
    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        if not issubclass(operation_class, Operation):
            raise TypeError("operation_class must be a subclass of Operation.")
        cls._operations[name.lower()] = operation_class
    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        operation_types = cls._operations.get(operation_type.lower())
        if not operation_types:
            raise ValueError("The operation type is not registered.")
        return operation_types()