import re

# Parser for simple algebra expressions without variables, making sure
# that 3 + 5, 5 + 3, 1 + 7, 8, etc. all result in a correct answer
# check if a value is a number
def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# returns if operator 1 has greater precedence than operator 2
def greater_precedence(operator1, operator2):
    # dictionary to assign precedence
    precedence = {'+': 0, '-': 0, '*': 1, '/': 1, '^':2}
    return precedence[operator1]>=precedence[operator2]

# implementing shunting yard algorithm
def shunting_yard(expression):
    output_queue = []
    operator_stack = []
    n = len(expression)
    i = 0

    # go through every character in the expression
    while i < n:
        char = expression[i]

        # skip space
        if char.isspace():
            i += 1
            continue
        
        # handle numbers, including negative numbers and floats
        if char.isdigit() or (char == '-' and (i == 0 or expression[i-1] in '(')):
            number = char
            i += 1
            # add other digits or points
            while i < n and (expression[i].isdigit() or expression[i] == '.'):
                number += expression[i]
                i += 1
            output_queue.append(number)
            continue
        
        # handle left parenthesis
        elif char == '(':
            operator_stack.append(char)
            i += 1
        
        # handle right parenthesis
        elif char == ')':
            # as long as there are operators on the operator stack, pop operators and add them to the output queue
            while operator_stack and operator_stack[-1] != '(':
                output_queue.append(operator_stack.pop())
            # pop the left parenthesis from the stack
            operator_stack.pop()
            i += 1
        
        # handle operators
        elif char in '+-*/^':
            # if the operator at the top of the stack has greater precedence than the current token, pop it and move it to the output queue
            while (operator_stack and operator_stack[-1] != '(' and
                   greater_precedence(operator_stack[-1], char)):
                output_queue.append(operator_stack.pop())
            # add the new operator to the operator stack
            operator_stack.append(char)
            i += 1

    # move all remaining operators to the output queue
    while operator_stack:
        output_queue.append(operator_stack.pop())
    
    return output_queue

# Function to evaluate the RPN (Reverse Polish Notation)
def evaluate_rpn(notation):
    stack = []
    for token in notation:
        if is_number(token):
            stack.append(float(token))
        else:
            # get the numbers from the stack and apply mathematical operations
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                stack.append(a / b)
            elif token == '^':
                stack.append(a ** b)
    return stack.pop()

# Function to process and evaluate an algebraic expression
def process_expression(expression):
    rpn = shunting_yard(expression)
    return evaluate_rpn(rpn)

# Parser for regular expressions taken directly from https://www.cs.princeton.edu/courses/archive/spr09/cos333/beautiful.html
def match(regexp, text):
    if regexp[0] == '^':
        return matchhere(regexp[1:], text)
    while True:  # must look even if string is empty
        if matchhere(regexp, text):
            return 1
        if not text:  # equivalent to *text++ != '\0'
            break
        text = text[1:]  # move to the next character
    return 0

def matchhere(regexp, text):
    if regexp == '':
        return 1
    if len(regexp) > 1 and regexp[1] == '*':
        return matchstar(regexp[0], regexp[2:], text)
    if regexp == '$' and len(regexp) == 1:
        return text == ''
    if text and (regexp[0] == '.' or regexp[0] == text[0]):
        return matchhere(regexp[1:], text[1:])
    return 0

def matchstar(c, regexp, text):
    while True:  # a * matches zero or more instances
        if matchhere(regexp, text):
            return 1
        if not text or (text[0] != c and c != '.'):
            break
        text = text[1:]  # move to the next character
    return 0