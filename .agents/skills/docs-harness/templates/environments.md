# Environments — {{PROJECT}} · البيئات

> Variable NAMES only. A value in this file is a security incident.
> Values live in the secret store: <!-- FILL: which one -->

| Environment | Purpose | URL | Data | Who has access |
|---|---|---|---|---|
| local | development | — | seeded / fake | everyone |
| staging | <!-- --> | <!-- --> | anonymised | <!-- --> |
| production | live | <!-- --> | real | <!-- --> |

## Variables
| Name | Environments | Owner | Rotation |
|---|---|---|---|
| `<!-- NAME -->` | local, staging, prod | <!-- --> | <!-- --> |

## Rules · القواعد
- Secret VALUES MUST NOT appear in this repository, in a commit message, or in a debug script.
- `.env`, `*.pem`, `*.key`, and credential files MUST be git-ignored and agent-ignored.
- Production data MUST NOT be copied to a lower environment without anonymisation.
- يُمنع وضع أي قيمة سرية في المستودع أو في رسائل الالتزام أو في نصوص التشخيص.
