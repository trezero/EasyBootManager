"""
PrivilegeManager - Handles administrator privilege checking and elevation
"""
import ctypes
import sys
import os


class PrivilegeManager:
    """Manages administrator privileges for the application."""
    
    @staticmethod
    def is_admin():
        """
        Check if the current process has administrator privileges.
        
        Returns:
            bool: True if running as administrator, False otherwise
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    
    @staticmethod
    def request_elevation():
        """
        Request administrator privileges by restarting the application with elevation.
        
        This method will cause the application to restart with a UAC prompt.
        If the user declines, the application will exit.
        """
        if PrivilegeManager.is_admin():
            return True
        
        try:
            # Get the current script path
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            
            # Request elevation via ShellExecute
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                params, 
                None, 
                1  # SW_SHOWNORMAL
            )
            
            if ret > 32:  # Success
                sys.exit(0)
            else:
                return False
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            return False
    
    @staticmethod
    def ensure_admin():
        """
        Ensure the application is running with administrator privileges.
        If not, request elevation and exit current process.
        
        Returns:
            bool: True if admin privileges are available
        """
        if not PrivilegeManager.is_admin():
            print("Administrator privileges required. Requesting elevation...")
            return PrivilegeManager.request_elevation()
        return True
