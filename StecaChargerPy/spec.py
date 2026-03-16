"""Parsing utilities for the Wallbox OpenAPI specification."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Sequence

import yaml

__all__ = [
    "ApiParameter",
    "ApiRequestBody",
    "ApiOperation",
    "ApiSpecification",
    "load_default_specification",
]


_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch"}


@dataclass(frozen=True, slots=True)
class ApiParameter:
    """Descriptor for path or query parameters defined in the OpenAPI spec."""

    name: str
    location: str
    required: bool
    schema: Mapping[str, Any]
    description: Optional[str] = None

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any]) -> "ApiParameter":
        return cls(
            name=raw["name"],
            location=raw.get("in", "query"),
            required=bool(raw.get("required")),
            schema=raw.get("schema", {}),
            description=raw.get("description"),
        )


@dataclass(frozen=True, slots=True)
class ApiRequestBody:
    """Request body metadata for an operation."""

    required: bool
    content_types: Sequence[str] = field(default_factory=tuple)
    json_schema: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True, slots=True)
class ApiOperation:
    """Parsed representation of an OpenAPI operation entry."""

    operation_id: str
    method: str
    path: str
    summary: Optional[str]
    description: Optional[str]
    parameters: Sequence[ApiParameter] = field(default_factory=tuple)
    request_body: Optional[ApiRequestBody] = None
    responses: Mapping[str, Any] = field(default_factory=dict)

    @property
    def path_parameters(self) -> List[ApiParameter]:
        return [param for param in self.parameters if param.location == "path"]

    @property
    def query_parameters(self) -> List[ApiParameter]:
        return [param for param in self.parameters if param.location == "query"]

    @property
    def success_status_codes(self) -> List[int]:
        codes: List[int] = []
        for status, _ in self.responses.items():
            if isinstance(status, str) and status.isdigit():
                status_code = int(status)
                if 200 <= status_code < 300:
                    codes.append(status_code)
        if not codes:
            # Fall back to the most common HTTP success codes
            codes = [200, 201, 202, 204]
        return codes


class ApiSpecification:
    """Wrapper around the OpenAPI document with convenient lookups."""

    def __init__(self, document: Mapping[str, Any], *, source: Optional[Path] = None) -> None:
        self._document = document
        self._source = source
        self._components = document.get("components", {})
        self._operations_by_id: Dict[str, ApiOperation] = {}
        self._parse()

    @classmethod
    def from_file(cls, path: Path | str) -> "ApiSpecification":
        file_path = Path(path)
        with file_path.open("r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        if not isinstance(document, MutableMapping):
            raise TypeError("OpenAPI document must be a mapping")
        return cls(document, source=file_path)

    @property
    def source(self) -> Optional[Path]:
        return self._source

    def _parse(self) -> None:
        paths = self._document.get("paths", {})
        if not isinstance(paths, Mapping):
            raise ValueError("OpenAPI document does not declare paths")

        for raw_path, operations in paths.items():
            if not isinstance(operations, Mapping):
                continue

            common_parameters = operations.get("parameters", [])
            if not isinstance(common_parameters, Iterable):
                common_parameters = []

            for method, operation in operations.items():
                if method not in _HTTP_METHODS:
                    continue
                if not isinstance(operation, Mapping):
                    continue
                operation_id = operation.get("operationId")
                if not operation_id:
                    # Skip undocumented operations
                    continue

                parameters = list(common_parameters)
                parameters.extend(operation.get("parameters", []) or [])

                parameter_objs = tuple(
                    self._build_parameter(param)
                    for param in parameters
                    if isinstance(param, Mapping)
                )

                request_body: Optional[ApiRequestBody] = None
                if "requestBody" in operation and isinstance(operation["requestBody"], Mapping):
                    request_body = self._parse_request_body(operation["requestBody"])

                responses = operation.get("responses", {})
                if not isinstance(responses, Mapping):
                    responses = {}

                api_operation = ApiOperation(
                    operation_id=operation_id,
                    method=method.upper(),
                    path=raw_path,
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    parameters=parameter_objs,
                    request_body=request_body,
                    responses=responses,
                )

                self._register_operation(api_operation)

    def _parse_request_body(self, request_body: Mapping[str, Any]) -> ApiRequestBody:
        required = bool(request_body.get("required"))
        content = request_body.get("content", {})
        content_types = tuple(content.keys()) if isinstance(content, Mapping) else tuple()

        json_schema: Optional[Mapping[str, Any]] = None
        if isinstance(content, Mapping):
            json_content = content.get("application/json")
            if isinstance(json_content, Mapping):
                schema = json_content.get("schema")
                if isinstance(schema, Mapping):
                    json_schema = schema

        return ApiRequestBody(
            required=required,
            content_types=content_types,
            json_schema=json_schema,
        )

    def _register_operation(self, operation: ApiOperation) -> None:
        operation_id = operation.operation_id
        if operation_id in self._operations_by_id:
            raise ValueError(f"Duplicate operationId detected: {operation_id}")
        self._operations_by_id[operation_id] = operation

    def get_operation(self, operation_id: str) -> ApiOperation:
        try:
            return self._operations_by_id[operation_id]
        except KeyError as exc:
            raise KeyError(f"Unknown operationId: {operation_id}") from exc

    def __iter__(self) -> Iterator[ApiOperation]:
        return iter(self._operations_by_id.values())

    def __len__(self) -> int:
        return len(self._operations_by_id)

    def _build_parameter(self, parameter: Mapping[str, Any]) -> ApiParameter:
        if "$ref" in parameter:
            resolved = self._resolve_reference(parameter["$ref"])
            if not isinstance(resolved, Mapping):
                raise TypeError(f"Referenced parameter is not a mapping: {parameter['$ref']}")
            return ApiParameter.from_raw(resolved)
        return ApiParameter.from_raw(parameter)

    def _resolve_reference(self, ref: str) -> Any:
        if not isinstance(ref, str) or not ref.startswith("#/"):
            raise ValueError(f"Unsupported $ref format: {ref!r}")

        parts = ref.lstrip("#/").split("/")
        node: Any = self._document
        for part in parts:
            if not isinstance(node, Mapping) or part not in node:
                raise KeyError(f"Unable to resolve reference: {ref}")
            node = node[part]
        return node


def load_default_specification() -> ApiSpecification:
    """Load the bundled OpenAPI specification from the repository.

    The helper looks up ``eSystemsWlwbRestApi.yaml`` relative to the package
    directory. Users may also load the specification manually via
    :meth:`ApiSpecification.from_file` when pointing to a different location.
    """

    package_dir = Path(__file__).resolve().parent
    candidate_paths = [
        package_dir / "data" / "eSystemsWlwbRestApi.yaml",
        package_dir.parent / "eSystemsWlwbRestApi.yaml",
    ]
    for path in candidate_paths:
        if path.exists():
            return ApiSpecification.from_file(path)
    raise FileNotFoundError(
        "Unable to locate eSystemsWlwbRestApi.yaml. Place the file next to the "
        "package or inside StecaChargerPy/data."
    )

