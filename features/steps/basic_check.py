from behave import given, when, then

@given('I have two numbers {num1:d} and {num2:d}')
def step_given_two_numbers(context, num1, num2):
    context.num1 = num1
    context.num2 = num2

@when('I add them')
def step_when_add_two_numbers(context):
    context.result = context.num1 + context.num2

@then('the result should be {expected_result:d}')
def step_then_check_result(context, expected_result):
    assert context.result == expected_result, f"Expected {expected_result}, but got {context.result}"
