from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
from pathlib import Path
import os
from typing import Optional
from dotenv import load_dotenv
from app.exceptions import ConfigurationError

load_dotenv()

def get_project_root() -> Path:
    current_file = Path(__file__)
    return current_file.parent.parent

@dataclass
class CalculatorConfig:
    def __init__(self,
                 base_dir: Optional[Path] = None,
                 max_history_size: Optional[int] = None,
                 auto_save: Optional[bool] = None,
                 precision: Optional[int] = None,
                 max_input_value: Optional[Number] = None,
                 default_encoding: Optional[str] = None
        ):
        project_root = get_project_root()
        self.base_dir = base_dir or Path(os.getenv('CALCULATOR_BASE_DIR', project_root)).resolve()
        self.max_history_size = max_history_size or int(os.getenv('CALCULATOR_MAX_HISTORY_SIZE', 100))
        self.auto_save = auto_save if auto_save is not None else os.getenv('CALCULATOR_AUTO_SAVE', 'true').lower() in ['true', '1']
        self.precision = precision or int(os.getenv('CALCULATOR_PRECISION', 2))
        self.max_input_value = max_input_value or Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e6'))
        self.default_encoding = default_encoding or os.getenv('CALCULATOR_DEFAULT_ENCODING', 'utf-8')

    @property
    def log_dir(self) -> Path:
        return Path(os.getenv('CALCULATOR_LOG_DIR', str(self.base_dir / 'logs'))).resolve()

    @property
    def history_dir(self) -> Path:
        return Path(os.getenv('CALCULATOR_HISTORY_DIR', str(self.base_dir / 'history'))).resolve()

    @property
    def history_file(self) -> Path:
        return Path(os.getenv('CALCULATOR_HISTORY_FILE', str(self.history_dir / 'history.csv'))).resolve()

    @property
    def log_file(self) -> Path:
        return Path(os.getenv('CALCULATOR_LOG_FILE', str(self.log_dir / 'app.log'))).resolve()

    def validate(self) -> None:
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size can't be 0 or negative")
        if self.precision <= 0:
            raise ConfigurationError("precision can't be 0 or negative")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value can't be 0 or negative")
        if not self.base_dir.exists():
            raise ConfigurationError(f"base_dir '{self.base_dir}' does not exist")