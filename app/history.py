from abc import ABC, abstractmethod
import logging
from typing import Any
from app.calculation import Calculation

class HistoryObserver(ABC):
    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        pass #pragma: no cover
    @abstractmethod
    def notify(self, calculation: Calculation) -> None:
        pass #pragma: no cover

class LoggingObserver(HistoryObserver):
    def update(self, calculation: Calculation) -> None:
        if calculation is not None:
            logging.info(f"Calculation performed: {calculation.operation} with operands {calculation.operand1} and {calculation.operand2} resulting in {calculation.outcome}")
        else:
            raise AttributeError("There cannot be no calculation provided")
    def notify(self, calculation: Calculation) -> None:
        self.update(calculation)

class AutoSaveObserver(HistoryObserver):
    def __init__(self, calculator: Any):
        if not hasattr(calculator, "config") or not hasattr(calculator, "save_history"):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator
    def notify(self, calculation: Calculation) -> None:
        self.update(calculation)

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("There cannot be no calculation provided")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("Calculations auto-saved")