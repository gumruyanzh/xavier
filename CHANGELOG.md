# Xavier Framework Changelog

All notable changes to Xavier Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-09-19

### Added
- **Update System**: New `/xavier-update` command for checking and installing updates
- **Update Script**: Standalone `update.sh` script for updating existing installations
- **Version Tracking**: VERSION file for consistent version management
- **Backup System**: Automatic backup of user data before updates
- **Installation Detection**: Install script now detects existing Xavier installations

### Changed
- Install script now offers update option when Xavier is already installed
- Version updated to 1.0.2 across all components
- Enhanced command documentation with update instructions

### Fixed
- Installation script now properly detects and handles existing installations

## [1.0.1] - 2025-09-19

### Added
- **Intelligent Project Creation**: `/create-project` command with AI-powered analysis
  - Automatic tech stack detection and suggestion
  - Feature detection from project descriptions
  - Auto-generation of initial stories and epics
  - Project templates for common architectures
- **Strict Command Boundaries**: Prevents automatic implementation
  - Commands now strictly separate planning from implementation
  - Only `/start-sprint` triggers actual coding
  - Clear warnings and instructions in all command documentation
- **Enhanced Documentation**: Rich examples in `/xavier-help`
  - JSON examples for all commands
  - Categorized command listing
  - Quick tips and best practices

### Changed
- Commands now explicitly state they don't implement (except `/start-sprint`)
- Updated all command documentation with DO and DON'T lists
- Framework version updated to track releases
- Improved help command with detailed examples

### Fixed
- Xavier website design issues (CSS/JavaScript loading)
- Command boundaries to prevent premature implementation
- Website domain configuration for gumruyan.com/xavier

## [1.0.0] - 2025-09-19

### Initial Release
- **Core Framework**: Enterprise SCRUM development for Claude Code
- **Test-First Development**: Enforced TDD with 100% coverage requirement
- **Clean Code Standards**: Function ≤20 lines, classes ≤200 lines
- **Sequential Execution**: One task at a time, no parallel work
- **SOLID Principles**: All code must follow SOLID design patterns
- **Agent System**: Specialized agents with strict language boundaries
  - Project Manager Agent
  - Context Manager Agent
  - Python Engineer Agent
  - Golang Engineer Agent
  - Frontend Engineer Agent
  - DevOps Agent
- **SCRUM Commands**:
  - `/create-story`: Create user stories with acceptance criteria
  - `/create-task`: Create tasks under stories
  - `/create-bug`: Report bugs with reproduction steps
  - `/create-sprint`: Plan sprints with auto-planning
  - `/start-sprint`: Begin sprint execution
  - `/show-backlog`: View prioritized backlog
  - `/xavier-help`: Show all commands
- **Data Persistence**: Stories, tasks, bugs, and sprints saved locally
- **GitHub Pages Documentation**: Professional documentation site
- **Installation Script**: Easy one-line installation
- **Claude Code Integration**: Custom commands and instructions

## Migration Guide

### From 1.0.0/1.0.1 to 1.0.2

1. Run the update command:
   ```bash
   curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/update.sh | bash
   ```
   Or use: `/xavier-update`

2. Your data is automatically backed up to `.xavier/backups/`

3. New features available:
   - Use `/create-project` for intelligent project setup
   - Use `/xavier-update` to check for future updates
   - Commands now have strict boundaries (no auto-implementation)

### First Installation

For new users, install Xavier with:
```bash
curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/install.sh | bash
```

## Support

- GitHub Issues: https://github.com/gumruyanzh/xavier/issues
- Documentation: https://gumruyan.com/xavier
- License: MIT