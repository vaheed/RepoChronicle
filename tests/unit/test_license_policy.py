from scripts.check_licenses import license_failures


def test_license_policy_accepts_common_spdx_psf_identifier() -> None:
    packages = [{"Name": "typing_extensions", "Version": "4.16.0", "License": "PSF-2.0"}]
    assert license_failures(packages) == []


def test_license_policy_corrects_only_reviewed_missing_metadata_version() -> None:
    assert license_failures(
        [{"Name": "py_rust_stemmers", "Version": "0.1.8", "License": "UNKNOWN"}]
    ) == []
    failures = license_failures(
        [{"Name": "py_rust_stemmers", "Version": "0.1.9", "License": "UNKNOWN"}]
    )
    assert len(failures) == 1
    assert "disallowed/unknown license" in failures[0]
