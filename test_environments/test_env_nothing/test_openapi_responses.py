import os
import re

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
OPENAPI_URL = f"{BASE_URL}/openapi.json"


def resolve_ref(ref, components):
    """Resolve a $ref in the OpenAPI schema."""
    if not ref.startswith("#/components/schemas/"):
        raise ValueError(f"Unsupported $ref: {ref}")
    schema_name = ref.split("/")[-1]
    return components[schema_name]


def build_example_from_schema(schema, components):
    """Recursively build an example from a schema definition."""
    if "$ref" in schema:
        schema = resolve_ref(schema["$ref"], components)
    if "example" in schema:
        return schema["example"]
    if schema.get("type") == "object":
        example = {}
        for prop, prop_schema in schema.get("properties", {}).items():
            example[prop] = build_example_from_schema(prop_schema, components)
        return example
    if schema.get("type") == "array":
        item_schema = schema.get("items", {})
        return [build_example_from_schema(item_schema, components)]
    # Fallback for simple types
    return schema.get("example", None)


def get_openapi_endpoints():
    """Yield (method, path, request_example, response_example,
    all_response_codes, required_request_fields,
    required_response_fields) for each endpoint with a 200 response."""
    resp = requests.get(OPENAPI_URL)
    resp.raise_for_status()
    openapi = resp.json()
    components = openapi.get("components", {}).get("schemas", {})
    for path, methods in openapi["paths"].items():
        for method, details in methods.items():
            responses = details.get("responses", {})
            if "200" in responses:
                request_example = {}
                response_example = None
                required_request_fields = []
                required_response_fields = []
                all_response_codes = [
                    int(code) if code.isdigit() else code
                    for code in responses.keys()
                ]

                # Extract request example if requestBody exists
                if "requestBody" in details:
                    content = details["requestBody"].get("content", {})
                    for media_type, media_details in content.items():
                        # Try to resolve $ref in schema
                        schema = media_details.get("schema", {})

                        # For POST requests, ensure schema has properties defined
                        if method == "post":
                            if not schema:
                                raise AssertionError(
                                    f"POST {path} is missing schema in requestBody"
                                )
                            # Resolve $ref if present
                            resolved_schema = schema
                            if "$ref" in schema:
                                resolved_schema = resolve_ref(
                                    schema["$ref"], components
                                )
                            if "properties" not in resolved_schema:
                                raise AssertionError(
                                    f"POST {path} schema is missing 'properties'. "
                                    f"Schema must define properties for request validation."
                                )
                            # Extract required fields from request schema
                            required_request_fields = resolved_schema.get(
                                "required", []
                            )

                        if schema:
                            request_example = build_example_from_schema(
                                schema, components
                            )
                        # If there is a direct example, prefer it
                        if "example" in media_details:
                            request_example = media_details["example"]
                        elif "examples" in media_details:
                            first = next(
                                iter(media_details["examples"].values())
                            )
                            request_example = first.get("value", {})

                # Extract response example and required fields from 200 response
                response_200 = responses["200"]
                response_content = response_200.get("content", {})
                for media_type, media_details in response_content.items():
                    schema = media_details.get("schema", {})
                    if "$ref" in schema:
                        schema = resolve_ref(schema["$ref"], components)
                    if schema:
                        response_example = build_example_from_schema(
                            schema, components
                        )
                        required_response_fields = schema.get("required", [])
                    # If there is a direct example, prefer it
                    if "example" in media_details:
                        response_example = media_details["example"]
                    elif "examples" in media_details:
                        first = next(iter(media_details["examples"].values()))
                        response_example = first.get("value", {})

                yield method, path, request_example, response_example, all_response_codes, required_request_fields, required_response_fields


@pytest.mark.depends(on=["test_health_endpoint.py::test_health_endpoint"])
@pytest.mark.parametrize(
    "method,path,request_example,response_example,all_response_codes,required_request_fields,required_response_fields",
    list(get_openapi_endpoints()),
)
def test_openapi_request_examples(
    method,
    path,
    request_example,
    response_example,
    all_response_codes,
    required_request_fields,
    required_response_fields,
):
    """Automatically checks that all documented endpoints with a 200
    response in the OpenAPI spec return one of their documented response
    codes."""
    # Replace path parameters with values from the response example
    url = f"{BASE_URL}{path}"
    if response_example and "{" in path:
        # Extract path parameters and substitute with values from example
        for param_match in re.finditer(r"\{(\w+)\}", path):
            param_name = param_match.group(1)
            if param_name in response_example:
                url = url.replace(
                    f"{{{param_name}}}", str(response_example[param_name])
                )

    if method == "get":
        # GET requests should have response examples
        assert (
            response_example is not None
        ), f"No response example found for {method.upper()} {path}"
        resp = requests.get(url)
    elif method == "post":
        assert (
            request_example
        ), f"No request example found for {method.upper()} {path}"
        assert (
            response_example is not None
        ), f"No response example found for {method.upper()} {path}"
        resp = requests.post(url, json=request_example)
    else:
        pytest.skip(f"Method {method.upper()} not supported for endpoint {url}")

    # Accept any documented response code as valid
    assert resp.status_code in all_response_codes, (
        f"Endpoint {method.upper()} {url} returned {resp.status_code}. "
        f"Expected one of {all_response_codes}. "
        f"Request: {request_example}. "
        f"Response: {resp.text}"
    )

    # If we got a 200 response, validate it matches the expected structure
    if resp.status_code == 200:
        actual_response = resp.json()
        # Check that all required fields from the schema are present in the response
        if isinstance(response_example, dict) and required_response_fields:
            for field in required_response_fields:
                assert (
                    field in actual_response
                ), f"Required field '{field}' not found in response. "

    # For POST requests, test that removing each REQUIRED field results in 422
    if (
        method == "post"
        and request_example
        and isinstance(request_example, dict)
        and required_request_fields
    ):
        for key in required_request_fields:
            # Only test required fields
            if key in request_example:
                # Create a copy with this key removed
                incomplete_request = {
                    k: v for k, v in request_example.items() if k != key
                }
                resp_incomplete = requests.post(url, json=incomplete_request)
                assert resp_incomplete.status_code == 422, (
                    f"Expected 422 when required field '{key}' is missing from POST {url}. "
                    f"Got {resp_incomplete.status_code}. Response: {resp_incomplete.text}"
                )
