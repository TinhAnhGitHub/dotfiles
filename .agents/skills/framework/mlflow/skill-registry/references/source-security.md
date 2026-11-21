# Skill Registry sources, credentials, and trust

## Source types and credentials

| Source | Credentials | Immutability guidance |
|---|---|---|
| Local folder | Caller's filesystem access | Upload content is stored as MLflow artifacts |
| Git | Caller's Git credentials | Pin `ref` to a commit or tag, not a moving branch |
| OCI | Image/container credentials | Prefer a digest tag over `latest` |
| ZIP | None (URL must be public) | Use an immutable, versioned URL |

External content is fetched **by the client** using the pulling user's credentials.
A registry `READ` permission does not grant access to the underlying Git or OCI
source, and a source that was readable at registration time may later become
private or change.

## Digest verification

Registered external sources carry a content digest. Digest verification protects
registered content from silent drift. Low-level `MlflowClient` registrations may
omit a digest, which disables verification — prefer the high-level
`mlflow.genai.register_skill()` / `import_skills()` APIs and assert the expected
digest in CI when the source is security-sensitive.

```python
import mlflow

version = mlflow.genai.register_skill(
    source="https://github.com/acme/agent-skills.git",
    organization="acme",
    status="active",
)
assert version.digest, "registration omitted a content digest"
```

## Permissions

Workspace permissions are `READ`, `EDIT`, and `MANAGE`. Organization names do not
grant access by themselves. Registry approval is not code-safety approval: a
skill's supporting scripts may execute if an agent chooses to run them. Review
pulled files before installing them into an agent harness.

## Trust checklist

1. Pin an immutable source (commit, digest, or versioned ZIP).
2. Confirm a digest is present and matches the approved content.
3. Review `SKILL.md` and every referenced script for network calls, credential
   access, and destructive commands.
4. Install into a scoped directory for the intended harness only.
5. Record the resolved version/alias in release evidence; never use bare `latest`.
