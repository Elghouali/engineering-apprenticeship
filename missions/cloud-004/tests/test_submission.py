"""Public test contract for Terraform plan JSON safety and drift."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
SUBMISSION=Path(os.environ.get("APPRENTICE_SUBMISSION_PATH",
                  str(ROOT/"submissions/cloud-004/plan_guard.py")))

def entry(address, actions, resource_type="terraform_data", after=None):
    return {"address":address,"type":resource_type,
            "change":{"actions":actions,"after": after or {}}}

class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing cloud-004 submission")
        spec=importlib.util.spec_from_file_location("cloud004",SUBMISSION)
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        cls.mod=mod

    def report(self,changes=None,drift=None):
        return self.mod.assess_plan({"format_version":"1.2",
                                     "resource_changes":changes or [],
                                     "resource_drift":drift or []})

    def test_safe_create_is_approved(self):
        self.assertEqual(self.report([entry("terraform_data.sample",["create"])]),
                         {"decision":"approve","reasons":[],
                          "destructive_resources":[],"drift_resources":[]})

    def test_deletion_and_both_replacement_orders_block(self):
        changes=[
            entry("aws_db_instance.primary",["delete","create"]),
            entry("aws_instance.legacy",["create","delete"]),
            entry("aws_s3_bucket.old",["delete"]),
        ]
        self.assertEqual(self.report(changes),{
            "decision":"block","reasons":["destructive_change"],
            "destructive_resources": sorted(x["address"] for x in changes),
            "drift_resources":[]})

    def test_drift_requires_review_but_not_deletion(self):
        drift=[entry("aws_s3_bucket.finance",["update"])]
        self.assertEqual(self.report([],drift),{
            "decision":"review","reasons":["unmanaged_drift"],
            "destructive_resources":[],"drift_resources":["aws_s3_bucket.finance"]})

    def test_public_ssh_rule_blocks(self):
        rule={"from_port":22,"to_port":22,"protocol":"tcp",
              "cidr_blocks":["0.0.0.0/0"]}
        changes=[entry("aws_security_group.web",["update"],
                       "aws_security_group",{"ingress":[rule]})]
        got=self.report(changes)
        self.assertEqual(got["decision"],"block")
        self.assertEqual(got["reasons"],["public_ssh"])
        self.assertEqual(got["destructive_resources"],[])

    def test_safe_non_ssh_port_and_internal_source(self):
        ingress=[
            {"from_port":443,"to_port":443,"protocol":"tcp",
             "cidr_blocks":["0.0.0.0/0"]},
            {"from_port":22,"to_port":22,"protocol":"tcp",
             "cidr_blocks":["10.0.0.0/8"]},
        ]
        result=self.report([entry("aws_security_group.web",["update"],
                                  "aws_security_group",{"ingress":ingress})])
        self.assertEqual(result["decision"],"approve")

    def test_multiple_risks_sorted_and_priority(self):
        changes=[entry("aws_db_instance.db",["delete"]),
                 entry("aws_security_group.ssh",["create"],
                       "aws_security_group",{"ingress":[{
                           "from_port":0,"to_port":65535,"protocol":"-1",
                           "cidr_blocks":["0.0.0.0/0"]}]})]
        result=self.report(changes,[entry("aws_s3_bucket.bucket",["update"])])
        self.assertEqual(result["decision"],"block")
        self.assertEqual(result["reasons"],
                         ["destructive_change","public_ssh","unmanaged_drift"])
        self.assertEqual(result["drift_resources"],["aws_s3_bucket.bucket"])

    def test_bad_json_contract_is_rejected(self):
        for plan in [{}, {"format_version":"1.2"},
                     {"format_version":"1.2","resource_changes":{}},
                     {"format_version":"2.0","resource_changes":[]},
                     {"format_version":"1.2","resource_changes":[{
                         "address":"x","change":{"actions":["launch"]}}]}]:
            with self.subTest(plan=plan):
                with self.assertRaisesRegex(ValueError,"invalid_plan"):
                    self.mod.assess_plan(plan)

if __name__=="__main__":
    unittest.main()
