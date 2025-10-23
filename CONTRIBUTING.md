# Contributing to PyBootManager

Thank you for considering contributing to PyBootManager! This document provides guidelines and information for contributors.

## 🎯 Project Goals

PyBootManager aims to be:
- **Simple**: Easy to use for non-technical users
- **Safe**: Never leaves boot configuration in an invalid state
- **Reliable**: Robust error handling and automatic backups
- **Open**: Transparent, well-documented, and community-driven

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/PyBootManager.git
   cd PyBootManager
   ```

2. **Ensure Python 3.8+ is installed:**
   ```bash
   python --version
   ```

3. **Test the application:**
   ```bash
   python pybootmanager.py
   ```
   Note: Must run as administrator on Windows

### Project Structure

```
PyBootManager/
├── src/                      # Source code
│   ├── __init__.py          # Package initialization
│   ├── bcd_manager.py       # Boot Configuration Data management
│   ├── backup_manager.py    # Backup/restore functionality
│   ├── privilege_manager.py # Admin privilege handling
│   └── gui.py               # Main GUI application
├── pybootmanager.py         # Main entry point
├── requirements.txt         # Dependencies
├── prd.md                   # Product Requirements Document
└── README.md                # Documentation
```

## 📝 Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use docstrings for all classes and functions

### Example:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation
    return True
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `BCDManager`, `BackupInfo`)
- **Functions/Methods**: snake_case (e.g., `get_boot_entries`, `create_backup`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_TIMEOUT`, `DEFAULT_DIR`)
- **Private methods**: Prefix with underscore (e.g., `_run_bcdedit`, `_load_metadata`)

## 🔧 Development Guidelines

### Testing

Before submitting changes:
1. Test on Windows 10 and/or Windows 11
2. Test with both UEFI and Legacy BIOS (if possible)
3. Verify backup creation and restoration
4. Test error handling scenarios
5. Ensure all operations require admin privileges

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, well-documented code
   - Follow existing code style
   - Add comments for complex logic

3. **Test thoroughly:**
   - Test all affected functionality
   - Test edge cases and error conditions

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   - Provide clear description of changes
   - Reference any related issues
   - Include screenshots if UI changes

## 🐛 Reporting Bugs

When reporting bugs, please include:
- **Windows Version**: (e.g., Windows 10 21H2, Windows 11 22H2)
- **Python Version**: Output of `python --version`
- **Boot Mode**: UEFI or Legacy BIOS
- **Steps to Reproduce**: Clear steps to trigger the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error text or screenshots
- **Logs**: Any relevant error logs

## 💡 Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists or is planned
- Describe the problem it solves
- Explain how it should work
- Consider if it aligns with project goals

## ⚠️ Safety Guidelines

Boot configuration changes are critical system operations. When contributing:

1. **Never skip backups**: Always create backup before modifications
2. **Validate inputs**: Check all user inputs and bcdedit output
3. **Handle errors gracefully**: Never leave system in invalid state
4. **Test thoroughly**: Boot configuration bugs can prevent system startup
5. **Document risks**: Clearly document any potentially dangerous operations

## 📚 Documentation

Good documentation is essential:
- Update README.md for user-facing changes
- Update docstrings for code changes
- Update CHANGELOG.md for all changes
- Add comments for complex logic

## 🎨 UI/UX Guidelines

For GUI changes:
- Keep interface simple and intuitive
- Use clear, non-technical language in messages
- Provide confirmation for dangerous operations
- Show progress for long-running operations
- Display helpful error messages

## 🔐 Security Considerations

- Never bypass administrator privilege checks
- Sanitize all inputs to bcdedit commands
- Validate file paths to prevent directory traversal
- Store backups with appropriate permissions

## 📋 Pull Request Checklist

Before submitting a PR, ensure:
- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have docstrings
- [ ] Changes are tested on Windows
- [ ] No breaking changes (or clearly documented)
- [ ] README updated if needed
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear and descriptive

## 🤝 Code Review Process

1. Maintainers will review your PR
2. Feedback may be provided for improvements
3. Make requested changes and update PR
4. Once approved, PR will be merged
5. Your contribution will be credited in CHANGELOG

## 📞 Questions?

If you have questions about contributing:
- Open a GitHub issue with "Question:" prefix
- Check existing issues and PRs for similar topics
- Review the Product Requirements Document (prd.md)

## 🙏 Thank You!

Your contributions make PyBootManager better for everyone. We appreciate your time and effort!

---

**Remember**: Always test boot configuration changes in a safe environment first!
