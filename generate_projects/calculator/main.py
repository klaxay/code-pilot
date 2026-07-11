import argparse
import sys

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

def main():
    parser = argparse.ArgumentParser(description='CLI Calculator')
    parser.add_argument('--num1', type=float, required=True, help='First number')
    parser.add_argument('--num2', type=float, required=True, help='Second number')
    parser.add_argument('--op', type=str, choices=['add', 'subtract', 'multiply', 'divide'], required=True, help='Operation to perform')
    args = parser.parse_args()

    operations = {
        'add': add,
        'subtract': subtract,
        'multiply': multiply,
        'divide': divide
    }

    try:
        result = operations[args.op](args.num1, args.num2)
        print(result)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()