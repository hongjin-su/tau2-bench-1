# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0](https://github.com/sierra-research/tau2-bench/compare/v0.2.0...v0.3.0) (2025-12-01)


### Features

* **experiment:** Add hyperparam sweep experimental code ([#77](https://github.com/sierra-research/tau2-bench/issues/77)) ([558e6cd](https://github.com/sierra-research/tau2-bench/commit/558e6cd066d7bf05db587fa2dc1509765c7d03bc))
* **gym:** add Gymnasium-compatible interface for RL training ([0ed2fd8](https://github.com/sierra-research/tau2-bench/commit/0ed2fd8d830a20657d89ae9c2efcc94838aa7129))


### Bug Fixes

* add missing gymnasium dependency ([#91](https://github.com/sierra-research/tau2-bench/issues/91)) ([a969a0c](https://github.com/sierra-research/tau2-bench/commit/a969a0c0a29bc47ba8580107932f5298ee636045))
* communicate_info fixed to nl_assertions in Mock domain tasks ([#66](https://github.com/sierra-research/tau2-bench/issues/66)) ([702ee77](https://github.com/sierra-research/tau2-bench/commit/702ee77e497d89e9d8942ab7206c1a465b12e503))

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.1] - 2025-11-07
### Added
- Gymnasium-compatible interface for RL training with `AgentGymEnv` and `UserGymEnv`
- Train/test task splits for all domains
- Interactive play mode (`tau2 play`) supporting both agent and user roles
- Possibility to strictly enforce communication protocol rules (e.g., no mixed messages with text and tool calls)

## [0.2.0] - 2025-10-06

### Added
- Web-based leaderboard system with interactive submission management
- GitHub Pages deployment for leaderboard with automated CI/CD
- Comprehensive submission validation and verification system
- Model comparison interface with performance metrics visualization
- Trajectory visualization in web interface
- Mobile-responsive leaderboard design
- Logo assets and branding for multiple LLM providers
- Live leaderboard deployment at tau-bench.com

### Changed
- Enhanced submission manifest structure
- Improved image handling and asset management
- Updated deployment workflow for better reliability

### Fixed
- Mobile view responsiveness issues
- Missing submissions from manifest
- Image path resolution for GitHub Pages deployment
- Base URL handling for subdirectory deployment

## [0.1.3] - 2025-08-26

### Fixed
- LLM arguments parsing and handling
- Removed default natural language assertion checks that were causing issues

## [0.1.2] - 2025-07-17

### Added
- `tau2 check-data` CLI command for verifying data directory setup
- Support for `TAU2_DATA_DIR` environment variable for non-editable installs
- Fallback to local source when data directory is not set
- `--num-tasks` CLI flag for limiting task count

### Changed
- Made `pip install -e .` the default installation method
- Improved task name display in CLI
- Enhanced data directory configuration flexibility

### Fixed
- Installation issues with data directory discovery
- Task filtering and display problems

## [0.1.1] - 2025-06-12

### Fixed
- Domain viewer CLI functionality
- `tau2 domain` command execution issues

## [0.1.0] - 2025-06-12

### Added
- Initial release of τ²-bench framework
- Support for multiple domains: mock, airline, retail, telecom
- Command-line interface with `tau2` command
- Agent evaluation system with LLM integration via LiteLLM
- User simulator for realistic conversation scenarios
- Environment system with domain-specific tools and policies
- Orchestration system for managing agent-user-environment interactions
- Comprehensive test suite
- Domain-specific documentation and API endpoints
- Experimental features: no-user mode, oracle-plan mode, workflow policies
- Support for ablation studies
- Interactive environment CLI for testing and debugging
- Caching system for LLM calls (Redis-based)
- Multi-trial evaluation with concurrent execution support

### Technical Details
- Python 3.10+ support
- FastAPI-based web services
- Pydantic data models
- Rich CLI with tabulated output
- Comprehensive logging with Loguru
- Performance metrics and visualization
- Configurable LLM backends
- Semantic versioning adoption

## Links
- [Repository](https://github.com/sierra-research/tau2-bench)
- [Leaderboard](https://tau-bench.com)
- [Paper](https://arxiv.org/abs/2506.07982)
- [Blog Post](https://sierra.ai/blog/benchmarking-agents-in-collaborative-real-world-scenarios)
