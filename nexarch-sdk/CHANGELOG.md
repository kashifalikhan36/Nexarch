# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-17

### Changed
- Reorganized package structure from `SDK/python` to `nexarch-sdk/nexarch`
- Improved import path: now use `from nexarch import NexarchSDK`
- Updated package configuration in pyproject.toml

### Fixed
- Fixed incomplete README path in pyproject.toml
- Added thread-safe lock for architecture discovery
- Fixed potential KeyError when accessing span tags
- Added input validation for sampling_rate
- Improved error handling in database instrumentation
- Added better exception handling in loggers
- Fixed potential datetime parsing errors in span finish method

### Added
- Added LICENSE file (MIT)
- Added setup.py for better compatibility
- Added MANIFEST.in for package distribution
- Added py.typed marker for PEP 561 compliance
- Added comprehensive .gitignore
- Added CONTRIBUTING.md
- Added this CHANGELOG.md

## [0.1.0] - 2026-01-10

### Added
- Initial release of Nexarch SDK
- FastAPI middleware for automatic instrumentation
- Architecture auto-discovery
- Database instrumentation (SQLAlchemy, MongoDB, Redis)
- HTTP client instrumentation (requests, httpx)
- Local JSON logging
- HTTP export to backend
- Distributed tracing support
- Telemetry endpoints
