# Xavier Framework Version Update Checklist

This checklist ensures all necessary updates are made when releasing a new version of Xavier Framework.

## Pre-Release Checklist

### 1. Code Updates
- [ ] Update version number in `/xavier/VERSION`
- [ ] Update version in `/xavier/src/commands/xavier_commands.py` (line with `version = "x.x.x"`)
- [ ] Update version in `/xavier/src/utils/greeting.sh` (default VERSION variable)
- [ ] Update version in `/xavier/src/utils/ansi_art.py` (display_welcome function default)
- [ ] Update CHANGELOG.md with version details

### 2. Test Coverage
- [ ] Run all unit tests: `python -m pytest xavier/tests/`
- [ ] Verify persistence tests pass
- [ ] Verify sprint tests pass
- [ ] Ensure 100% test coverage

### 3. Installation/Update Scripts
- [ ] Test install.sh with fresh installation
- [ ] Test update.sh from previous version
- [ ] Verify Claude Code commands are properly registered
- [ ] Test fix-commands.sh if applicable

## Documentation Updates (REQUIRED)

### 4. Website Documentation - docs/
**IMPORTANT: Always update website documentation when changing versions!**

- [ ] **index.html**
  - [ ] Update version number (line ~34)
  - [ ] Update "What's New" section if major features added

- [ ] **documentation.html**
  - [ ] Update version in info box (line ~67)
  - [ ] Add new features to relevant sections

- [ ] **quick-start.html**
  - [ ] Update "Current Version" in info box (line ~209)
  - [ ] Update "Latest Features" list

- [ ] **changelog.html**
  - [ ] Add new version section at the top
  - [ ] Move "LATEST" badge to new version
  - [ ] Include all changes: fixes, features, improvements
  - [ ] Add migration notes if breaking changes

### 5. GitHub Pages
- [ ] Verify website deploys correctly to GitHub Pages
- [ ] Test all navigation links
- [ ] Verify changelog displays correctly
- [ ] Check responsive design on mobile

## Release Process

### 6. Git Operations
- [ ] Commit all changes with descriptive message
- [ ] Tag release: `git tag v1.x.x`
- [ ] Push to main: `git push origin main`
- [ ] Push tags: `git push origin --tags`

### 7. GitHub Release
- [ ] Create GitHub release from tag
- [ ] Copy relevant changelog section to release notes
- [ ] Attach any binary artifacts if needed
- [ ] Mark as latest release

## Post-Release Verification

### 8. Installation Testing
- [ ] Test fresh install: `curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/install.sh | bash`
- [ ] Test update: `/xavier-update`
- [ ] Verify all commands work in Claude Code
- [ ] Test creating story, task, sprint
- [ ] Verify persistence works correctly

### 9. Documentation Verification
- [ ] Visit https://gumruyan.com/xavier (or your GitHub Pages URL)
- [ ] Verify version displays correctly
- [ ] Check changelog shows new version
- [ ] Test all documentation links

## Common Issues to Check

- [ ] Dict/dataclass compatibility (use safe accessors)
- [ ] Sprint status enum vs string handling
- [ ] DateTime serialization in persistence
- [ ] Command registration in Claude Code
- [ ] Update script path detection

## Notes

- Always test with both fresh installations and updates from previous versions
- Pay special attention to backward compatibility
- Website documentation must ALWAYS be updated with version changes
- Use semantic versioning: MAJOR.MINOR.PATCH
  - MAJOR: Breaking changes
  - MINOR: New features (backward compatible)
  - PATCH: Bug fixes

## Version History Reference

- 1.0.0: Initial release
- 1.0.1: Minor improvements
- 1.0.2: Project creation, update system
- 1.0.3: ANSI art system
- 1.1.0: Colored agents
- 1.1.1: Auto estimation
- 1.1.2: Claude Code integration
- 1.1.3: Update script fix
- 1.1.4: Persistence fix
- 1.1.5: Sprint management fix

---
Remember: Documentation updates are NOT optional - they are a critical part of every release!