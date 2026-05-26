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

The script reads the version from `pyproject.toml` and the current value of `build_number.txt` to produce a tag like `0.1.0-dev.12`. It builds and pushes the Docker image and creates a git tag (`v0.1.0-dev.12`), but does **not** increment `build_number.txt` — that is the Helm chart publish step's responsibility.

## Dev release (Helm chart)

From VS Code: **Tasks: Run Task** → **Publish Helm Chart (Dev)**

From the terminal:

```bash
bash scripts/publish-helm-chart.sh --dev
```

### Build number resolution

Rather than trusting `build_number.txt` blindly, the script derives the next build number from two sources of truth:

1. **Git tags** — scans `v{VERSION}-dev.*` and extracts the highest N
2. **Docker Hub** — queries the public tags API and extracts the highest M for `{VERSION}-dev.*`

The new build number is `max(N, M + 1)`. This guarantees the Helm chart never reuses a build number already claimed by a Docker image or a prior git tag, even if `build_number.txt` is stale.

After a successful push, `build_number.txt` is set to `NEW_BUILD + 1` and committed.

### Combined Docker + Helm dev release

Run **Release (Dev)** first, then **Publish Helm Chart (Dev)**. Because the Docker step does not increment `build_number.txt`, the Helm step will see the Docker image in the Hub API and select `docker_build + 1` as the next number — keeping them on separate, non-colliding build numbers by design.

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
