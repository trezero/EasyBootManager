"""
WindowsEventLogCollector - Collects Windows Event Logs related to boot operations
"""
import subprocess
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class EventLogEntry:
    """Represents a Windows Event Log entry."""
    
    def __init__(self, event_id: int, timestamp: float, level: str,
                 source: str, message: str, raw_data: Optional[Dict] = None):
        self.event_id = event_id
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.raw_data = raw_data or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp,
            'level': self.level,
            'source': self.source,
            'message': self.message,
            'raw_data': self.raw_data
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EventLogEntry':
        """Create EventLogEntry from dictionary."""
        return EventLogEntry(
            event_id=data['event_id'],
            timestamp=data['timestamp'],
            level=data['level'],
            source=data['source'],
            message=data['message'],
            raw_data=data.get('raw_data', {})
        )
    
    def get_formatted_time(self) -> str:
        """Get formatted timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')


class WindowsEventLogCollector:
    """Collects Windows Event Logs related to boot operations."""
    
    # Boot-related Event IDs to collect
    BOOT_EVENT_IDS = [
        12,    # Boot start
        13,    # Boot end
        27,    # Boot configuration
        41,    # Unexpected shutdown
        1001,  # Bug check
        6005,  # Event log service started
        6006,  # Event log service stopped
        6008,  # Unexpected shutdown (previous)
        6009,  # System boot
    ]
    
    def __init__(self):
        """Initialize WindowsEventLogCollector."""
        # Set up storage directory
        appdata = os.getenv('LOCALAPPDATA')
        self.storage_dir = os.path.join(appdata, 'PyBootManager', 'logs', 'event_logs')
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.has_permission = self._check_permissions()
    
    def _check_permissions(self) -> bool:
        """Check if we have permission to read event logs."""
        try:
            # Try a simple query to check permissions
            cmd = ['wevtutil', 'qe', 'System', '/c:1', '/rd:true', '/f:text']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def collect_boot_events(self, since_timestamp: Optional[float] = None,
                           max_events: int = 50) -> List[EventLogEntry]:
        """
        Collect boot-related events from Windows Event Log.
        
        Args:
            since_timestamp: Only collect events after this timestamp
            max_events: Maximum number of events to collect
            
        Returns:
            List of EventLogEntry objects
        """
        if not self.has_permission:
            print("Warning: No permission to read Windows Event Log")
            return []
        
        events = []
        
        try:
            # Build XPath query for boot-related events
            event_id_filter = ' or '.join([
                f"EventID={eid}" for eid in self.BOOT_EVENT_IDS
            ])
            
            # Query System event log
            events.extend(self._query_log('System', event_id_filter, max_events))
            
            # Query Application event log for BCD-related events
            events.extend(self._query_log('Application', None, max_events // 2))
            
            # Filter by timestamp if specified
            if since_timestamp:
                events = [e for e in events if e.timestamp >= since_timestamp]
            
            # Sort by timestamp (most recent first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return events[:max_events]
        except Exception as e:
            print(f"Error collecting boot events: {e}")
            return []
    
    def _query_log(self, log_name: str, event_id_filter: Optional[str],
                   max_events: int) -> List[EventLogEntry]:
        """
        Query a specific Windows Event Log.
        
        Args:
            log_name: Name of the log (e.g., 'System', 'Application')
            event_id_filter: XPath filter for event IDs
            max_events: Maximum number of events to retrieve
            
        Returns:
            List of EventLogEntry objects
        """
        events = []
        
        try:
            # Build wevtutil command
            cmd = ['wevtutil', 'qe', log_name, f'/c:{max_events}', '/rd:true', '/f:text']
            
            if event_id_filter:
                query = f"*[System[{event_id_filter}]]"
                cmd.extend(['/q:' + query])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10,
                check=False
            )
            
            if result.returncode == 0:
                events = self._parse_event_output(result.stdout, log_name)
            else:
                print(f"Event log query failed for {log_name}: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"Event log query timed out for {log_name}")
        except Exception as e:
            print(f"Error querying {log_name}: {e}")
        
        return events
    
    def _parse_event_output(self, output: str, log_name: str) -> List[EventLogEntry]:
        """
        Parse wevtutil text output into EventLogEntry objects.
        
        Args:
            output: Text output from wevtutil
            log_name: Name of the log source
            
        Returns:
            List of EventLogEntry objects
        """
        events = []
        current_event = {}
        
        try:
            lines = output.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    # Empty line indicates end of event
                    if current_event:
                        events.append(self._create_event_entry(current_event, log_name))
                        current_event = {}
                    continue
                
                # Parse key-value pairs
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        current_event[key] = value
            
            # Add last event if exists
            if current_event:
                events.append(self._create_event_entry(current_event, log_name))
        except Exception as e:
            print(f"Error parsing event output: {e}")
        
        return events
    
    def _create_event_entry(self, event_data: Dict[str, str],
                           log_name: str) -> Optional[EventLogEntry]:
        """
        Create EventLogEntry from parsed event data.
        
        Args:
            event_data: Dictionary of parsed event fields
            log_name: Name of the log source
            
        Returns:
            EventLogEntry object or None
        """
        try:
            # Extract event ID
            event_id_str = event_data.get('Event ID', '0')
            event_id = int(event_id_str)
            
            # Extract timestamp
            date_str = event_data.get('Date', '')
            timestamp = self._parse_event_timestamp(date_str)
            
            # Extract other fields
            level = event_data.get('Level', 'Information')
            source = event_data.get('Source', log_name)
            message = event_data.get('Description', 'No description')
            
            return EventLogEntry(
                event_id=event_id,
                timestamp=timestamp,
                level=level,
                source=source,
                message=message,
                raw_data=event_data
            )
        except Exception as e:
            print(f"Error creating event entry: {e}")
            return None
    
    def _parse_event_timestamp(self, date_str: str) -> float:
        """
        Parse event timestamp string.
        
        Args:
            date_str: Date string from event log
            
        Returns:
            Unix timestamp
        """
        try:
            # Try multiple date formats
            formats = [
                '%m/%d/%Y %I:%M:%S %p',  # US format with AM/PM
                '%Y-%m-%d %H:%M:%S',      # ISO format
                '%d/%m/%Y %H:%M:%S',      # EU format
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.timestamp()
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            return time.time()
        except Exception:
            return time.time()
    
    def get_bcd_error_events(self) -> List[EventLogEntry]:
        """
        Get BCD-related error events.
        
        Returns:
            List of EventLogEntry objects for BCD errors
        """
        if not self.has_permission:
            return []
        
        try:
            # Query for BCD-related errors in System log
            cmd = [
                'wevtutil', 'qe', 'System', '/c:50', '/rd:true', '/f:text',
                '/q:*[System[Provider[@Name="Microsoft-Windows-Kernel-Boot"] and Level=2]]'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10,
                check=False
            )
            
            if result.returncode == 0:
                return self._parse_event_output(result.stdout, 'System')
            else:
                return []
        except Exception as e:
            print(f"Error getting BCD error events: {e}")
            return []
    
    def get_system_boot_events(self, boot_count: int = 5) -> List[EventLogEntry]:
        """
        Get system boot events for the last N boots.
        
        Args:
            boot_count: Number of recent boots to retrieve events for
            
        Returns:
            List of EventLogEntry objects
        """
        # Get boot start events (Event ID 6005 or 12)
        boot_events = self.collect_boot_events(max_events=boot_count * 10)
        
        # Filter to just boot start events
        boot_start_events = [
            e for e in boot_events
            if e.event_id in [6005, 6009, 12]
        ]
        
        return boot_start_events[:boot_count]
    
    def save_events_for_session(self, session_id: str, events: List[EventLogEntry]):
        """
        Save event logs for a specific boot session.
        
        Args:
            session_id: Boot session identifier
            events: List of EventLogEntry objects to save
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            
            data = {
                'session_id': session_id,
                'saved_timestamp': time.time(),
                'events': [e.to_dict() for e in events]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Clean up old session files (keep only last 5)
            self._cleanup_old_sessions()
        except Exception as e:
            print(f"Error saving events for session: {e}")
    
    def load_events_for_session(self, session_id: str) -> List[EventLogEntry]:
        """
        Load event logs for a specific boot session.
        
        Args:
            session_id: Boot session identifier
            
        Returns:
            List of EventLogEntry objects
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [EventLogEntry.from_dict(e) for e in data.get('events', [])]
        except Exception as e:
            print(f"Error loading events for session: {e}")
            return []
    
    def _cleanup_old_sessions(self):
        """Remove old session event log files, keeping only the last 5."""
        try:
            files = sorted(
                Path(self.storage_dir).glob('boot_*.json'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Keep only the 5 most recent files
            for old_file in files[5:]:
                old_file.unlink()
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
