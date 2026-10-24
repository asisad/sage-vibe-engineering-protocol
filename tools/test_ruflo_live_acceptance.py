#!/usr/bin/env python3
"""Offline regression coverage for the Ruflo coding acceptance verifier."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

VERIFIER=pathlib.Path(__file__).resolve().parents[1]/"tools"/"verify_ruflo_live_acceptance.py"

class AcceptanceTests(unittest.TestCase):
    def check_suite(self, tests):
        with tempfile.TemporaryDirectory() as d:
            base=pathlib.Path(d)
            root=base/"workspace"
            (root/"src").mkdir(parents=True)
            (root/"tests").mkdir()
            (root/"src/__init__.py").write_text("")
            target=root/"src/calc.py"
            target.write_text("def add(a,b): return a-b\n")
            baseline=hashlib.sha256(target.read_bytes()).hexdigest()
            target.write_text("def add(a,b): return a+b\n")
            (root/"tests/test_calc.py").write_text(tests)
            output=base/"receipt.json"
            p=subprocess.run([sys.executable,str(VERIFIER),"--workspace",str(root),
                "--task-id","ruflo.fixture.002","--engine","direct","--baseline",baseline,
                "--output",str(output)],capture_output=True,text=True,timeout=50)
            return p.returncode,json.loads(output.read_text())

    def test_empty_suite_is_not_acceptance(self):
        code,receipt=self.check_suite("# no tests\n")
        self.assertNotEqual(code,0)
        self.assertFalse(receipt["verified"])

    def test_all_skipped_is_not_acceptance(self):
        code,receipt=self.check_suite('import unittest\n@unittest.skip("not run")\n'
            'class T(unittest.TestCase):\n def test_skip(self): pass\n')
        self.assertNotEqual(code,0)
        self.assertFalse(receipt["verified"])

    def test_executed_success_and_skip_are_accepted(self):
        code,receipt=self.check_suite('import unittest\nfrom src.calc import add\n'
            'class T(unittest.TestCase):\n def test_sum(self): self.assertEqual(add(2,3),5)\n'
            ' @unittest.skip("optional")\n def test_optional(self): pass\n')
        self.assertEqual(code,0,receipt)
        self.assertTrue(receipt["verified"])
        self.assertEqual(receipt["checks"]["tests_executed"],1)

    def test_executed_failure_cannot_pass(self):
        code,receipt=self.check_suite('import unittest\nfrom src.calc import add\n'
            'class T(unittest.TestCase):\n def test_failure(self): self.assertEqual(add(2,3),6)\n')
        self.assertNotEqual(code,0)
        self.assertFalse(receipt["verified"])

    def test_unchanged_and_fixed_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            base=pathlib.Path(d)
            root=base/"workspace"
            (root/"src").mkdir(parents=True)
            (root/"tests").mkdir()
            (root/"src"/"__init__.py").write_text("")
            target=root/"src"/"calc.py"
            target.write_text("def add(a, b):\n    return a - b\n")
            (root/"tests"/"test_calc.py").write_text(
                "import unittest\nfrom src.calc import add\n"
                "class TestAdd(unittest.TestCase):\n"
                "    def test_sum(self):\n        self.assertEqual(add(2, 3), 5)\n")
            baseline=hashlib.sha256(target.read_bytes()).hexdigest()
            out=base/"result.json"
            def verify():
                p=subprocess.run([sys.executable,str(VERIFIER),"--workspace",str(root),
                    "--task-id","ruflo.fixture.001","--engine","ruflo",
                    "--baseline",baseline,"--output",str(out)],capture_output=True,text=True)
                return p.returncode,json.loads(out.read_text())
            code,result=verify()
            self.assertEqual(code,1)
            self.assertEqual(result["status"],"FAIL")
            target.write_text("def add(a, b):\n    return a + b\n")
            code,result=verify()
            self.assertEqual(code,0,result)
            self.assertEqual(result["status"],"PASS")
            self.assertTrue(result["verified"])

if __name__=="__main__":
    unittest.main()
