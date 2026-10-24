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
