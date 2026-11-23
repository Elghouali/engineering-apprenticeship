# Security Policy

This pre-release academy intentionally contains faulty exercise starter code; these synthetic bugs are not deployed production vulnerabilities.

## Reporting

Do not disclose real secrets, private data or a working exploit against a real account in a public GitHub Issue. Use GitHub private vulnerability reporting / security advisories if the maintainer has enabled them. Otherwise request a private contact route without posting exploit details.

## Important boundaries

- The local grading command executes learner-supplied Python. Treat submissions as untrusted code.
- Never run another person's submission on a device with cloud credentials, production files, SSH agent credentials or privileged tokens.
- GitHub Actions uses read-only repository permissions with no intended cloud secrets, but hosted runners alone do not prove secure isolation against malicious submissions.
- Do not add pull_request_target workflows executing user-controlled code.
- Do not host arbitrary code execution or deploy cloud services as part of the initial academy.
- Use synthetic fixtures only.

Before public promotion, review dependency versions, workflow permissions, a private reporting channel and approved licenses. See [Launch Gate](docs/PUBLIC_LAUNCH.md).
