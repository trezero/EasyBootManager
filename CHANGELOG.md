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
- **Diagnostic logging system with comprehensive operation tracking**
- **Boot session detection and correlation**
- **Windows Event Log collection for boot-related events**
- **Diagnostics viewer GUI with timeline and correlation analysis**
- **Log export functionality for troubleshooting support**
- **Boot mismatch detection and diagnosis**
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
- **LogManager class with rotating file handlers (10MB, 3 backups)**
- **BootSessionTracker class for boot session detection (last 5 sessions)**
- **WindowsEventLogCollector class for event log gathering**
- **DiagnosticsViewer class for log viewing and analysis**
- Clean separation of concerns with modular architecture
- Metadata storage in JSON format
- **Structured logging in JSON Lines format**
- **Boot session correlation with operation tracking**
- Backups stored in %LOCALAPPDATA%\PyBootManager\backups\
- **Logs stored in %LOCALAPPDATA%\PyBootManager\logs\**

### Dependencies
- **psutil>=5.9.0** - For system boot time detection

### Documentation
- Comprehensive README with installation and usage instructions
- Product Requirements Document (PRD) with detailed specifications
- **DIAGNOSTICS_GUIDE.md - Complete troubleshooting guide**
- **Updated QUICKSTART.md with diagnostics use cases**
- MIT License
- Helper batch script for running as administrator
- CHANGELOG for version tracking

### Features Detail

#### Diagnostic Logging
- All user actions logged with context
- All bcdedit operations logged with command, args, return code, stdout, stderr
- Backup/restore operations tracked
- Application lifecycle events recorded
- Error logging with full stack traces
- Operation IDs for correlation

#### Boot Session Tracking
- Automatic detection of new boot sessions
- Tracks last 5 boot sessions
- Correlates operations with subsequent boots
- Identifies actual vs expected boot entry
- Flags mismatches with diagnostic messages
- Supports mismatch analysis for troubleshooting

#### Windows Event Log Collection
- Collects boot-related Event IDs (12, 13, 27, 41, 1001, 6005, 6006, 6008, 6009)
- Stores events per boot session
- Graceful handling of permission errors
- Automatic cleanup (keeps last 5 sessions)

#### Diagnostics Viewer
- Three-tab interface: Operation Logs, Event Logs, Timeline
- Boot session selector (last 5 sessions)
- Category filtering (USER_ACTION, BCD_OPERATION, BACKUP_OPERATION, ERROR)
- Detailed log entry viewer with JSON details
- Timeline view showing operation → boot correlation
- Mismatch highlighting with color-coded status
- Export all diagnostics to ZIP file for support

### Bug Fixes
- None (initial release)

### Known Issues
- Windows Event Log collection requires read permissions (gracefully degrades if unavailable)
- Fast Startup on Windows can interfere with "Boot Once" functionality (documented in diagnostics guide)
