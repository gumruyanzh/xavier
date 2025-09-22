# Xavier Framework Changelog

All notable changes to Xavier Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.10] - 2025-09-22

### Fixed
- **Critical Sub-Agent Distribution Issue**: Fixed issue where users were not receiving native Claude Code sub-agents
  - Root cause: update.sh and install.sh were not copying new agent files from repository
  - Users updating to v1.1.9 were not getting the promised native Claude Code sub-agents
  - Install script was creating outdated agent definitions instead of native ones
  - Enhanced update.sh to copy agent files directly from downloaded repository
  - Enhanced install.sh to copy native agent files during installation

### Added
- **Native Claude Code Sub-Agent Distribution**: Both new installations and updates now properly distribute:
  - project-manager.md with YAML front matter and comprehensive prompts
  - python-engineer.md with TDD expertise and detailed constraints
  - golang-engineer.md with microservices and performance focus
  - frontend-engineer.md with React/TypeScript and accessibility standards
  - context-manager.md with codebase analysis capabilities
  - test-runner.md with 100% coverage enforcement

### Technical
- Fixed repository file copying in both installation and update workflows
- Removed outdated agent creation logic that was overriding native agents
- Ensured proper YAML front matter and tool specifications are distributed
- Verified both git clone and archive download structures work correctly

### Impact
This critical fix ensures that ALL users (both new and updating) receive the complete native Claude Code sub-agent functionality introduced in v1.1.8, providing the specialized development teams as intended.

## [1.1.9] - 2025-09-22

### Fixed
- **Critical Version Detection Bug**: Fixed issue where `xavier-update` command showed outdated version information
  - Users running `xavier-update` were seeing "version 1.1.5" despite version 1.1.8+ being available
  - Root cause: Missing VERSION file in user project directories
  - Update script now creates VERSION file after successful updates
  - Install script now creates VERSION file during initial installation
  - Ensures accurate version detection for future updates

### Technical
- Enhanced update.sh to create VERSION file after successful framework updates
- Enhanced install.sh to create VERSION file during initial installation
- Fixed version detection priority to work correctly with newly created VERSION files
- Prevents users from seeing incorrect "up to date" messages when newer versions are available

### Impact
This critical fix ensures that the xavier-update command works correctly for all users, providing accurate version information and enabling proper framework updates.

## [1.1.8] - 2025-09-22

### Added
- **Native Claude Code Sub-Agent Integration**:
  - Implemented proper `.claude/agents/` directory structure for native sub-agent support
  - Created specialized agent definitions for project management, development, and testing
  - Each agent runs in isolated context with dedicated expertise and tool access
  - Automatic agent selection and delegation based on task requirements

### Enhanced
- **Professional Agent Specializations**:
  - Project Manager: Sprint planning, story estimation, roadmap management
  - Context Manager: Codebase analysis, dependency tracking, architecture insights
  - Python Engineer: TDD, Clean Code, Django/FastAPI development
  - Golang Engineer: Microservices, concurrency, performance optimization
  - Frontend Engineer: React/TypeScript, accessibility, responsive design
  - Test Runner: Quality assurance, 100% coverage enforcement

### Improved
- **Developer Experience**: Native Claude Code agent visualization and identification
- **Task Delegation**: Intelligent agent selection based on task complexity and requirements
- **Context Management**: Isolated agent contexts prevent cross-contamination
- **Quality Standards**: Each agent enforces framework-specific best practices

### Technical
- Markdown-based agent definitions with YAML front matter
- Tool access control and permission management per agent
- Model selection optimization (Haiku/Sonnet/Opus) based on task complexity
- Seamless integration with Claude Code's native orchestration system

### Impact
This release transforms Xavier Framework into a true multi-agent development environment, providing specialized expertise for each aspect of software development while maintaining the framework's commitment to quality and test-first development.

## [1.1.7] - 2025-09-21

### Added
- **Enhanced Agent Visualization System**:
  - Visual agent identification with distinct colors, emojis, and labels for each agent type
  - Bordered output boxes with timestamps and real-time status indicators
  - Clear handoff transitions between agents showing delegation flow
  - Thinking indicators displaying agent processing states
  - Professional terminal display with improved readability

### Improved
- **Developer Experience**: Clearer visibility of agent operations during development
- **Agent Communication**: Enhanced visual feedback for multi-agent coordination
- **Terminal Output**: Professional, structured display of agent activities
- **Status Tracking**: Real-time updates on agent progress and task completion

### Technical
- YAML-based agent metadata system for consistent styling and information
- AgentBoxDrawing class for enhanced terminal visualization
- Metadata-driven color schemes and emojis for agent identification
- Standardized display functions across all agent types

### Impact
These enhancements significantly improve the developer experience by providing clear visual feedback about which agents are working on what tasks, making multi-agent development workflows much more transparent and easier to follow.

