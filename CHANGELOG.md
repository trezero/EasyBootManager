# Changelog

All notable changes to PyBootManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-23

### Added
- Initial release of PyBootManager
- Boot entry detection for Windows Boot Manager
- One-time boot selection (boot once)
- Default boot OS configuration
- Boot menu timeout adjustment (0-999 seconds)
- Automatic backup before all configuration changes
- Manual backup creation with custom names
- Backup restoration with selection dialog
- Backup viewer showing all available backups
- Modern GUI built with tkinter
- Administrator privilege checking and elevation
- Comprehensive error handling and user feedback
- Status bar for operation feedback
- Confirmation dialogs for dangerous operations
- Support for both UEFI and Legacy BIOS boot modes

### Technical Details
- BCDManager class for Windows Boot Manager interaction
- BackupManager class for backup/restore operations
- PrivilegeManager class for admin privilege handling
- Clean separation of concerns with modular architecture
- Metadata storage in JSON format
- Backups stored in %LOCALAPPDATA%\PyBootManager\backups\

### Documentation
- Comprehensive README with installation and usage instructions
- Product Requirements Document (PRD) with detailed specifications
- MIT License
- Helper batch script for running as administrator
- CHANGELOG for version tracking
