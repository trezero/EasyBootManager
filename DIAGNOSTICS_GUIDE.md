# PyBootManager Diagnostics Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Boot Sessions](#understanding-boot-sessions)
3. [Accessing Diagnostics](#accessing-diagnostics)
4. [Reading Diagnostic Logs](#reading-diagnostic-logs)
5. [Interpreting Boot Mismatches](#interpreting-boot-mismatches)
6. [Exporting Logs for Support](#exporting-logs-for-support)
7. [Common Issues and Solutions](#common-issues-and-solutions)

---

## Introduction

PyBootManager includes comprehensive diagnostic logging to help you troubleshoot boot configuration issues. The diagnostics system tracks:

- **User Actions**: Every button click and configuration change
- **BCD Operations**: All bcdedit commands executed with their results
- **Boot Sessions**: Detection and tracking of system boots
- **Windows Event Logs**: Boot-related system events
- **Operation Correlation**: Matching your actions with actual boot results

This guide will help you use these diagnostics to solve boot-related problems.

---

## Understanding Boot Sessions

### What is a Boot Session?

A **boot session** represents a single system boot. PyBootManager tracks the last 5 boot sessions and correlates them with operations you performed before the boot.

Each boot session includes:
- **Session ID**: Unique identifier with timestamp (e.g., `boot_20251023_090000`)
- **Boot Time**: When the system actually booted
- **Previous Operations**: Actions taken before this boot
- **Actual Boot Entry**: Which OS actually booted
- **Expected Boot Entry**: Which OS should have booted
- **Match Status**: Whether actual matched expected (MATCH, MISMATCH, or UNKNOWN)
- **Diagnosis**: Explanation if there was a mismatch

### Boot Session Detection

PyBootManager automatically detects new boot sessions when you launch the application by comparing the system's current boot time with the last recorded boot time.

---

## Accessing Diagnostics

### Opening the Diagnostics Viewer

1. Launch PyBootManager
2. Click the **"View Diagnostics"** button (teal/green color)
3. The Diagnostics window will open showing all available data

### Diagnostics Window Layout

The diagnostics window has three main areas:

1. **Left Panel**: Boot session selector (last 5 sessions)
2. **Top Panel**: Session information summary
3. **Right Panel**: Three tabs with detailed information
   - **Operation Logs**: All logged operations for the session
   - **Windows Event Logs**: System event logs related to booting
   - **Timeline & Correlation**: Visual timeline showing operation-to-boot correlation

---

## Reading Diagnostic Logs

### Operation Logs Tab

The Operation Logs tab shows all recorded operations for the selected boot session.

**Columns:**
- **Timestamp**: Exact date and time of the operation
- **Level**: Severity (INFO, ERROR)
- **Category**: Type of operation
  - `USER_ACTION`: Button clicks and user interactions
  - `BCD_OPERATION`: bcdedit commands
  - `BACKUP_OPERATION`: Backup create/restore operations
  - `ERROR`: Errors and exceptions
  - `APP_LIFECYCLE`: Application start/stop events
- **Message**: Description of what happened

**Filtering:**
Use the category dropdown to filter logs by type. This helps focus on specific types of operations.

**Details View:**
Click on any log entry to see detailed information in the bottom panel, including:
- Operation ID
- Full command details (for BCD operations)
- Error stack traces (for errors)
- Additional context data

### Windows Event Logs Tab

Shows Windows Event Log entries related to boot operations for the selected session.

**Important Event IDs:**
- **6005**: Event Log service started (boot completed)
- **6009**: System boot information
- **12**: Boot start
- **27**: Boot configuration change
- **41**: Unexpected shutdown (system crashed)
- **6008**: Previous unexpected shutdown detected

### Timeline & Correlation Tab

This tab provides a visual representation of:
1. **Previous Operations**: What you did before the boot
2. **Boot Result**: What actually happened when the system booted
3. **Match Status**: Whether your operation worked as expected
4. **Diagnosis**: Explanation if there was a problem

---

## Interpreting Boot Mismatches

### What is a Mismatch?

A **mismatch** occurs when:
- You used "Boot Once" to select an OS, but a different OS booted
- You changed the default OS, but the old default still boots

### Common Mismatch Causes

#### 1. Permission Issues
**Symptoms:**
- Operation log shows "access denied" in stderr
- BCD operation failed with return code 1

**Solution:**
- Ensure you're running PyBootManager as Administrator
- Right-click and "Run as Administrator"

#### 2. System Crash After Operation
**Symptoms:**
- Event Log shows Event ID 41 (unexpected shutdown)
- Boot sequence was cleared due to crash

**Explanation:**
When Windows crashes, the "boot once" setting may be cleared. The system will boot using the default entry instead.

**Solution:**
- Address the cause of the crash
- Use "Set Default" instead of "Boot Once" for more reliability

#### 3. UEFI Firmware Override
**Symptoms:**
- BCD operation succeeded
- No errors in logs
- But different OS booted anyway

**Explanation:**
Some UEFI firmware has its own boot override settings that take precedence over Windows BCD settings.

**Solution:**
- Check your UEFI/BIOS boot settings
- Disable any firmware-level boot overrides
- Ensure Windows Boot Manager is first in UEFI boot order

#### 4. Fast Startup Interference
**Symptoms:**
- Boot Once doesn't work
- System appears to boot directly to Windows

**Explanation:**
Windows Fast Startup (hybrid shutdown) can bypass the boot menu.

**Solution:**
1. Open Control Panel → Power Options
2. Click "Choose what the power buttons do"
3. Click "Change settings that are currently unavailable"
4. Uncheck "Turn on fast startup"
5. Save changes

---

## Exporting Logs for Support

If you need help troubleshooting an issue, you can export all diagnostic data to share with support or developers.

### How to Export

1. Open the Diagnostics Viewer
2. Click the **"Export All"** button in the left panel
3. Choose a location to save the ZIP file
4. The ZIP file includes:
   - All operation logs (operations.jsonl)
   - Application logs (application.log)
   - Boot session history (boot_sessions.json)
   - Windows Event Logs for each session
   - All supporting log files

### What Gets Exported

- **operations.jsonl**: Every logged operation in JSON Lines format
- **application.log**: General application log with rotating backups
- **boot_sessions.json**: Boot session tracking data
- **event_logs/**: Folder with Windows Event Logs per session

The exported ZIP typically contains the last 5 boot sessions worth of data.

---

## Common Issues and Solutions

### Issue: "Boot Once" Doesn't Work

**Diagnosis Steps:**
1. Open Diagnostics Viewer
2. Select the boot session after you used "Boot Once"
3. Go to Timeline & Correlation tab
4. Check the Match Status

**Possible Causes:**
- Permission denied → Run as Administrator
- System crash → Check Event Logs for Event ID 41
- Fast Startup enabled → Disable it
- UEFI override → Check firmware settings

### Issue: Default OS Changed Back

**Diagnosis Steps:**
1. Check Operation Logs for the "Set Default" operation
2. Look for return code in BCD operation details
3. Check for any ERROR level entries

**Possible Causes:**
- Operation failed → Check admin privileges
- Another tool changed it → Check for BCD operations you didn't make
- System restore → Check for restore operations

### Issue: Timeout Setting Not Applied

**Diagnosis Steps:**
1. Find the "Configure Timeout" operation in logs
2. Check BCD operation return code
3. Verify the timeout value in operation details

**Common Cause:**
- Permission denied → Requires Administrator

### Issue: Logs Not Being Created

**Symptoms:**
- Diagnostics Viewer shows no data
- "No boot sessions found" message

**Possible Causes:**
1. **psutil not installed**:
   ```bash
   pip install psutil>=5.9.0
   ```

2. **First run**: Logs accumulate over time. Perform some operations and reboot to generate data.

3. **Log directory permissions**: Check that PyBootManager can write to:
   ```
   %LOCALAPPDATA%\PyBootManager\logs\
   ```

---

## Log File Locations

All diagnostic data is stored in:
```
%LOCALAPPDATA%\PyBootManager\logs\
```

On a typical Windows system, this resolves to:
```
C:\Users\YourUsername\AppData\Local\PyBootManager\logs\
```

**Directory Structure:**
```
logs\
├── application.log          (10MB max, 3 rotating files)
├── operations.jsonl         (JSON Lines format, unlimited)
├── boot_sessions.json       (Last 5 sessions)
└── event_logs\
    ├── boot_20251023_090000.json
    ├── boot_20251023_140000.json
    └── ... (max 5 files)
```

---

## Advanced: Reading JSON Logs Directly

If you need to analyze logs programmatically, you can read the JSON files directly.

### operations.jsonl Format

Each line is a complete JSON object:

```json
{
  "timestamp": 1729707600.123,
  "log_level": "INFO",
  "category": "BCD_OPERATION",
  "operation_id": "op_20251023_104000_001",
  "boot_session_id": "boot_20251023_090000",
  "message": "bcdedit /bootsequence {uuid}",
  "details": {
    "command": "bcdedit",
    "args": ["/bootsequence", "{uuid}"],
    "returncode": 0,
    "stdout": "The operation completed successfully.",
    "stderr": ""
  }
}
```

### boot_sessions.json Format

```json
[
  {
    "session_id": "boot_20251023_090000",
    "boot_timestamp": 1729688400.0,
    "previous_operations": [
      {
        "operation_id": "op_20251022_180000_003",
        "operation_type": "BOOT_ONCE",
        "target_entry": "{ubuntu-guid}",
        "timestamp": 1729680000.0
      }
    ],
    "actual_boot_entry": "{windows-guid}",
    "expected_boot_entry": "{ubuntu-guid}",
    "boot_match_status": "MISMATCH",
    "diagnosis": "Boot once may have been cleared or system crashed | Check operation logs for permission errors"
  }
]
```

---

## Tips for Effective Troubleshooting

1. **Always check Operation Logs first**: Look for ERROR entries
2. **Verify return codes**: BCD operations should return 0 for success
3. **Check Event Logs for crashes**: Event ID 41 indicates unexpected shutdown
4. **Compare expected vs actual**: Timeline tab makes this easy
5. **Export and share**: When asking for help, export your diagnostics
6. **Keep logs clean**: Fresh boot sessions provide clearest data

---

## Need More Help?

If you've followed this guide and still have issues:

1. Export your diagnostic logs (as described above)
2. Note the specific boot session with the problem
3. Include your Windows version and UEFI/BIOS information
4. Share the exported ZIP file when reporting the issue

The diagnostic logs contain all the information needed to help solve most boot configuration problems!
