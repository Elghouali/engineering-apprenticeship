"""Public IAM S3 prefix scope contract: no external cloud account."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
SUBMISSION=Path(os.environ.get("APPRENTICE_SUBMISSION_PATH",
                      str(ROOT/"submissions/cloud-005/policy.py")))

class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing cloud-005 submission")
        spec=importlib.util.spec_from_file_location("cloud005",SUBMISSION)
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        cls.mod=mod

    def test_exact_least_privilege_and_conditions(self):
        policy=self.mod.build_least_privilege_policy("atlas-finance-reports",
                                                     "daily/2026/")
        self.assertEqual(policy, {
            "Version":"2012-10-17",
            "Statement":[
                {"Effect":"Allow","Action":["s3:ListBucket"],
                 "Resource":"arn:aws:s3:::atlas-finance-reports",
                 "Condition":{"StringLike":{
                     "s3:prefix":["daily/2026/","daily/2026/*"]}}},
                {"Effect":"Allow","Action":["s3:GetObject","s3:PutObject"],
                 "Resource":"arn:aws:s3:::atlas-finance-reports/daily/2026/*"},
            ]
        })

    def test_bucket_and_prefix_retarget(self):
        got=self.mod.build_least_privilege_policy("reports-123","team-a")
        self.assertEqual(got["Statement"][0]["Resource"],
                         "arn:aws:s3:::reports-123")
        self.assertEqual(got["Statement"][0]["Condition"]["StringLike"]["s3:prefix"],
                         ["team-a/","team-a/*"])
        self.assertEqual(got["Statement"][1]["Resource"],
                         "arn:aws:s3:::reports-123/team-a/*")

    def test_denied_wildcard_or_destructive_permissions(self):
        policy=self.mod.build_least_privilege_policy("reports-123","finance")
        serialized=str(policy)
        for forbidden in ("s3:*","DeleteObject","'Resource': '*'",
                          "arn:aws:s3:::*"):
            self.assertNotIn(forbidden,serialized)

    def test_reject_unsafe_scopes(self):
        for bucket,prefix in [
            ("","daily"), ("ABCD","daily"), ("a","daily"),
            ("abc*","daily"), ("-bucket","daily"),
            ("abc",""), ("abc","../root"), ("abc","a//b"),
            ("abc","a/../b"), ("abc","a b"), ("abc","/a"),
            ("abc","a/*"), ("abc","./a"),
        ]:
            with self.subTest(bucket=bucket,prefix=prefix):
                with self.assertRaisesRegex(ValueError,"invalid_policy_scope"):
                    self.mod.build_least_privilege_policy(bucket,prefix)

if __name__=="__main__":
    unittest.main()
