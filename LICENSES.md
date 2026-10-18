# Third-Party Notices

RepoChronicle does not vendor third-party source code or model weights in this foundation starter. Runtime dependencies are installed from their package/container sources and are governed by their own licenses, notices and terms.

See `docs/DEPENDENCY_INVENTORY.md` and `docs/LICENSE_POLICY.md`. Before redistributing a built image or release:
- record exact resolved Python package versions/licenses;
- generate an SBOM;
- record container base-image and OS package licenses;
- record the exact model/embedding revisions and their terms;
- include required third-party notices;
- rerun security and license checks.

Do not infer that the RepoChronicle Apache-2.0 license applies to third-party libraries, data, models, or remote APIs.
