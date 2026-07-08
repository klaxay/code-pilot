def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def main():
    print("Simple Calculator")
    print("Operations: +, -, *, /")
    print("Type 'q' to quit\n")
    
    while True:
        try:
            num1_input = input("Enter first number: ")
            if num1_input.lower() == 'q':
                print("Goodbye!")
                break
            num1 = float(num1_input)
        except ValueError:
            print("Invalid input. Please enter a valid number or 'q' to quit.")
            continue
        
        operation = input("Enter operation (+, -, *, /): ")
        if operation.lower() == 'q':
            print("Goodbye!")
            break
        
        if operation not in ['+', '-', '*', '/']:
            print("Invalid operation. Please use +, -, *, or /")
            continue
        
        try:
            num2_input = input("Enter second number: ")
            if num2_input.lower() == 'q':
                print("Goodbye!")
                break
            num2 = float(num2_input)
        except ValueError:
            print("Invalid input. Please enter a valid number or 'q' to quit.")
            continue
        
        try:
            if operation == '+':
                result = add(num1, num2)
            elif operation == '-':
                result = subtract(num1, num2)
            elif operation == '*':
                result = multiply(num1, num2)
            elif operation == '/':
                result = divide(num1, num2)
            
            print(f"Result: {result}\n")
        except ValueError as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()