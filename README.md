# PyBootManager

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-orange)

**A lightweight, user-friendly Python application for managing dual-boot and multi-boot configurations on Windows systems.**

## 🎯 Overview

PyBootManager simplifies boot management on Windows by providing an intuitive GUI to:
- Select which OS boots next without accessing BIOS/UEFI
- Change default boot OS
- Configure boot menu timeout
- Backup and restore boot configurations

Perfect for users with display sync issues, headless setups, or anyone who wants convenient boot selection from Windows.

## ✨ Features

- **🔄 One-Time Boot Selection** - Choose which OS boots next without changing defaults
- **⚙️ Default Boot Configuration** - Set permanent default boot OS
- **⏱️ Timeout Management** - Adjust boot menu timeout (0-999 seconds)
- **💾 Backup & Restore** - Automatic backups before every change + manual backup creation
- **🖥️ User-Friendly GUI** - Clean, modern interface built with tkinter
- **🔒 Safe Operations** - Validates all changes and creates backups before modifications
- **📋 Boot Entry Detection** - Automatically detects all available boot entries

## 📋 Requirements

- **Operating System:** Windows 10 or Windows 11 (x64)
- **Python Version:** Python 3.8 or higher
- **Administrator Privileges:** Required for boot configuration management
- **Boot Modes:** Supports both UEFI and Legacy BIOS

## 🚀 Installation

### Option 1: Run from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/PyBootManager.git
   cd PyBootManager
   ```

2. **Install Python 3.8+** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)

3. **Run the application:**
   ```bash
   python pybootmanager.py
   ```

### Option 2: Build Executable (Coming Soon)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name PyBootManager pybootmanager.py
```

## 📖 Usage

### Launching the Application

1. **Right-click** `pybootmanager.py`
2. Select **"Run as administrator"**
3. The GUI will open showing your current boot configuration

### Managing Boot Entries

#### Set Boot Once
1. Select a boot entry from the list
2. Click **"Boot Once"**
3. Confirm the action
4. Your selected OS will boot on next restart, then revert to default

#### Change Default Boot OS
1. Select a boot entry from the list
2. Click **"Set Default"**
3. Confirm the action
4. The selected OS becomes the permanent default

#### Configure Timeout
1. Click **"Configure Timeout"**
2. Enter timeout value (0-999 seconds)
3. Confirm the change

#### Create Manual Backup
1. Click **"Create Backup"**
2. Enter a name for the backup
3. Backup is created and stored

#### Restore from Backup
1. Click **"Restore Backup"**
2. Select a backup from the list
3. Confirm restoration

## 🏗️ Project Structure

```
PyBootManager/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── bcd_manager.py        # Boot Configuration Data management
│   ├── backup_manager.py     # Backup/restore functionality
│   ├── privilege_manager.py  # Admin privilege handling
│   └── gui.py                # Main GUI application
├── pybootmanager.py          # Main entry point
├── requirements.txt          # Python dependencies
├── prd.md                    # Product Requirements Document
└── README.md                 # This file
```

## 🔧 Technical Details

### Core Components

- **BCDManager:** Interfaces with Windows Boot Manager via `bcdedit` command
- **BackupManager:** Manages boot configuration backups using `bcdedit export/import`
- **PrivilegeManager:** Ensures administrator privileges for boot modifications
- **GUI:** Tkinter-based user interface with modern styling

### Data Storage

Backups are stored in: `%LOCALAPPDATA%\PyBootManager\backups\`

### How It Works

1. Application detects boot entries using `bcdedit /enum`
2. User selects an action (boot once, set default, etc.)
3. Automatic backup is created before any modification
4. Change is applied via appropriate `bcdedit` command
5. Success/failure is reported to user

## ⚠️ Important Notes

- **Always requires administrator privileges**
- **Automatic backups created before every change**
- **Do not interrupt operations in progress**
- **Test in a safe environment before production use**

## 🐛 Troubleshooting

### "Administrator Required" Error
- Right-click and select "Run as administrator"
- Or open Command Prompt as admin and run: `python pybootmanager.py`

### Boot Entries Not Showing
- Ensure you're running Windows 10/11
- Check that you have multiple boot entries configured
- Verify Windows Boot Manager is your boot loader

### Operation Failed
- Confirm administrator privileges
- Check Windows Event Viewer for bcdedit errors
- Restore from a recent backup if needed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for users experiencing display sync issues during boot
- Inspired by the need for a free, open-source alternative to commercial boot managers
- Thanks to the Windows bcdedit documentation

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [Product Requirements Document](prd.md) for detailed specifications

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Boot entry detection
- ✅ One-time boot selection
- ✅ Default boot configuration
- ✅ Timeout management
- ✅ Backup and restore
- ✅ GUI interface

### Version 2.0 (Planned)
- 🔮 GRUB configuration support
- 🔮 Remote boot management
- 🔮 Scheduled boot switching
- 🔮 Custom boot entry creation

---

**Made with ❤️ for the dual-boot community**
