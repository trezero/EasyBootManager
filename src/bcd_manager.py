"""
BCDManager - Handles all interactions with Windows Boot Manager via bcdedit
"""
import subprocess
import re
from typing import List, Dict, Optional


class BootEntry:
    """Represents a single boot entry in the BCD store."""
    
    def __init__(self, identifier: str, description: str, is_default: bool = False):
        self.identifier = identifier
        self.description = description
        self.is_default = is_default
    
    def __repr__(self):
        default_marker = " [DEFAULT]" if self.is_default else ""
        return f"BootEntry('{self.description}'{default_marker}, {self.identifier})"


class BCDManager:
    """Manages Windows Boot Configuration Data (BCD) store operations."""
    
    def __init__(self):
        self.boot_entries = []
        self.current_default = None
        self.timeout = None
    
    def _run_bcdedit(self, args: List[str]) -> Optional[str]:
        """
        Execute bcdedit command with specified arguments.
        
        Args:
            args: List of command arguments
            
        Returns:
            Command output as string, or None if command failed
        """
        try:
            cmd = ['bcdedit'] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"bcdedit command failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error running bcdedit: {e}")
            return None
    
    def get_boot_entries(self) -> List[BootEntry]:
        """
        Retrieve all boot entries from the BCD store.
        
        Returns:
            List of BootEntry objects
        """
        output = self._run_bcdedit(['/enum', 'firmware'])
        if not output:
            output = self._run_bcdedit(['/enum'])
        
        if not output:
            return []
        
        entries = []
        current_id = None
        current_desc = None
        
        # Parse bcdedit output
        for line in output.split('\n'):
            line = line.strip()
            
            # Match identifier line
            id_match = re.match(r'^identifier\s+(.+)$', line, re.IGNORECASE)
            if id_match:
                current_id = id_match.group(1).strip()
                continue
            
            # Match description line
            desc_match = re.match(r'^description\s+(.+)$', line, re.IGNORECASE)
            if desc_match:
                current_desc = desc_match.group(1).strip()
                
                # Create entry when we have both ID and description
                if current_id and current_desc:
                    entries.append(BootEntry(current_id, current_desc))
                    current_id = None
                    current_desc = None
        
        self.boot_entries = entries
        
        # Mark the default entry
        default_id = self.get_current_default()
        if default_id:
            for entry in self.boot_entries:
                if entry.identifier == default_id:
                    entry.is_default = True
                    break
        
        return self.boot_entries
    
    def get_current_default(self) -> Optional[str]:
        """
        Get the current default boot entry identifier.
        
        Returns:
            Default boot entry identifier, or None if not found
        """
        output = self._run_bcdedit(['/enum', '{bootmgr}'])
        
        if not output:
            return None
        
        # Look for default entry
        for line in output.split('\n'):
            line = line.strip()
            default_match = re.match(r'^default\s+(.+)$', line, re.IGNORECASE)
            if default_match:
                self.current_default = default_match.group(1).strip()
                return self.current_default
        
        return None
    
    def get_timeout(self) -> Optional[int]:
        """
        Get the current boot menu timeout value.
        
        Returns:
            Timeout in seconds, or None if not found
        """
        output = self._run_bcdedit(['/enum', '{bootmgr}'])
        
        if not output:
            return None
        
        # Look for timeout value
        for line in output.split('\n'):
            line = line.strip()
            timeout_match = re.match(r'^timeout\s+(\d+)$', line, re.IGNORECASE)
            if timeout_match:
                self.timeout = int(timeout_match.group(1))
                return self.timeout
        
        return None
    
    def set_default(self, identifier: str) -> bool:
        """
        Set the default boot entry.
        
        Args:
            identifier: Boot entry identifier to set as default
            
        Returns:
            True if successful, False otherwise
        """
        output = self._run_bcdedit(['/default', identifier])
        return output is not None
    
    def set_boot_once(self, identifier: str) -> bool:
        """
        Set the OS to boot once on next restart.
        
        Args:
            identifier: Boot entry identifier to boot once
            
        Returns:
            True if successful, False otherwise
        """
        output = self._run_bcdedit(['/bootsequence', identifier])
        return output is not None
    
    def set_timeout(self, seconds: int) -> bool:
        """
        Set the boot menu timeout.
        
        Args:
            seconds: Timeout value in seconds (0-999)
            
        Returns:
            True if successful, False otherwise
        """
        if not 0 <= seconds <= 999:
            print(f"Invalid timeout value: {seconds}. Must be between 0 and 999.")
            return False
        
        output = self._run_bcdedit(['/timeout', str(seconds)])
        return output is not None
    
    def validate_identifier(self, identifier: str) -> bool:
        """
        Validate that a boot entry identifier exists.
        
        Args:
            identifier: Boot entry identifier to validate
            
        Returns:
            True if identifier exists, False otherwise
        """
        if not self.boot_entries:
            self.get_boot_entries()
        
        for entry in self.boot_entries:
            if entry.identifier == identifier:
                return True
        
        return False