## [1.1.6] - 2025-09-21

### Fixed
- **Story ID Uniqueness**: Resolved duplicate story ID generation issue
  - Added `_generate_unique_story_id()` with collision detection and retry logic
  - Implements fallback mechanism for extremely rare UUID collisions
  - Ensures no two stories can have the same ID, preventing user confusion

### Added
- **Automatic Data Structure Initialization**:
  - Creates all required JSON files on SCRUM manager startup
  - Initializes: stories.json, tasks.json, bugs.json, sprints.json, epics.json, roadmaps.json
  - Preserves existing data when files already exist
  - Provides consistent data directory structure for all users

- **Automatic Roadmap Generation**:
  - Roadmap automatically created when creating new project via `/create-project`
  - Includes 4 default milestone templates (MVP Foundation, Core Features Complete, Beta Release, Production Launch)
  - Timeline spans 16 weeks with realistic development phases
  - Vision derived from project description
  - Saves to roadmaps.json immediately with proper persistence

### Improved
- **Data Persistence**: Enhanced data directory management with automatic file creation
- **User Experience**: Streamlined project setup process with automatic roadmap
- **Test Coverage**: Added comprehensive tests for unique ID generation, data initialization, and roadmap creation
- **Documentation**: Updated user guides to reflect automatic roadmap feature

### Impact
These updates address key user feedback about duplicate story IDs and missing roadmap files. The framework now provides a more robust and user-friendly experience with automatic setup and guaranteed unique identifiers.

## [1.1.5] - 2025-09-19

### Fixed
- **Complete Sprint Management Dictionary Issues**: Fixed all sprint-related dict/dataclass mismatches
  - `plan_sprint()` now uses safe accessors for all story/task/bug attributes
  - `_calculate_velocity()` handles both SprintStatus enum and string values
  - `start_sprint()` uses safe accessors for all sprint item updates
  - `update_task_progress()` and `_update_story_progress()` use safe accessors
  - `_update_sprint_burndown()` safely accesses all sprint/story/bug attributes
  - `complete_sprint()` handles both enum and string status values
  - Fixed datetime comparison in velocity calculation (string vs datetime)

### Added
- **Sprint Status Compatibility Helper**: `get_sprint_status_value()` for consistent status handling
  - Works with both SprintStatus enum and string values
  - Used throughout xavier_commands.py for reliable sprint status checks
- **Comprehensive Sprint Tests**: Full test coverage for sprint operations
  - Tests create/plan/start/complete sprint lifecycle
  - Tests mixed dict/dataclass format handling
  - Tests velocity calculation with various data formats
  - Tests sprint burndown calculations

### Updated
- **xavier_commands.py Sprint Methods**: All sprint commands use safe accessors
  - `create_sprint` command properly accesses sprint attributes
  - `start_sprint` command handles status checking correctly
  - Fixed planned sprint detection to work with both data formats

### Impact
This completes the enterprise-grade persistence solution. All sprint operations now work flawlessly with both dictionary and dataclass formats, ensuring 100% backward compatibility while maintaining type safety.

## [1.1.4] - 2025-09-19

### Fixed
- **Critical Data Persistence Bug**: Fixed fundamental dataclass/dictionary mismatch
  - Data models were defined as dataclasses but stored/loaded as plain dictionaries
  - Caused AttributeError when accessing loaded data (e.g., story.status, story.story_points)
  - Affected all SCRUM operations: stories, tasks, bugs, sprints, epics

### Added
- **Proper Serialization/Deserialization**: Complete data persistence solution
  - Added `serialize_dataclass()` and `deserialize_to_dataclass()` utilities
  - Handles datetime conversion between objects and ISO strings
  - Supports enum serialization for SprintStatus
- **Compatibility Layer**: Safe attribute access for mixed data types
  - `safe_get_attr()` works with both dataclass instances and dictionaries
  - `safe_set_attr()` provides unified interface for modifications
  - Ensures backward compatibility with existing data
- **Comprehensive Unit Tests**: Full test coverage for persistence
  - Tests for serialization/deserialization
  - Tests for compatibility layer
  - Tests for backward compatibility with old JSON format
  - End-to-end persistence tests

### Technical Details
- Fixed `_load_data()` to properly convert JSON to dataclass instances
- Fixed `_save_data()` to properly serialize dataclasses to JSON
- Updated all attribute access in `scrum_manager.py` to use compatibility helpers
- Updated `xavier_commands.py` methods for safe attribute access
- Maintains backward compatibility with projects using old dictionary format

### Impact
This fix resolves critical issues reported by partners where Xavier would crash with AttributeError when loading saved data. All SCRUM operations now work correctly with persisted data.

## [1.1.3] - 2025-09-19

