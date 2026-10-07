---
name: hr-release-readiness
description: Use when preparing CI, container image publishing, or a versioned HR system release.
---

# HR release readiness

1. Read PROGRESS.md and docs/releasing.md. Do not equate image publishing with production readiness.
2. Verify the same lint, type, and offline test commands used by CI inside the Dev Container.
3. Build the production Dockerfile separately; the Dev Container is not the release image.
4. Check that runtime imports are declared as runtime dependencies, not only dev extras.
5. Keep secrets, local HR documents, vector databases, and development tools out of the build context.
6. Ensure release publishing depends on successful validation and uses minimal GitHub token permissions.
7. Obtain explicit approval before version bumps, tags, registry publication, or cloud deployment.
8. After an approved tag, inspect the Actions run and record the published image digest.
9. Roll back by digest, not by assuming a moving tag still points to the previous image.

Never tag v1.0.0 until the documented release checklist is satisfied.
