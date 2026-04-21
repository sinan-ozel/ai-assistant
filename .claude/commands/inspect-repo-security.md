---
allowed-tools: Bash(git *), Bash(grep *), Bash(find *), Read, Write, Read(!**/.env) Read(!**/*.pem), Read(!**/*.key), Read(!**/*.p12)
---

Inpect all of the repo for security issues.

First read _SECURITY_INSPECTION.md

Check for:
(1) PII: emails, phone numbers, SSNs, internal IPs, usernames hardcoded in source
(2) Secrets: API keys, tokens, passwords, connection strings
(3) .gitignore completeness: are .env*, *.pem, *.key, secrets/, etc. excluded?
(4) Any files that shouldn't be tracked (git ls-files)

Suggest specific changes with file paths and line numbers where possible.

Write a timestamped report to _SECURITY_INSPECTION.md (append, don't overwrite).
Ensure _SECURITY_INSPECTION.md is listed in .gitignore.