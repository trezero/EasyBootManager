"""
BackupManager - Manages boot configuration backups using bcdedit export/import
"""
import subprocess
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class BackupInfo:
    """Represents backup metadata."""
    
    def __init__(self, name: str, timestamp: float, file_path: str, description: str = ""):
        self.name = name
        self.timestamp = timestamp
        self.file_path = file_path
        self.description = description
    
    def get_formatted_time(self) -> str:
        """Get formatted timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'timestamp': self.timestamp,
            'file_path': self.file_path,
            'description': self.description
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'BackupInfo':
        """Create BackupInfo from dictionary."""
        return BackupInfo(
            name=data['name'],
            timestamp=data['timestamp'],
            file_path=data['file_path'],
            description=data.get('description', '')
        )


class BackupManager:
    """Manages boot configuration backups."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        Initialize BackupManager.
        
        Args:
            backup_dir: Directory to store backups. Defaults to AppData\Local\PyBootManager\backups
        """
        if backup_dir is None:
            appdata = os.getenv('LOCALAPPDATA')
            backup_dir = os.path.join(appdata, 'PyBootManager', 'backups')
        
        self.backup_dir = backup_dir
        self.metadata_file = os.path.join(backup_dir, 'backups.json')
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Load existing backups
        self.backups = self._load_metadata()
    
    def _load_metadata(self) -> List[BackupInfo]:
        """Load backup metadata from JSON file."""
        if not os.path.exists(self.metadata_file):
            return []
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                return [BackupInfo.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error loading backup metadata: {e}")
            return []
    
    def _save_metadata(self):
        """Save backup metadata to JSON file."""
        try:
            data = [backup.to_dict() for backup in self.backups]
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving backup metadata: {e}")
    
    def create_backup(self, name: Optional[str] = None, description: str = "") -> Optional[BackupInfo]:
        """
        Create a backup of the current boot configuration.
        
        Args:
            name: Optional backup name. If not provided, generates timestamp-based name
            description: Optional description for the backup
            
        Returns:
            BackupInfo object if successful, None otherwise
        """
        # Generate backup name if not provided
        if name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name = f"backup_{timestamp}"
        
        # Create backup file path
        backup_file = os.path.join(self.backup_dir, f"{name}.bcd")
        
        # Export BCD store
        try:
            cmd = ['bcdedit', '/export', backup_file]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                check=False
            )
            
            if result.returncode != 0:
                print(f"Backup export failed: {result.stderr}")
                return None
            
            # Create backup info
            backup_info = BackupInfo(
                name=name,
                timestamp=time.time(),
                file_path=backup_file,
                description=description
            )
            
            # Add to metadata and save
            self.backups.append(backup_info)
            self._save_metadata()
            
            print(f"Backup created: {name}")
            return backup_info
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore a backup by name.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        # Find backup by name
        backup = None
        for b in self.backups:
            if b.name == backup_name:
                backup = b
                break
        
        if not backup:
            print(f"Backup not found: {backup_name}")
            return False
        
        if not os.path.exists(backup.file_path):
            print(f"Backup file not found: {backup.file_path}")
            return False
        
        try:
            # Import BCD store
            cmd = ['bcdedit', '/import', backup.file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                check=False
            )
            
            if result.returncode != 0:
                print(f"Backup restore failed: {result.stderr}")
                return False
            
            print(f"Backup restored: {backup_name}")
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """
        Get list of all available backups.
        
        Returns:
            List of BackupInfo objects, sorted by timestamp (newest first)
        """
        return sorted(self.backups, key=lambda x: x.timestamp, reverse=True)
    
    def delete_backup(self, backup_name: str) -> bool:
        """
        Delete a backup by name.
        
        Args:
            backup_name: Name of the backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Find backup by name
        backup = None
        for b in self.backups:
            if b.name == backup_name:
                backup = b
                break
        
        if not backup:
            print(f"Backup not found: {backup_name}")
            return False
        
        try:
            # Delete backup file
            if os.path.exists(backup.file_path):
                os.remove(backup.file_path)
            
            # Remove from metadata
            self.backups.remove(backup)
            self._save_metadata()
            
            print(f"Backup deleted: {backup_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False
    
    def create_auto_backup(self) -> Optional[BackupInfo]:
        """
        Create an automatic backup before configuration changes.
        
        Returns:
            BackupInfo object if successful, None otherwise
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = f"auto_{timestamp}"
        return self.create_backup(name, "Automatic backup before configuration change")
