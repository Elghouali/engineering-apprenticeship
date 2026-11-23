"""CLOUD-005 intentionally overly permissive S3 IAM policy."""
def build_least_privilege_policy(bucket: str, prefix: str) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*",
        }]
    }
