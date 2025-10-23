# PyBootManager - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Verify Requirements
- ✅ Windows 10 or Windows 11
- ✅ Python 3.8 or higher installed
- ✅ Required dependencies: `pip install -r requirements.txt`
- ✅ Administrator access

### Step 2: Run the Application

**Option A: Using Batch File (Recommended)**
1. Double-click `run_as_admin.bat`
2. Click "Yes" on UAC prompt
3. Application launches automatically

**Option B: Manual Launch**
1. Right-click `pybootmanager.py`
2. Select "Run as administrator"
3. Application window opens

### Step 3: Explore Features

#### 📋 View Boot Entries
- Application automatically displays all boot entries
- Current default is marked with "DEFAULT" status
- Current timeout is shown at the top

#### 🔄 Boot Another OS Once
1. Select an OS from the list
2. Click **"Boot Once"**
3. Confirm the action
4. Restart your computer
5. Selected OS boots, then reverts to default

#### ⚙️ Change Default OS
1. Select an OS from the list
2. Click **"Set Default"**
3. Confirm the action
4. Selected OS becomes permanent default

#### ⏱️ Change Boot Timeout
1. Click **"Configure Timeout"**
2. Enter seconds (e.g., 5, 10, 30)
3. Confirm the change

#### 💾 Backups (Automatic)
- Backup created before every change
- Stored in: `%LOCALAPPDATA%\PyBootManager\backups\`
- View backups: Click **"View Backups"**
- Restore: Click **"Restore Backup"** → Select backup

#### 📊 Diagnostics (Troubleshooting)
- Click **"View Diagnostics"** to open diagnostics viewer
- Review operation logs, event logs, and boot session timeline
- Export logs for troubleshooting: Click **"Export All"**
- See detailed guide: [DIAGNOSTICS_GUIDE.md](DIAGNOSTICS_GUIDE.md)

## 🎯 Common Use Cases

### Use Case 1: Switch to Linux for Development
```
1. Open PyBootManager (as admin)
2. Select "Ubuntu" (or your Linux distro)
3. Click "Boot Once"
4. Confirm
5. Restart computer
```
Your computer boots to Linux once, then back to Windows default.

### Use Case 2: Make Linux Your Default OS
```
1. Open PyBootManager (as admin)
2. Select "Ubuntu" (or your Linux distro)
3. Click "Set Default"
4. Confirm
```
Linux is now your default OS on every boot.

### Use Case 3: Speed Up Boot (Reduce Timeout)
```
1. Open PyBootManager (as admin)
2. Click "Configure Timeout"
3. Enter "3" (for 3 seconds)
4. Confirm
```
Boot menu now shows for only 3 seconds.

### Use Case 4: Restore Previous Configuration
```
1. Open PyBootManager (as admin)
2. Click "Restore Backup"
3. Select the backup you want
4. Confirm restoration
```
Boot configuration restored to selected state.

### Use Case 5: Troubleshoot "Boot Once" Not Working
```
1. Open PyBootManager (as admin)
2. Click "View Diagnostics"
3. Select the boot session after your "Boot Once" attempt
4. Go to "Timeline & Correlation" tab
5. Check Match Status and Diagnosis
6. Common issues:
   - Fast Startup enabled (disable in Power Options)
   - Permission denied (check Operation Logs)
   - System crashed (check Event Logs for Event ID 41)
```
Diagnostics help identify why boot didn't work as expected.

## ⚠️ Important Tips

### ✅ DO:
- Always run as administrator
- Create manual backups before major changes
- Test in safe environment first
- Keep Windows updated

### ❌ DON'T:
- Don't close application during operations
- Don't modify BCD store manually while using PyBootManager
- Don't delete backup folder
- Don't run multiple instances simultaneously

## 🐛 Troubleshooting

### Problem: "Administrator Required" Error
**Solution:** Right-click → "Run as administrator" or use `run_as_admin.bat`

### Problem: No Boot Entries Showing
**Solution:** 
- Ensure you have dual-boot setup
- Run `bcdedit /enum` in admin Command Prompt
- Check Windows Boot Manager is active

### Problem: Changes Don't Apply
**Solution:**
- Verify administrator privileges
- Open **View Diagnostics** to check operation logs
- Look for ERROR entries in Operation Logs tab
- Check BCD operation return codes (should be 0 for success)
- Try restoring from backup

### Problem: "Boot Once" Doesn't Work
**Solution:**
1. Click **"View Diagnostics"**
2. Select the boot session in question
3. Review **Timeline & Correlation** tab
4. Check diagnosis for specific cause:
   - **Fast Startup**: Disable in Control Panel → Power Options
   - **Permission Denied**: Run as Administrator
   - **System Crash**: Check Event Logs for Event ID 41
   - **UEFI Override**: Check BIOS boot settings

### Problem: Application Won't Start
**Solution:**
- Verify Python 3.8+ installed: `python --version`
- Check Python is in system PATH
- Try running: `python pybootmanager.py` from Command Prompt

## 📚 Learn More

- **Full Documentation:** [README.md](README.md)
- **Diagnostics & Troubleshooting:** [DIAGNOSTICS_GUIDE.md](DIAGNOSTICS_GUIDE.md)
- **Technical Details:** [prd.md](prd.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changes:** [CHANGELOG.md](CHANGELOG.md)

## 🎬 Example Workflow

```
Day 1 - Monday (Need Windows for work)
→ Current default: Windows ✅

Day 2 - Tuesday (Need Linux for development)
→ PyBootManager → Select Linux → Boot Once → Restart
→ Boots to Linux
→ Work done, restart
→ Boots back to Windows (default) ✅

Day 3 - Wednesday (Mostly Linux this week)
→ PyBootManager → Select Linux → Set Default
→ Now Linux boots by default ✅

Day 4 - Thursday (Troubleshooting boot issue)
→ Notice Linux didn't boot as expected
→ PyBootManager → View Diagnostics
→ Check boot session timeline
→ Discover Fast Startup was enabled
→ Disable Fast Startup in Power Options
→ Problem solved ✅

Day 7 - Sunday (Back to Windows next week)
→ PyBootManager → Select Windows → Set Default
→ Now Windows boots by default ✅
```

## 🆘 Need Help?

- Check [README.md](README.md) troubleshooting section
- Open GitHub issue with error details
- Include: Windows version, Python version, error message

---

**Happy dual-booting! 🚀**
