from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "mcp_env_preflight.py"


def run_cli(raw: bytes) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, str(SCRIPT)], input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT, check=False)


class CliTests(unittest.TestCase):
    def invoke(self, doc: object) -> subprocess.CompletedProcess[bytes]:
        return run_cli(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))

    def test_checked_in_example_exact_output(self) -> None:
        result = run_cli((ROOT / "fixtures" / "example.json").read_bytes())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b'{"references":[{"name":"API_TOKEN","ordinal":1,"source":"declared"},{"name":"CACHE_DIR","ordinal":1,"source":"ambient"},{"name":"OPTIONAL","ordinal":2,"source":"fallback"}]}\n')
        self.assertEqual(result.stderr, b"")

    def test_missing_required_reference_exit_one(self) -> None:
        result = self.invoke({"values": ["${MISSING}"], "declared_names": [], "ambient_names": []})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b'{"references":[{"name":"MISSING","ordinal":1,"source":"missing"}]}\n')

    def test_declared_precedes_ambient_and_forms_and_empty_fallback(self) -> None:
        result = self.invoke({"values": ["$X ${X} $Y ${Z:-}"], "declared_names": ["X"], "ambient_names": ["X", "Y"]})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {"references": [
            {"name": "X", "ordinal": 1, "source": "declared"},
            {"name": "X", "ordinal": 1, "source": "declared"},
            {"name": "Y", "ordinal": 1, "source": "ambient"},
            {"name": "Z", "ordinal": 1, "source": "fallback"},
        ]})

    def test_value_order_is_preserved(self) -> None:
        result = self.invoke({"values": ["$B", "${A}"], "declared_names": ["A", "B"], "ambient_names": []})
        self.assertEqual(json.loads(result.stdout)["references"], [
            {"name": "B", "ordinal": 1, "source": "declared"},
            {"name": "A", "ordinal": 2, "source": "declared"},
        ])

    def test_config_and_fallback_are_not_echoed(self) -> None:
        sentinel = "NEVER_ECHO_THIS_SECRET"
        result = self.invoke({"values": [f"prefix-{sentinel}-${{MISSING:-{sentinel}}}"], "declared_names": [], "ambient_names": []})
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(sentinel.encode(), result.stdout)
        self.assertEqual(json.loads(result.stdout)["references"][0]["source"], "fallback")

    def test_dollar_non_placeholder_is_literal_but_bad_braces_rejected(self) -> None:
        literal = self.invoke({"values": ["$ and $9 and $$"], "declared_names": [], "ambient_names": []})
        self.assertEqual(literal.returncode, 0)
        self.assertEqual(literal.stdout, b'{"references":[]}\n')
        bad = self.invoke({"values": ["${bad-name}"], "declared_names": [], "ambient_names": []})
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, b'{"error":"unsupported_placeholder"}\n')

    def test_unbraced_name_over_128_chars_is_rejected_as_a_whole(self) -> None:
        prefix = "A" * 128
        result = self.invoke({"values": ["$" + prefix + "A"], "declared_names": [prefix], "ambient_names": []})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'{"error":"unsupported_placeholder"}\n')

    def test_rejects_malformed_and_nested_braced_placeholders(self) -> None:
        for value in ("${UNCLOSED", "${1BAD}", "${A:-${B}}", "${A:+x}"):
            with self.subTest(value=value):
                result = self.invoke({"values": [value], "declared_names": [], "ambient_names": []})
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b'{"error":"unsupported_placeholder"}\n')

    def test_rejects_invalid_json_duplicate_keys_and_utf8(self) -> None:
        samples = ((b"{", b'{"error":"invalid_json"}\n'), (b'{"values":[],"values":[],"declared_names":[],"ambient_names":[]}', b'{"error":"duplicate_key"}\n'), (b"\xff", b'{"error":"invalid_json"}\n'))
        for raw, expected in samples:
            with self.subTest(raw=raw):
                result = run_cli(raw)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, expected)

    def test_shape_and_names_validation(self) -> None:
        cases = [
            {"values": ["$A"], "declared_names": [], "ambient_names": [], "extra": 1},
            {"values": [], "declared_names": [], "ambient_names": []},
            {"values": ["$A"], "declared_names": ["1BAD"], "ambient_names": []},
            {"values": ["$A"], "declared_names": ["A", "A"], "ambient_names": []},
            {"values": ["$A"], "declared_names": [], "ambient_names": ["A" * 129]},
        ]
        for doc in cases:
            with self.subTest(doc=doc):
                result = self.invoke(doc)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stdout.startswith(b'{"error":'))

    def test_size_and_occurrence_limits(self) -> None:
        too_long = self.invoke({"values": ["x" * 4097], "declared_names": [], "ambient_names": []})
        self.assertEqual(too_long.returncode, 2)
        self.assertEqual(too_long.stdout, b'{"error":"invalid_value"}\n')
        too_many = self.invoke({"values": ["$A" * 2048, "$A" * 2048, "$A" * 2048], "declared_names": ["A"], "ambient_names": []})
        self.assertEqual(too_many.returncode, 2)
        self.assertEqual(too_many.stdout, b'{"error":"too_many_references"}\n')
        oversized = run_cli(b" " * (256 * 1024 + 1))
        self.assertEqual(oversized.returncode, 2)
        self.assertEqual(oversized.stdout, b'{"error":"input_too_large"}\n')

    def test_bad_root_and_entry_types(self) -> None:
        for doc in ([], {"values": [None], "declared_names": [], "ambient_names": []}, {"values": ["$A"], "declared_names": None, "ambient_names": []}):
            self.assertEqual(self.invoke(doc).returncode, 2)


if __name__ == "__main__":
    unittest.main()

