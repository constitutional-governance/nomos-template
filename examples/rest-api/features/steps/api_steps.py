import re
from behave import given, when, then


# ── Simple URL validator (example implementation) ──────────────────────────────

_URL_PATTERN = re.compile(r"^/api/v\d+/[a-z][a-z-]+(/.*)?$")
_VERB_PATTERN = re.compile(r"[A-Z]|[a-z](get|post|put|delete|process|create|update)[A-Z]", re.IGNORECASE)


def _validate_url(path: str):
    errors = []
    if not re.match(r"^/api/v\d+/", path):
        errors.append("version prefix required — path must start with /api/v{N}/")
    else:
        resource_segment = path.split("/")[3] if len(path.split("/")) > 3 else ""
        verbs = ["get", "post", "put", "delete", "process", "create", "update", "fetch", "cancel"]
        if any(v == resource_segment.lower() for v in verbs):
            errors.append("resource name must be a noun, not a verb")
    return errors


@given('the API path "{path}"')
def step_api_path(context, path):
    context.path = path


@when("I validate the URL structure")
def step_validate_url(context):
    context.errors = _validate_url(context.path)
    context.valid = len(context.errors) == 0


@then("it should be valid")
def step_valid(context):
    assert context.valid, f"Expected valid, got errors: {context.errors}"


@then("it should be invalid")
def step_invalid(context):
    assert not context.valid, f"Expected invalid, but got valid for: {context.path}"


@then('the reason should mention "{keyword}"')
def step_reason_mentions(context, keyword):
    combined = " ".join(context.errors).lower()
    assert keyword.lower() in combined, f"Expected '{keyword}' in errors: {context.errors}"
