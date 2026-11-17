#!/usr/bin/env python3
"""Offline, bounded checker for a narrow environment-placeholder subset."""
from __future__ import annotations

import json
import re
import sys
from typing import Any

MAX_INPUT = 256 * 1024
MAX_VALUE = 4096
MAX_ITEMS = 64
MAX_NAMES = 128
MAX_OCCURRENCES = 4096
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}")
_NAME_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class Invalid(Exception):
    def __init__(self, code: str) -> None:
        self.code = code


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Invalid("duplicate_key")
        result[key] = value
    return result


def _bad_constant(_: str) -> None:
    raise Invalid("invalid_json")


def _names(value: Any) -> set[str]:
    if not isinstance(value, list) or len(value) > MAX_NAMES:
        raise Invalid("invalid_shape")
    result: set[str] = set()
    for name in value:
        if not isinstance(name, str) or not _NAME.fullmatch(name) or name in result:
            raise Invalid("invalid_names")
        result.add(name)
    return result


def _scan(text: str, declared: set[str], ambient: set[str], ordinal: int, out: list[dict[str, Any]]) -> None:
    i = 0
    while i < len(text):
        if text.startswith("${", i):
            end = text.find("}", i + 2)
            if end < 0:
                raise Invalid("unsupported_placeholder")
            body = text[i + 2:end]
            if "${" in body:
                raise Invalid("unsupported_placeholder")
            if ":-" in body:
                name, _fallback = body.split(":-", 1)
                has_fallback = True
            else:
                name, has_fallback = body, False
            if not _NAME.fullmatch(name):
                raise Invalid("unsupported_placeholder")
            source = "declared" if name in declared else "ambient" if name in ambient else "fallback" if has_fallback else "missing"
            out.append({"ordinal": ordinal, "name": name, "source": source})
            i = end + 1
        elif text[i] == "$":
            match = _NAME_TOKEN.match(text, i + 1)
            if match:
                name = match.group(0)
                if len(name) > 128:
                    raise Invalid("unsupported_placeholder")
                source = "declared" if name in declared else "ambient" if name in ambient else "missing"
                out.append({"ordinal": ordinal, "name": name, "source": source})
                i = match.end()
            else:
                i += 1
        else:
            i += 1
        if len(out) > MAX_OCCURRENCES:
            raise Invalid("too_many_references")


def _evaluate(doc: Any) -> dict[str, Any]:
    if not isinstance(doc, dict) or set(doc) != {"values", "declared_names", "ambient_names"}:
        raise Invalid("invalid_shape")
    values = doc["values"]
    if not isinstance(values, list) or not 1 <= len(values) <= MAX_ITEMS:
        raise Invalid("invalid_shape")
    for value in values:
        if not isinstance(value, str) or len(value) > MAX_VALUE:
            raise Invalid("invalid_value")
    declared = _names(doc["declared_names"])
    ambient = _names(doc["ambient_names"])
    occurrences: list[dict[str, Any]] = []
    for ordinal, value in enumerate(values, 1):
        _scan(value, declared, ambient, ordinal, occurrences)
    return {"references": occurrences}


def main() -> int:
    try:
        data = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(data) > MAX_INPUT:
            raise Invalid("input_too_large")
        try:
            doc = json.loads(data.decode("utf-8", errors="strict"), object_pairs_hook=_pairs_no_duplicates, parse_constant=_bad_constant)
        except Invalid:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
            raise Invalid("invalid_json") from None
        output = _evaluate(doc)
        code = 1 if any(item["source"] == "missing" for item in output["references"]) else 0
    except Invalid as exc:
        output, code = {"error": exc.code}, 2
    except OSError:
        output, code = {"error": "io_error"}, 2
    encoded = json.dumps(output, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii") + b"\n"
    sys.stdout.buffer.write(encoded)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
