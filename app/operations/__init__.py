class Operations:
    @staticmethod
    def addition( a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtraction( a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiplication( a: float, b: float) -> float:
        return a * b

    @staticmethod
    def division(a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b
    