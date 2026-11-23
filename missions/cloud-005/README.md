# CLOUD-005 — Finance reports bucket has excessive IAM privileges

**Atlas Retail | Cloud Security Engineer | Prerequisites: CLOUD-002, CLOUD-004**

## Incident
The analytics reporting service received s3:* on all resources. A compromised service could delete or read unrelated objects. Your task is to create a tightly scoped identity-policy document for one report prefix.

## Required function
Implement build_least_privilege_policy(bucket: str, prefix: str) -> dict in submissions/cloud-005/policy.py.

- Validate bucket as a lower-case DNS-style string of 3–63 characters using letters, digits, dot or hyphen (first/last must be alphanumeric); reject wildcard, uppercase, empty or malformed bucket.
- Validate prefix as 1+ slash-delimited path segments of lowercase ASCII letters, digits, underscore or hyphen (may have a trailing slash), no empty/dot/dot-dot/parent segments.
- Invalid input raises ValueError("invalid_policy_scope").
- Return Version "2012-10-17" and exactly two Allow statements:
  1. ListBucket on arn:aws:s3:::BUCKET conditioned by StringLike s3:prefix = [PREFIX + "/", PREFIX + "/*"] (ordered as shown).
  2. GetObject and PutObject on arn:aws:s3:::BUCKET/PREFIX/*.
- No wildcard Action, Resource "*", DeleteObject, or broad access to other buckets.
- Bucket/prefix are case-sensitive and must be preserved exactly except for removing one optional trailing slash.

This is a small teaching contract for the shape of an AWS IAM identity policy, **not** a replacement for AWS IAM evaluation, resource policies, SCPs, KMS permissions or IAM Access Analyzer.

## Review evidence
Provide a before/after policy diff, describe least privilege, separate ListBucket vs object-level ARNs, identity vs resource-based policy, conditions, and what needs testing via actual AWS policy simulation in a controlled account. **Do not provision cloud resources.**

Post-launch local commands:
    python tools/apprentice.py start cloud-005
    python tools/apprentice.py check cloud-005

**Status: prototype.** Official references: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html


## Maintainer validation evidence

The public contract has a correct implementation in a separate private repository and passes Linux/Windows tests. See [Cloud sprint evidence](../../docs/CLOUD_SPRINT_EVIDENCE.md).

These are static policy-structure checks only. AWS IAM policy simulation, identity/resource policy interplay, organization controls and cloud permission evaluation were not performed.
