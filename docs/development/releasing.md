# Releasing

Releases are built and pushed using the **Release** VS Code task (or `bash release/release.sh <version>` directly).

## Prerequisites

- Logged in to Docker Hub: `docker login`
- On branch `main` with a clean working tree
- All integration tests passing

## Running a release

From VS Code: **Tasks: Run Task** → **Release**, then enter the version when prompted.

From the terminal:

```bash
bash release/release.sh 1.2.3
```

## What the release script does

1. Validates the version is valid semver (`MAJOR.MINOR.PATCH`)
2. Checks the version is not already a git tag
3. Checks the new version is strictly greater than the current latest tag
4. Verifies the working tree is clean
5. Verifies the current branch is `main`
6. Builds the Docker image with OCI annotations (`version`, `revision`, `created`)
7. Tags the git commit as `v<version>`
8. Pushes the Docker image as both `sinanozel/agent-stem:<version>` and `sinanozel/agent-stem:latest`
9. Pushes the git tag

## Versioning

Versions follow [Semantic Versioning](https://semver.org/):

- `MAJOR` — breaking changes to the `cortex/` API (provider YAML format, prompt DSL, workflow YAML)
- `MINOR` — new features, backward-compatible
- `PATCH` — bug fixes

## After the release

<!-- TODO: Release documentation (MkDocs site) at the same time as the image.
     Consider: mkdocs gh-deploy or publishing the site in CI alongside this step. -->

Documentation release is not yet automated. To publish the docs manually:

```bash
mkdocs gh-deploy
```

This is tracked as a TODO in `release/release.sh`.
