class CalculatorError(Exception):
    """Base class for all calculator-related exceptions."""
    pass

class ValidationError(CalculatorError):
    """Exception raised for input validation failures."""
    pass

class OperationError(CalculatorError):
    """Exception raised for errors during calculation operations."""
    pass

class ConfigurationError(CalculatorError):
    """Exception raised for errors related to invalid calculator configuration."""
    pass