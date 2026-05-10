# Step definitions

Add your Behave step definitions here. One file per domain is recommended:

```
features/steps/
├── kafka_steps.py       ← step definitions for kafka/ feature files
├── api_steps.py         ← step definitions for api/ feature files
└── ...
```

A step definition connects a Gherkin step to executable Python code:

```python
# features/steps/api_steps.py
from behave import given, when, then

@given('the API path "{path}"')
def step_api_path(context, path):
    context.path = path
    context.validate = lambda: validate_url_path(path)

@when('I validate the URL structure')
def step_validate(context):
    context.result = context.validate()

@then('it should be valid')
def step_valid(context):
    assert context.result.valid, f"Expected valid, got errors: {context.result.errors}"

@then('it should be invalid')
def step_invalid(context):
    assert not context.result.valid, "Expected invalid, but got valid"
```

See `examples/kafka/features/steps/validation_steps.py` for a complete example.

Only mark a scenario `@enforced` once its step definitions exist and the scenario passes locally.
