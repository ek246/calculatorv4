from decimal import Decimal
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation

#Type aliases
Digits = Union[int, float, Decimal]
CalculationResult = Union[Digits, str]

class Calculator:
    def __init__(self, config: Optional[CalculatorConfig] = None):
        if config is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            config = CalculatorConfig(base_dir = project_root)

        self.config = config
        self.config.validate()

        os.makedirs(self.config.log_dir, exist_ok=True)
        self._setup_logging()

        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None

        self.observers: List[HistoryObserver] = []

        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        self._setup_directories()

        try:
            self.load_history()
        except Exception as e:
            logging.warning(f"Failed to load history: {e}")

        logging.info("Initialization complete.")

    def _setup_logging(self):
        try:
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()

            logging.basicConfig(
                filename = str(log_file),
                level = logging.INFO,
                format = '%(asctime)s - %(levelname)s - %(message)s',
                force = True
            )
            logging.info(f"Logging initialized successfully at {log_file}.")
        except Exception as e:
            logging.error(f"Failed to initialize logging: {e}")
    
    def _setup_directories(self) -> None:
        self.config.history_dir.mkdir(parents=True, exist_ok=True)

    def add_observer(self, observer: HistoryObserver) -> None:
        self.observers.append(observer)
        logging.info(f"Observer created: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        if observer in self.observers:
            self.observers.remove(observer)
            logging.info(f"Observer removed: {observer.__class__.__name__}")
        else:
            logging.warning(f"Observer not found: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        for observer in self.observers:
            observer.update(calculation)
            observer.notify(calculation)
            logging.info(f"Observer notified: {observer.__class__.__name__}")

    def set_operation(self, operation: Operation) -> None:
        self.operation_strategy = operation
        logging.info(f"Operation is set: {operation}")

    def perform_operation(self, a: Union[str, Digits], b:Union[str, Digits]) -> CalculationResult:
        if not self.operation_strategy:
            raise OperationError("No operation is set.")
        try:
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)
            result = self.operation_strategy.execute(validated_a, validated_b)
            calculation = Calculation(
                operand1=validated_a,
                operand2=validated_b,
                operation=self.operation_strategy.__class__.__name__.lower(),
            )
            self.undo_stack.append(CalculatorMemento(self.history.copy()))
            self.redo_stack.clear()
            self.history.append(calculation)
            if len(self.history) > self.config.max_history_size:
                self.history.pop(0)
            self.notify_observers(calculation)
            return result
        
        except ValidationError as ve:
            logging.error(f"Validation failed: {ve}")
            raise
        except Exception as e:
            logging.error(f"Operation failed: {e}")
            raise OperationError(f"Operation failed: {e}")
    def save_history(self) -> None:
        try:
            self.config.history_dir.mkdir(parents=True, exist_ok=True)

            data = []
            for calculation in self.history:
                data.append({
                    'operation': str(calculation.operation),
                    'operand1': str(calculation.operand1),
                    'operand2': str(calculation.operand2),
                    'outcome': str(calculation.outcome) if calculation.outcome is not None else None,
                    'timestamp': str(calculation.timeOfCalc) if calculation.timeOfCalc is not None else None,
                })

                if data:
                    df = pd.DataFrame(data)
                    df.to_csv(self.config.history_file, index=False)
                    logging.info(f"History saved to {self.config.history_file}")
                else:
                    pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'outcome', 'timestamp']).to_csv(self.config.history_file, index=False)
                    logging.info("Empty history saved")
        except Exception as e:
            logging.error(f"Could not save history: {e}")
            raise OperationError(f"Could not save history: {e}")
    def load_history(self) -> None:
        try:
            if self.config.history_file.exists():
                  df = pd.read_csv(self.config.history_file)
                  if not df.empty:
                    self.history = [
                         Calculation.from_dict({
                                'operation': row['operation'],
                                'operand1': row['operand1'],
                                'operand2': row['operand2'],
                                'outcome': row['outcome'],
                                'timeOfCalc': row['timestamp'],
                            })
                            for _, row in df.iterrows()
                        ]
                    logging.info(f"History loaded from {self.config.history_file}")
                  else:
                    logging.info("No history to load")
        except Exception as e:
                logging.error(f"Could not load history: {e}")
                raise OperationError(f"Could not load history: {e}")

    def load_history_dataframe(self) -> pd.DataFrame:
         data = []
         for calculation in self.history:
            data.append({
                    'operation': str(calculation.operation),
                    'operand1': str(calculation.operand1),
                    'operand2': str(calculation.operand2),
                    'outcome': str(calculation.outcome) if calculation.outcome is not None else None,
                    'timestamp': str(calculation.timeOfCalc) if calculation.timeOfCalc is not None else None,
                })
            
            return pd.DataFrame(data)
    def show_history(self) -> None:
        for calculation in self.history:
            print(f"{calculation.operation}({calculation.operand1}, {calculation.operand2}) = {calculation.outcome}")
        if not self.history:
            print("No history available.")
    def clear_history(self) -> None:
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("History cleared")
    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        memento = self.undo_stack.pop()
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True
    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        memento = self.redo_stack.pop()
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True