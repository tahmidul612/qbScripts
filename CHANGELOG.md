# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added

- Initial project setup with uv
- Core module structure
- Basic dependency management

## v0.3.0 (2025-10-29)

### Feat

- improve UI output with clearer explanations and better formatting
- add map bounds fitting in screenshot generation
- add spinner for VPN data fetch and persistent IP geolocation cache
- add batch geolocation with fallback providers and improved UI
- add HTML to PNG rendering option for map generation

### Fix

- improve map screenshot rendering by hiding zoom controls and adjusting max zoom level
- resolve Chrome timeout issue in PNG rendering with containerized environment flags
- add missing newline for better readability in README
- implement persistent disk-based cache for city geocoding
- prevent duplicate progress bar prints and add parallel city geocoding with timeout
- remove verbose IP output from progress bar and disable slow geocoding

### Refactor

- replace subprocess browser calls with Playwright for PNG rendering
- move subprocess import to top of test file

## v0.2.0 (2025-10-22)

### BREAKING CHANGE

- Initial release

### Feat

- implement qBittorrent peer clustering and VPN recommendations
- **cli**: add initial main.py entrypoint

### Fix

- update ProtonVPN API endpoint to huzky-v repository
- correct spelling of 'qBittorrent' in README.md
