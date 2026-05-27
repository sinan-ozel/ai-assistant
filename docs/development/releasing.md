# Releasing

Releases are built and pushed using the **Release** VS Code task (or `bash scripts/release.sh <version>` directly).

## Prerequisites

- Logged in to Docker Hub: `docker login`
- On branch `main` with a clean working tree
- All integration tests passing

## Dev release (Docker image)

Used to publish a pre-release Docker image without going through the full production checklist.

From VS Code: **Tasks: Run Task** → **Release (Dev)**

From the terminal:

```bash
bash scripts/release.sh --dev
```

The script reads the version from `pyproject.toml` and the current value of `build_number.txt` to produce a tag like `0.1.0-dev.13`. It builds and pushes the Docker image, creates a git tag (`v0.1.0-dev.13`), then increments `build_number.txt` and commits.

### Build number invariants

| Thing | Source of truth |
|---|---|
| Latest Docker image | Most recent git tag (`git describe --tags`) |
| Latest Helm chart version | `build_number - 1` |
| Build currently in progress | `build_number` |

After a Docker release with build number N: `build_number.txt` is set to `N + 1`.

## Dev release (Helm chart)

From VS Code: **Tasks: Run Task** → **Publish Helm Chart (Dev)**

From the terminal:

```bash
bash scripts/publish-helm-chart.sh --dev
```

The script is a no-op if neither `helm/ai-assistant/` nor `scripts/publish-helm-chart.sh` has changed since the last git tag. When it does publish:

- **Chart version** — uses the current `build_number` value (e.g. `0.1.0-dev.14`)
- **appVersion** — set to the latest git tag (e.g. `0.1.0-dev.13`), so the chart deploys the Docker image that actually exists
- **build_number.txt** — incremented to `build_number + 1` and committed

After a Helm release with chart version N: `build_number - 1` resolves to that chart version.

## Production release

From VS Code: **Tasks: Run Task** → **Release**, then enter the version when prompted.

From the terminal:

```bash
bash scripts/release.sh
```

### What the production release script does

1. Validates the version is valid semver (`MAJOR.MINOR.PATCH`)
2. Checks the version is not already a git tag
3. Checks the new version is strictly greater than the current latest tag
4. Verifies the working tree is clean
5. Verifies the current branch is `main`
6. Builds the Docker image with OCI annotations (`version`, `revision`, `created`)
7. Tags the git commit as `v<version>`
8. Pushes the Docker image as both `sinanozel/ai-assistant:<version>` and `sinanozel/ai-assistant:latest`
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

This is tracked as a TODO in `scripts/release.sh`.
