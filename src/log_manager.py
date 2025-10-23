"""
LogManager - Central logging system for all application operations
"""
import logging
import json
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid


class LogEntry:
    """Represents a single log entry."""
    
    def __init__(self, timestamp: float, log_level: str, category: str,
                 operation_id: str, boot_session_id: Optional[str],
                 message: str, details: Optional[Dict] = None):
        self.timestamp = timestamp
        self.log_level = log_level
        self.category = category
        self.operation_id = operation_id
        self.boot_session_id = boot_session_id
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp,
            'log_level': self.log_level,
            'category': self.category,
            'operation_id': self.operation_id,
            'boot_session_id': self.boot_session_id,
            'message': self.message,
            'details': self.details
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'LogEntry':
        """Create LogEntry from dictionary."""
        return LogEntry(
            timestamp=data['timestamp'],
            log_level=data['log_level'],
            category=data['category'],
            operation_id=data['operation_id'],
            boot_session_id=data.get('boot_session_id'),
            message=data['message'],
            details=data.get('details', {})
        )
    
    def get_formatted_time(self) -> str:
        """Get formatted timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class LogManager:
    """Central logging system for all application operations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one LogManager instance."""
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize LogManager with rotating file handlers."""
        if self._initialized:
            return
        
        # Set up log directory
        appdata = os.getenv('LOCALAPPDATA')
        self.log_dir = os.path.join(appdata, 'PyBootManager', 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Log file paths
        self.app_log_path = os.path.join(self.log_dir, 'application.log')
        self.operations_log_path = os.path.join(self.log_dir, 'operations.jsonl')
        
        # Current boot session ID
        self.current_boot_session_id = None
        
        # Set up Python logger
        self.logger = logging.getLogger('PyBootManager')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Rotating file handler for general application logs (10MB, 3 files)
        app_handler = RotatingFileHandler(
            self.app_log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.DEBUG)
        
        # Format for application log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        app_handler.setFormatter(formatter)
        self.logger.addHandler(app_handler)
        
        # Also add console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
        self.logger.info("LogManager initialized")
    
    def set_boot_session_id(self, session_id: str):
        """Set the current boot session ID."""
        self.current_boot_session_id = session_id
        self.logger.info(f"Boot session set: {session_id}")
    
    def _generate_operation_id(self) -> str:
        """Generate a unique operation ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"op_{timestamp}_{unique_id}"
    
    def _write_operation_log(self, entry: LogEntry):
        """Write operation log entry to JSON Lines file."""
        try:
            with open(self.operations_log_path, 'a', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write operation log: {e}")
    
    def log_user_action(self, action: str, details: Optional[Dict] = None) -> str:
        """
        Log user action from GUI.
        
        Args:
            action: Description of the user action
            details: Additional context details
            
        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()
        
        entry = LogEntry(
            timestamp=time.time(),
            log_level='INFO',
            category='USER_ACTION',
            operation_id=operation_id,
            boot_session_id=self.current_boot_session_id,
            message=action,
            details=details or {}
        )
        
        self.logger.info(f"USER_ACTION: {action} - {details}")
        self._write_operation_log(entry)
        
        return operation_id
    
    def log_bcd_operation(self, command: str, args: List[str], 
                          result: Dict[str, Any]) -> str:
        """
        Log bcdedit operation with full command details.
        
        Args:
            command: The bcdedit command
            args: Command arguments
            result: Dictionary with 'returncode', 'stdout', 'stderr'
            
        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()
        
        details = {
            'command': command,
            'args': args,
            'returncode': result.get('returncode'),
            'stdout': result.get('stdout', '')[:500],  # Limit output size
            'stderr': result.get('stderr', '')[:500]
        }
        
        level = 'INFO' if result.get('returncode') == 0 else 'ERROR'
        
        entry = LogEntry(
            timestamp=time.time(),
            log_level=level,
            category='BCD_OPERATION',
            operation_id=operation_id,
            boot_session_id=self.current_boot_session_id,
            message=f"bcdedit {' '.join(args)}",
            details=details
        )
        
        if level == 'ERROR':
            self.logger.error(f"BCD_OPERATION FAILED: {command} {args} - {result.get('stderr')}")
        else:
            self.logger.info(f"BCD_OPERATION: {command} {args}")
        
        self._write_operation_log(entry)
        
        return operation_id
    
    def log_backup_operation(self, operation_type: str, backup_name: str,
                            success: bool, details: Optional[Dict] = None) -> str:
        """
        Log backup/restore operation.
        
        Args:
            operation_type: Type of operation ('create', 'restore', 'delete')
            backup_name: Name of the backup
            success: Whether the operation succeeded
            details: Additional context details
            
        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()
        
        log_details = details or {}
        log_details['backup_name'] = backup_name
        log_details['operation_type'] = operation_type
        log_details['success'] = success
        
        level = 'INFO' if success else 'ERROR'
        message = f"Backup {operation_type}: {backup_name} - {'SUCCESS' if success else 'FAILED'}"
        
        entry = LogEntry(
            timestamp=time.time(),
            log_level=level,
            category='BACKUP_OPERATION',
            operation_id=operation_id,
            boot_session_id=self.current_boot_session_id,
            message=message,
            details=log_details
        )
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
        
        self._write_operation_log(entry)
        
        return operation_id
    
    def log_error(self, error: Exception, context: str, details: Optional[Dict] = None) -> str:
        """
        Log an error with full context.
        
        Args:
            error: The exception that occurred
            context: Description of what was happening when error occurred
            details: Additional context details
            
        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()
        
        import traceback
        
        log_details = details or {}
        log_details['error_type'] = type(error).__name__
        log_details['error_message'] = str(error)
        log_details['traceback'] = traceback.format_exc()
        
        entry = LogEntry(
            timestamp=time.time(),
            log_level='ERROR',
            category='ERROR',
            operation_id=operation_id,
            boot_session_id=self.current_boot_session_id,
            message=f"{context}: {str(error)}",
            details=log_details
        )
        
        self.logger.error(f"ERROR in {context}: {error}", exc_info=True)
        self._write_operation_log(entry)
        
        return operation_id
    
    def log_info(self, message: str, category: str = 'INFO', 
                 details: Optional[Dict] = None) -> str:
        """
        Log general information message.
        
        Args:
            message: Log message
            category: Log category
            details: Additional context details
            
        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()
        
        entry = LogEntry(
            timestamp=time.time(),
            log_level='INFO',
            category=category,
            operation_id=operation_id,
            boot_session_id=self.current_boot_session_id,
            message=message,
            details=details or {}
        )
        
        self.logger.info(f"{category}: {message}")
        self._write_operation_log(entry)
        
        return operation_id
    
    def get_recent_logs(self, count: int = 100, 
                        category: Optional[str] = None) -> List[LogEntry]:
        """
        Get recent log entries.
        
        Args:
            count: Number of recent entries to retrieve
            category: Optional category filter
            
        Returns:
            List of LogEntry objects
        """
        entries = []
        
        try:
            if not os.path.exists(self.operations_log_path):
                return []
            
            # Read JSON Lines file in reverse to get most recent entries first
            with open(self.operations_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Process lines in reverse order
            for line in reversed(lines):
                if len(entries) >= count:
                    break
                
                try:
                    data = json.loads(line.strip())
                    entry = LogEntry.from_dict(data)
                    
                    # Apply category filter if specified
                    if category is None or entry.category == category:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
            
            return entries
        except Exception as e:
            self.logger.error(f"Failed to read recent logs: {e}")
            return []
    
    def get_logs_by_session(self, session_id: str) -> List[LogEntry]:
        """
        Get all log entries for a specific boot session.
        
        Args:
            session_id: Boot session ID
            
        Returns:
            List of LogEntry objects for the session
        """
        entries = []
        
        try:
            if not os.path.exists(self.operations_log_path):
                return []
            
            with open(self.operations_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        entry = LogEntry.from_dict(data)
                        
                        if entry.boot_session_id == session_id:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            return sorted(entries, key=lambda x: x.timestamp)
        except Exception as e:
            self.logger.error(f"Failed to read session logs: {e}")
            return []
    
    def export_logs(self, file_path: str, session_count: int = 5) -> bool:
        """
        Export logs to a file.
        
        Args:
            file_path: Path to export file
            session_count: Number of recent sessions to include
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get recent log entries
            entries = self.get_recent_logs(count=1000)
            
            # Export to JSON
            export_data = {
                'export_timestamp': time.time(),
                'session_count': session_count,
                'log_entries': [entry.to_dict() for entry in entries]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Logs exported to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
            return False
    
    def get_log_directory(self) -> str:
        """Get the log directory path."""
        return self.log_dir
