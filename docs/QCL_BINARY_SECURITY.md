# QCL binary security

The repository contains legacy QCL 0.6.4 ELF binaries and build objects. Their
original upstream provenance, reproducible build process, and signature have not
been independently verified. They must therefore be treated as untrusted native
code.

`bin/qcl` verifies the repository-recorded SHA-256 and blocks execution by
default. The opt-in environment variable is a risk acknowledgement, not proof of
safety:

```bash
QCL_ALLOW_UNVERIFIED_BINARY=1 bin/qcl quantum_languages/qcl/example.qcl
```

Use the opt-in only in a disposable, non-privileged environment without secrets,
personal data, host mounts, or unnecessary network access. Do not use it in CI
or production.

Future releases must rebuild QCL from an authenticated source in isolated CI,
publish an SBOM and provenance attestation, and compare the result with an
independently documented upstream checksum before removing this quarantine.
