from app.calculator import Calculator
from decimal import Decimal
import logging
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory

def calculator_repl():
    try:
        calculator = Calculator()
        calculator.add_observer(LoggingObserver())
        calculator.add_observer(AutoSaveObserver(calculator))

        print("Calculator has started. Type 'stop' to quit.")

        while True:
            try:
                input_str = input("\nEnter operation: ").lower().strip()
                if input_str.lower() == "help":
                    print("\n Things you can do:")
                    print("Available operations: addition, subtraction, multiplication, division, power, root")
                    print("history - view calculation history")
                    print("clear - clear calculation history")
                    print("load - load calculation history from file")
                    print("stop - exit the calculator")
                    print("undo - undo the last operation from file")
                    print("redo - redo the last undone operation from file")
                    print("save - save calculation history to file")
                    continue
                if input_str == "stop":
                    try:
                        calculator.save_history()
                    except Exception as e:
                        print(f"History lost: {e}")
                    break
                if input_str == "history":
                    calculator.show_history()
                    continue
                if input_str == "clear":
                    try:
                        calculator.clear_history()
                        print("Calculation history cleared")
                    except Exception as e:
                        print(f"Error clearing history: {e}")
                    continue
                if input_str == "load":
                    try:
                        calculator.load_history()
                        print("Calculation history loaded")
                    except Exception as e:
                        print(f"Error loading history: {e}")
                    continue
                if input_str == "undo":
                    try:
                        if calculator.undo():
                            print("Last operation undone")
                        else:
                            print("No actions to undo.")
                    except Exception as e:
                        print(f"Error undoing operation: {e}")
                    continue
                if input_str == "redo":
                    try:
                        if calculator.redo():
                            print("Last undone operation redone")
                        else:
                            print("No actions to redo.")
                    except Exception as e:
                        print(f"Error redoing operation: {e}")
                    continue
                if input_str == "save":
                    try:
                        calculator.save_history()
                        print("Calculation history saved")
                    except Exception as e:
                        print(f"Error saving history: {e}")
                    continue
                if input_str in ["add", "subtract", "multiply", "divide"]:
                    try:
                        print("\nEnter numbers for the operation or type 'c' to cancel")
                        operand_a = input("Enter the first number: ")
                        if operand_a.lower() == 'c':
                            print("Operation cancelled")
                            continue
                        operand_b = input("Enter the second number: ")
                        if operand_b.lower() == 'c':
                            print("Operation cancelled")
                            continue
                        operation_names = {
                            "add": "addition",
                            "subtract": "subtraction",
                            "multiply": "multiplication",
                            "divide": "division"
                        }
                        operation = OperationFactory.create_operation(operation_names[input_str])
                        calculator.set_operation(operation)
                        result = calculator.perform_operation(float(operand_a), float(operand_b))
                        print(f"Result: {result}")
                    except (OperationError, ValidationError) as e:
                        print(f"Error: {e}")
                    continue
            except KeyboardInterrupt:
                print("\nCalculator stopped.")
                break
            except EOFError:
                print("\nNo more input detected. Stopping calculator.")
                break
    except Exception as e:
        print(f"Unexpected error: {e}")
            
    