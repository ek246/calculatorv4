from app.operations import addition, subtraction, multiplication, division
def calculator():
    print("Welcome to the REPL calculator. To quit, type 'stop'.")
    while True:
        user_input = input("Enter an operation (e.g., 'add 2 3'), enter stop to quit: ")
        if user_input.lower() == 'stop':
            print("Stopping the calculator")
            break

        try:
            operation, num1, num2 = user_input.split()
            num1, num2 = float(num1), float(num2)

            if operation == 'add':
                result = addition(num1, num2)
            elif operation == 'subtract':
                result = subtraction(num1, num2)
            elif operation == 'multiply':
                result = multiplication(num1, num2)
            elif operation == 'divide':
                result = division(num1, num2)
            else:
                print("Only 'add', 'subtract', 'multiply', or 'divide' are accepted.")
                continue

            print(f"The result is: {result}")

        except ValueError:
            print("Invalid input. Enter two numbers and an operation.")
        except ZeroDivisionError:
            print("Error: You cannot divide by zero.")