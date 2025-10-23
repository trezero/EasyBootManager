# PyBootManager
## Product Requirements Document
### A Python-Based Boot Manager for Windows

---

| **Version** | 1.0 |
|------------|-----|
| **Date** | October 23, 2025 |
| **Status** | Draft |

---

## 1. Executive Summary

PyBootManager is a lightweight, user-friendly Python application designed to simplify dual-boot and multi-boot management on Windows systems. The tool addresses a critical pain point for users who maintain multiple operating systems: the inability to select their boot OS without accessing the BIOS/UEFI boot menu during system startup.

By providing a Windows-based interface to configure the next boot OS, PyBootManager eliminates the need for display visibility during boot, making it ideal for users with monitor sync issues, headless setups, or those who simply want a more convenient boot selection method.

---

## 2. Problem Statement

### 2.1 Current Challenges

- Users with dual-boot systems must manually select their OS during boot by pressing function keys (F11, F12, ESC, etc.)
- Display synchronization issues can prevent users from seeing the boot menu
- Remote or headless systems cannot easily switch between operating systems
- Existing solutions like EasyBCD are commercial, closed-source, or have limited platform support
- Technical users need to understand BCD commands or GRUB configuration

### 2.2 Target Users

- Developers who maintain Windows and Linux environments
- IT professionals managing dual-boot workstations
- Enthusiasts and gamers with multiple OS configurations
- Anyone experiencing display issues during boot

---

## 3. Product Overview

### 3.1 Vision

PyBootManager aims to be the go-to open-source solution for boot management on Windows systems, providing a simple, reliable, and accessible way to manage multi-boot configurations without requiring deep technical knowledge or physical access to the boot menu.

### 3.2 Core Value Proposition

- **Simplicity:** Intuitive GUI requiring minimal technical knowledge
- **Reliability:** Safe operations with built-in backup and restore functionality
- **Accessibility:** Works without display visibility during boot
- **Open Source:** Free, transparent, and community-driven
- **Cross-Platform Bootloader Support:** Works with GRUB, Windows Boot Manager, and UEFI

---

## 4. User Stories

### Story 1: One-Time Boot Selection
*As a* developer with a Windows/Linux dual-boot setup, *I want to* select which OS boots next from within Windows *so that* I can switch to Linux without seeing the boot menu.

### Story 2: Default Boot OS Configuration
*As a* system administrator, *I want to* set a permanent default boot OS *so that* the system always boots into my preferred environment.

### Story 3: Boot Menu Timeout Configuration
*As a* power user, *I want to* adjust the boot menu timeout *so that* I have enough time to select an OS manually if needed.

### Story 4: Backup and Restore
*As a* cautious user, *I want to* backup my boot configuration before making changes *so that* I can recover if something goes wrong.

### Story 5: View Boot Entries
*As a* curious user, *I want to* see all available boot entries in my system *so that* I understand what operating systems are configured.

---

## 5. Functional Requirements

### 5.1 Core Features

#### FR1: Boot Entry Detection
1. System shall automatically detect all boot entries in Windows Boot Manager
2. System shall identify the current default boot entry
3. System shall display OS names, descriptions, and identifiers
4. System shall handle both UEFI and Legacy BIOS boot modes

#### FR2: Boot Configuration Management
1. System shall allow users to set the next boot OS (one-time boot)
2. System shall allow users to change the default boot OS (permanent)
3. System shall allow users to modify boot menu timeout (0-999 seconds)
4. System shall validate all changes before applying them

#### FR3: Backup and Recovery
1. System shall create automatic backups before any configuration change
2. System shall allow users to manually create named backups
3. System shall provide a list of available backups with timestamps
4. System shall allow users to restore from any backup

### 5.2 User Interface Requirements

- GUI shall use modern, native Windows styling (via tkinter or PyQt)
- Interface shall provide clear status messages and error notifications
- All dangerous operations shall require confirmation dialogs
- Application shall display current boot configuration prominently

### 5.3 Safety Features

- Require administrator privileges for all boot modifications
- Validate boot entry identifiers before making changes
- Create automatic backups before every configuration change
- Provide detailed error messages and recovery instructions

---

## 6. Technical Requirements

### 6.1 Platform Support

- **Operating System:** Windows 10 and Windows 11 (x64)
- **Python Version:** Python 3.8 or higher
- **Boot Modes:** UEFI and Legacy BIOS

### 6.2 Dependencies

| Library | Purpose |
|---------|---------|
| **subprocess** | Execute bcdedit commands |
| **tkinter / PyQt5** | GUI framework |
| **ctypes** | Windows API access for privilege elevation |
| **json** | Configuration and backup storage |
| **re** | Parse bcdedit output |

### 6.3 Core Components

#### BCDManager Class
Handles all interactions with Windows Boot Manager via bcdedit command-line utility.

- **Methods:** get_boot_entries(), set_default(), set_timeout(), get_current_default()
- **Key Feature:** Parse bcdedit output and convert to structured data

#### BackupManager Class
Manages boot configuration backups using bcdedit export/import functionality.

- **Methods:** create_backup(), restore_backup(), list_backups(), delete_backup()
- **Storage:** JSON metadata + binary BCD exports in AppData

#### PrivilegeManager Class
Ensures application runs with administrator privileges and requests elevation when needed.

- **Methods:** is_admin(), request_elevation()
- **Implementation:** Uses ctypes to call Windows ShellExecuteEx API

#### GUI Class
Main application window providing user interface for all features.

- **Components:** Boot entry list, action buttons, status bar, settings panel
- **Framework Options:** tkinter (lightweight) or PyQt5 (modern)

---

## 7. Non-Functional Requirements

### 7.1 Performance

- Boot entry detection shall complete within 2 seconds
- Configuration changes shall apply within 1 second
- Application startup time shall be under 3 seconds

