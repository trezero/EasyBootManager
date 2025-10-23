"""
BootSessionTracker - Tracks and correlates boot sessions with operations
"""
import psutil
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class BootSession:
    """Represents a single boot session."""
    
    def __init__(self, session_id: str, boot_timestamp: float,
                 previous_operations: Optional[List[Dict]] = None,
                 actual_boot_entry: Optional[str] = None,
                 expected_boot_entry: Optional[str] = None):
        self.session_id = session_id
        self.boot_timestamp = boot_timestamp
        self.previous_operations = previous_operations or []
        self.actual_boot_entry = actual_boot_entry
        self.expected_boot_entry = expected_boot_entry
        self.boot_match_status = 'UNKNOWN'
        self.diagnosis = ''
        self.event_logs = []
        
        # Calculate match status
        if actual_boot_entry and expected_boot_entry:
            self.boot_match_status = 'MATCH' if actual_boot_entry == expected_boot_entry else 'MISMATCH'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'boot_timestamp': self.boot_timestamp,
            'previous_operations': self.previous_operations,
            'actual_boot_entry': self.actual_boot_entry,
            'expected_boot_entry': self.expected_boot_entry,
            'boot_match_status': self.boot_match_status,
            'diagnosis': self.diagnosis,
            'event_logs': self.event_logs
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'BootSession':
        """Create BootSession from dictionary."""
        session = BootSession(
            session_id=data['session_id'],
            boot_timestamp=data['boot_timestamp'],
            previous_operations=data.get('previous_operations', []),
            actual_boot_entry=data.get('actual_boot_entry'),
            expected_boot_entry=data.get('expected_boot_entry')
        )
        session.boot_match_status = data.get('boot_match_status', 'UNKNOWN')
        session.diagnosis = data.get('diagnosis', '')
        session.event_logs = data.get('event_logs', [])
        return session
    
    def get_formatted_time(self) -> str:
        """Get formatted timestamp."""
        return datetime.fromtimestamp(self.boot_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def has_event(self, event_id: int) -> bool:
        """Check if session has a specific event ID."""
        return any(e.get('event_id') == event_id for e in self.event_logs)
    
    def add_event_log(self, event_data: Dict):
        """Add event log data to this session."""
        self.event_logs.append(event_data)


class BootSessionTracker:
    """Tracks and correlates boot sessions with operations."""
    
    MAX_SESSIONS = 5  # Keep last 5 boot sessions
    
    def __init__(self):
        """Initialize BootSessionTracker."""
        # Set up storage directory
        appdata = os.getenv('LOCALAPPDATA')
        self.storage_dir = os.path.join(appdata, 'PyBootManager', 'logs')
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.sessions_file = os.path.join(self.storage_dir, 'boot_sessions.json')
        self.last_boot_file = os.path.join(self.storage_dir, 'last_boot_time.txt')
        
        # Load existing sessions
        self.sessions: List[BootSession] = self._load_sessions()
        
        # Detect if this is a new boot session
        self.current_session = self._detect_new_boot()
    
    def _load_sessions(self) -> List[BootSession]:
        """Load boot sessions from storage."""
        if not os.path.exists(self.sessions_file):
            return []
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [BootSession.from_dict(s) for s in data]
        except Exception as e:
            print(f"Error loading boot sessions: {e}")
            return []
    
    def _save_sessions(self):
        """Save boot sessions to storage."""
        try:
            # Keep only the last MAX_SESSIONS sessions
            sessions_to_save = self.sessions[-self.MAX_SESSIONS:]
            
            data = [session.to_dict() for session in sessions_to_save]
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.sessions = sessions_to_save
        except Exception as e:
            print(f"Error saving boot sessions: {e}")
    
    def _load_last_boot_time(self) -> Optional[float]:
        """Load last recorded boot time."""
        if not os.path.exists(self.last_boot_file):
            return None
        
        try:
            with open(self.last_boot_file, 'r') as f:
                return float(f.read().strip())
        except Exception as e:
            print(f"Error loading last boot time: {e}")
            return None
    
    def _save_last_boot_time(self, boot_time: float):
        """Save boot time."""
        try:
            with open(self.last_boot_file, 'w') as f:
                f.write(str(boot_time))
        except Exception as e:
            print(f"Error saving boot time: {e}")
    
    def _detect_new_boot(self) -> Optional[BootSession]:
        """
        Detect if this is a new boot session.
        
        Returns:
            New BootSession if detected, None otherwise
        """
        try:
            # Get current boot time from system
            current_boot_time = psutil.boot_time()
            last_boot_time = self._load_last_boot_time()
            
            # Check if this is a new boot
            if last_boot_time is None or current_boot_time > last_boot_time:
                # Create new boot session
                boot_dt = datetime.fromtimestamp(current_boot_time)
                session_id = f"boot_{boot_dt.strftime('%Y%m%d_%H%M%S')}"
                
                session = BootSession(
                    session_id=session_id,
                    boot_timestamp=current_boot_time
                )
                
                # Add to sessions list
                self.sessions.append(session)
                
                # Save boot time and sessions
                self._save_last_boot_time(current_boot_time)
                self._save_sessions()
                
                print(f"New boot session detected: {session_id}")
                return session
            else:
                # Return the most recent session
                return self.sessions[-1] if self.sessions else None
        except Exception as e:
            print(f"Error detecting boot session: {e}")
            return None
    
    def detect_boot_session(self) -> Optional[BootSession]:
        """
        Detect and return current boot session.
        
        Returns:
            Current BootSession
        """
        if self.current_session is None:
            self.current_session = self._detect_new_boot()
        
        return self.current_session
    
    def get_boot_history(self, count: int = 5) -> List[BootSession]:
        """
        Get boot session history.
        
        Args:
            count: Number of recent sessions to retrieve
            
        Returns:
            List of BootSession objects (most recent first)
        """
        return list(reversed(self.sessions[-count:]))
    
    def correlate_operation_to_boot(self, operation_id: str, 
                                     operation_type: str,
                                     target_entry: str,
                                     timestamp: float) -> bool:
        """
        Correlate an operation with the next boot session.
        
        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation (e.g., 'BOOT_ONCE', 'SET_DEFAULT')
            target_entry: Target boot entry identifier
            timestamp: Operation timestamp
            
        Returns:
            True if correlated successfully
        """
        try:
            # Find the most recent boot session before this operation
            # The operation affects the NEXT boot
            operation_data = {
                'operation_id': operation_id,
                'operation_type': operation_type,
                'target_entry': target_entry,
                'timestamp': timestamp
            }
            
            # Add to the most recent session's previous operations
            # (These will be used to diagnose the next boot)
            if self.current_session:
                self.current_session.previous_operations.append(operation_data)
                
                # If this is a BOOT_ONCE or SET_DEFAULT, set expected entry
                if operation_type in ['BOOT_ONCE', 'SET_DEFAULT']:
                    # This will be verified on next boot
                    # For now, we just record it
                    pass
                
                self._save_sessions()
                return True
            
            return False
        except Exception as e:
            print(f"Error correlating operation: {e}")
            return False
    
    def verify_boot_success(self, expected_entry: str, actual_entry: str) -> bool:
        """
        Verify if boot matched expectation.
        
        Args:
            expected_entry: Expected boot entry identifier
            actual_entry: Actual boot entry identifier
            
        Returns:
            True if matched, False otherwise
        """
        return expected_entry == actual_entry
    
    def update_current_session(self, actual_boot_entry: str,
                               expected_boot_entry: Optional[str] = None):
        """
        Update current session with actual boot information.
        
        Args:
            actual_boot_entry: The boot entry that was actually used
            expected_boot_entry: The expected boot entry (if known)
        """
        if not self.current_session:
            return
        
        self.current_session.actual_boot_entry = actual_boot_entry
        
        if expected_boot_entry:
            self.current_session.expected_boot_entry = expected_boot_entry
        else:
            # Try to determine expected from previous operations
            if self.current_session.previous_operations:
                # Get the most recent BOOT_ONCE or SET_DEFAULT operation
                for op in reversed(self.current_session.previous_operations):
                    if op['operation_type'] in ['BOOT_ONCE', 'SET_DEFAULT']:
                        self.current_session.expected_boot_entry = op['target_entry']
                        break
        
        # Update match status
        if self.current_session.actual_boot_entry and self.current_session.expected_boot_entry:
            match = self.verify_boot_success(
                self.current_session.expected_boot_entry,
                self.current_session.actual_boot_entry
            )
            self.current_session.boot_match_status = 'MATCH' if match else 'MISMATCH'
            
            if not match:
                # Generate diagnosis
                self.current_session.diagnosis = self._generate_diagnosis()
        
        self._save_sessions()
    
    def _generate_diagnosis(self) -> str:
        """
        Generate diagnosis for boot mismatch.
        
        Returns:
            Diagnosis message
        """
        if not self.current_session:
            return "Unknown"
        
        diagnosis_parts = []
        
        # Check for boot-once scenario
        boot_once_ops = [
            op for op in self.current_session.previous_operations
            if op['operation_type'] == 'BOOT_ONCE'
        ]
        
        if boot_once_ops:
            diagnosis_parts.append("Boot once may have been cleared or system crashed")
        
        # Check for permission issues (would be in operation logs)
        diagnosis_parts.append("Check operation logs for permission errors")
        
        # Check for unexpected shutdown events
        if self.current_session.has_event(41):
            diagnosis_parts.append("System experienced unexpected shutdown")
        
        if not diagnosis_parts:
            return "Boot entry mismatch - cause unknown"
        
        return " | ".join(diagnosis_parts)
    
    def add_event_to_current_session(self, event_data: Dict):
        """Add event log data to current session."""
        if self.current_session:
            self.current_session.add_event_log(event_data)
            self._save_sessions()
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current boot session ID."""
        return self.current_session.session_id if self.current_session else None