### Fixed
- **Critical Update Script Bug**: Fixed command extraction failing when Xavier downloaded as archive
  - Update script now properly detects install.sh location for both git clone and archive download
  - Commands properly extracted regardless of download method
  - Added verbose output showing which commands are being updated

### Added
- **fix-commands.sh**: Quick fix script for users affected by 1.1.2 update issue
  - Manually installs estimate-story and set-story-points commands
  - Can be run without full Xavier update
  - Validates Xavier version before applying fix

## [1.1.2] - 2025-09-19

### Added
- **Claude Code Integration**: Complete integration of new story estimation commands
  - `/estimate-story` command now properly registered in Claude Code
  - `/set-story-points` command available as slash command
  - Both commands added to xavier_bridge.py command mapping
  - Commands automatically available after Xavier update

### Fixed
- Claude Code command registration for new estimation features
- Update script now properly installs new commands
- Xavier bridge command mapping includes all new commands

### Documentation
- Updated all command documentation files
- Added examples for both estimate-story and set-story-points
- Clear distinction between automatic and manual estimation

## [1.1.1] - 2025-09-19

### Added
- **Automatic Story Estimation Command**: `/estimate-story` now uses PM agent for intelligent estimation
  - Comprehensive complexity analysis algorithm
  - Batch estimation for entire backlog
  - Specific story estimation with story ID
  - Force re-estimation with --all flag

### Changed
- Renamed `/estimate-story` to `/set-story-points` for manual point setting
- Enhanced PM agent with sophisticated scoring system

### Improved
- PM agent analyzes technical complexity, CRUD operations, UI/UX requirements
- Complexity scores map to Fibonacci story points
- Visual feedback shows PM agent working with colored display

## [1.1.0] - 2025-09-19

### Added
- **Automatic Story Estimation**: New `/estimate-story` command uses PM agent to analyze and estimate story points
  - Analyzes technical complexity, acceptance criteria, UI/UX, and testing requirements
  - PM agent uses comprehensive scoring algorithm mapping to Fibonacci points
  - Batch estimation for entire backlog or specific stories
  - Visual feedback with colored PM agent display
- **Colored Agent System**: Professional visual feedback showing which agent is working
  - Each agent type has unique color, emoji, and short label (e.g., [PY] 🐍 PythonEngineer)
  - Agent takeover displays with colored boxes when agents start tasks
  - Real-time status updates with icons (⚙️ Working, 🧪 Testing, ✅ Completed)
  - Visual agent handoffs showing transitions between specialists
  - Sprint execution with colored progress indicators
- **Agent Visual Features**:
  - 9 distinct agent types with custom colors and emojis
  - Agent status tracking throughout task lifecycle
  - Clear TDD process visualization (Testing → Working → Complete)
  - Colored error messages and success indicators
- **Enhanced Orchestrator**:
  - Visual task delegation with agent identification
  - Sprint progress tracking with task counters
  - Agent handoff notifications with reasons

### Changed
- **Renamed Command**: `/estimate-story` renamed to `/set-story-points` for manual point setting
- `/estimate-story` now triggers automatic PM agent estimation
- `base_agent.py` enhanced with colored output methods
- `orchestrator.py` updated with visual feedback and handoff tracking
- All agents now announce themselves when taking over tasks
- Sprint execution shows clear visual progress

### Technical
- Added `AgentColors` class in `ansi_art.py` with agent color mappings
- New display functions: `display_agent_takeover()`, `display_agent_status()`, `display_agent_handoff()`, `display_agent_result()`
- Integration with existing ANSI color system
- Test script `test_colored_agents.py` for demonstration

## [1.0.3] - 2025-09-19

### Added
- **Beautiful ANSI Art System**: Professional ASCII art displays throughout the framework
  - XAVIER logo in block-style ASCII art similar to Claude Code
  - Light cyan/white color scheme for consistent branding
  - Welcome screens, sprint announcements, and update notifications
  - Responsive terminal width detection
- **Greeting Display System**: Multiple greeting types for various occasions
  - Welcome greeting with quick start commands
  - Sprint start/end announcements
  - Daily tips and update notifications
  - Mini banner for compact displays
- **Visual Feedback**: Enhanced user experience with visual cues
  - Installation success screen with organized command list
  - Update completion screen with changelog highlights
  - Sprint status displays with progress indicators

### Changed
- Installation script now features professional ANSI art banner
- Update script displays enhanced visual feedback with version comparison
- Commands like `/xavier-help` and `/start-sprint` now include visual elements
- Version updated to 1.0.3 across all components

### Technical
- Added `xavier/src/utils/ansi_art.py` utility module for Python-based displays
- Created `xavier/src/utils/greeting.sh` for flexible bash-based greetings
- Integrated ANSI art with command system
- Fallback support when bash is unavailable

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