### 7.2 Usability

- Application shall be usable by non-technical users
- All error messages shall be clear and actionable
- Help documentation shall be accessible from the application

### 7.3 Reliability

- System shall never leave boot configuration in an invalid state
- All operations shall be atomic (complete fully or not at all)
- Backup creation must succeed before any modification is attempted

### 7.4 Security

- Application shall require administrator privileges
- All bcdedit commands shall be properly sanitized
- Backup files shall be stored with restricted permissions

### 7.5 Maintainability

- Code shall follow PEP 8 Python style guidelines
- All functions shall have comprehensive docstrings
- Unit tests shall cover critical boot management functions
- Architecture shall support future extensions (GRUB support, etc.)

---

## 8. User Interface Design

### 8.1 Main Window Layout

```
┌──────────────────────────────────────────────────┐
│              PyBootManager                       │
├──────────────────────────────────────────────────┤
│         Current Configuration                    │
│  Default: Windows 11 | Timeout: 30 seconds      │
├──────────────────────────────────────────────────┤
│         Available Boot Entries                   │
│  [ ] Windows 11                                  │
│  [ ] Ubuntu 22.04 LTS                           │
│  [ ] Windows Recovery                           │
├──────────────────────────────────────────────────┤
│  [Boot Once] [Set Default] [Configure Timeout]  │
│  [Backup] [Restore]                             │
│                                                  │
│  Status: Ready                                   │
└──────────────────────────────────────────────────┘
```

### 8.2 Key UI Elements

- **Header:** Application title and version
- **Status Panel:** Current default OS and timeout settings
- **Boot Entry List:** Selectable list of all detected boot entries
- **Action Buttons:** Boot Once, Set Default, Configure Timeout, Backup, Restore
- **Status Bar:** Operation feedback and error messages

---

## 9. Technical Architecture

### 9.1 System Architecture Diagram

```
┌────────────────────────────────────────────────┐
│         Presentation Layer                     │
│  GUI (tkinter/PyQt5) | Event Handlers |       │
│  Input Validation                              │
├────────────────────────────────────────────────┤
│         Business Logic Layer                   │
│  BCDManager | BackupManager | PrivilegeManager│
│  ConfigValidator                               │
├────────────────────────────────────────────────┤
│         System Interface Layer                 │
│  subprocess (bcdedit) | ctypes (Windows API) | │
│  File I/O                                      │
├────────────────────────────────────────────────┤
│         Operating System                       │
│  Windows Boot Manager (BCD Store) |           │
│  Windows Registry | File System                │
└────────────────────────────────────────────────┘
```

### 9.2 Data Flow

1. **User Action:** User selects a boot entry and clicks an action button
2. **Validation:** GUI validates input and confirms with user
3. **Privilege Check:** PrivilegeManager verifies admin rights
4. **Backup:** BackupManager creates automatic backup
5. **Execution:** BCDManager executes bcdedit command
6. **Verification:** System verifies change was applied correctly
7. **Feedback:** GUI displays success or error message

---

## 10. Implementation Plan

### 10.1 Phase 1: Core Functionality (Weeks 1-2)

- Implement BCDManager class with boot entry detection
- Implement PrivilegeManager for admin rights
- Create basic command-line interface for testing
- Implement set_default() and set_timeout() methods

### 10.2 Phase 2: Backup System (Week 3)

- Implement BackupManager class
- Add automatic backup before modifications
- Implement restore functionality

### 10.3 Phase 3: GUI Development (Weeks 4-5)

- Design and implement main window layout
- Connect GUI to business logic layer
- Add confirmation dialogs and error handling
- Implement status bar and feedback mechanisms

### 10.4 Phase 4: Testing and Polish (Week 6)

- Write unit tests for critical functions
- Perform integration testing on various Windows configurations
- Create user documentation and help system
- Package application as executable (PyInstaller)

### 10.5 Phase 5: Release (Week 7)

- Create GitHub repository with proper documentation
- Publish v1.0 release with installer
- Gather user feedback for future iterations

---

## 11. Success Metrics

### 11.1 Quantitative Metrics

- **User Adoption:** 100+ GitHub stars within 3 months
- **Reliability:** Zero critical bugs reported after v1.0 release
- **Performance:** Boot detection completes in under 2 seconds
- **Code Quality:** 90%+ unit test coverage for core functions

### 11.2 Qualitative Metrics

- Users report the application is easy to use
- No user reports boot configuration corruption
- Positive community feedback and feature requests

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Boot corruption | Critical | Mandatory backups before all changes |
| Windows updates breaking bcdedit | Medium | Version checking and graceful degradation |
| Privilege escalation failures | Low | Clear error messages and instructions |
| Limited platform testing | Medium | Community beta testing program |

---

## 13. Future Enhancements

### 13.1 Version 2.0 Features

- Direct GRUB configuration support (edit grub.cfg)
- Remote boot management via network
- Scheduled boot switching (e.g., boot to Windows on weekdays)
- Custom boot entry creation for advanced users

### 13.2 Long-Term Vision

- Cross-platform support (Linux version for managing GRUB)
- Cloud backup synchronization
- Integration with system monitoring tools
- Mobile companion app for remote boot selection

---

## 14. Conclusion

PyBootManager represents a significant improvement in boot management usability for dual-boot Windows users. By eliminating the need for physical access to the boot menu and providing a reliable, user-friendly interface, this tool addresses a critical pain point in multi-OS workflows.

The open-source nature of the project ensures transparency, community involvement, and continuous improvement. With a focus on safety, reliability, and ease of use, PyBootManager has the potential to become the standard tool for Windows boot configuration management.

Development can begin immediately with a clear roadmap, well-defined requirements, and a commitment to user safety and satisfaction.