"""
DiagnosticsViewer - GUI component for viewing and exporting diagnostic logs
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import zipfile
import shutil
from datetime import datetime
from typing import List, Optional

from log_manager import LogManager, LogEntry
from boot_session_tracker import BootSessionTracker, BootSession
from event_log_collector import WindowsEventLogCollector, EventLogEntry


class DiagnosticsViewer:
    """User interface for viewing and exporting diagnostic logs."""
    
    def __init__(self, parent):
        """
        Initialize DiagnosticsViewer window.
        
        Args:
            parent: Parent tkinter window
        """
        self.parent = parent
        self.window = None
        
        # Initialize managers
        self.log_manager = LogManager()
        self.session_tracker = BootSessionTracker()
        self.event_collector = WindowsEventLogCollector()
        
        # Current selection
        self.current_session: Optional[BootSession] = None
        self.current_category = "ALL"
        
    def show(self):
        """Show the diagnostics viewer window."""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("PyBootManager - Diagnostics")
        self.window.geometry("1000x700")
        self.window.transient(self.parent)
        
        self._create_ui()
        self._load_sessions()
    
    def _create_ui(self):
        """Create the user interface."""
        # Header
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Diagnostic Logs & Boot Session Viewer",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=12)
        
        # Main content area
        content_frame = tk.Frame(self.window, padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Boot Sessions
        left_panel = tk.Frame(content_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self._create_session_panel(left_panel)
        
        # Right panel - Logs and Details
        right_panel = tk.Frame(content_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self._create_details_panel(right_panel)
    
    def _create_session_panel(self, parent):
        """Create boot session selection panel."""
        tk.Label(
            parent,
            text="Boot Sessions",
            font=("Arial", 11, "bold")
        ).pack(pady=(0, 10))
        
        # Session list
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.session_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 9),
            selectmode=tk.SINGLE
        )
        self.session_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.session_listbox.yview)
        
        self.session_listbox.bind('<<ListboxSelect>>', self._on_session_select)
        
        # Buttons
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="Refresh",
            command=self._load_sessions,
            bg="#3498db",
            fg="white",
            font=("Arial", 9)
        ).pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            btn_frame,
            text="Export All",
            command=self._export_diagnostics,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 9)
        ).pack(fill=tk.X)
    
    def _create_details_panel(self, parent):
        """Create details panel with tabs."""
        # Session info frame
        info_frame = tk.LabelFrame(
            parent,
            text="Session Information",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.session_info_label = tk.Label(
            info_frame,
            text="Select a boot session to view details",
            font=("Arial", 9),
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.session_info_label.pack(fill=tk.X)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Operation Logs tab
        self._create_operation_logs_tab()
        
        # Event Logs tab
        self._create_event_logs_tab()
        
        # Timeline tab
        self._create_timeline_tab()
    
    def _create_operation_logs_tab(self):
        """Create operation logs tab."""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Operation Logs")
        
        # Filter frame
        filter_frame = tk.Frame(tab_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Category:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.category_var = tk.StringVar(value="ALL")
        categories = ["ALL", "USER_ACTION", "BCD_OPERATION", "BACKUP_OPERATION", "ERROR", "INFO"]
        
        category_menu = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=20
        )
        category_menu.pack(side=tk.LEFT, padx=(0, 10))
        category_menu.bind('<<ComboboxSelected>>', self._on_category_change)
        
        tk.Button(
            filter_frame,
            text="Refresh Logs",
            command=self._load_operation_logs,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        # Logs treeview
        tree_frame = tk.Frame(tab_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("Time", "Level", "Category", "Message")
        self.ops_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode=tk.BROWSE
        )
        
        self.ops_tree.heading("Time", text="Timestamp")
        self.ops_tree.heading("Level", text="Level")
        self.ops_tree.heading("Category", text="Category")
        self.ops_tree.heading("Message", text="Message")
        
        self.ops_tree.column("Time", width=150)
        self.ops_tree.column("Level", width=80)
        self.ops_tree.column("Category", width=150)
        self.ops_tree.column("Message", width=400)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.ops_tree.yview)
        self.ops_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ops_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ops_tree.bind('<<TreeviewSelect>>', self._on_log_select)
        
        # Details text
        details_frame = tk.Frame(tab_frame)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(details_frame, text="Log Details:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.log_details_text = tk.Text(details_frame, height=8, font=("Courier", 8), wrap=tk.WORD)
        self.log_details_text.pack(fill=tk.X)
    
    def _create_event_logs_tab(self):
        """Create Windows Event Logs tab."""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Windows Event Logs")
        
        # Info label
        info_label = tk.Label(
            tab_frame,
            text="Boot-related Windows Event Log entries for this session",
            font=("Arial", 9),
            fg="#555"
        )
        info_label.pack(pady=10)
        
        # Events treeview
        tree_frame = tk.Frame(tab_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("Event ID", "Time", "Level", "Source", "Message")
        self.events_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings"
        )
        
        self.events_tree.heading("Event ID", text="Event ID")
        self.events_tree.heading("Time", text="Timestamp")
        self.events_tree.heading("Level", text="Level")
        self.events_tree.heading("Source", text="Source")
        self.events_tree.heading("Message", text="Message")
        
        self.events_tree.column("Event ID", width=80)
        self.events_tree.column("Time", width=150)
        self.events_tree.column("Level", width=100)
        self.events_tree.column("Source", width=200)
        self.events_tree.column("Message", width=350)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_timeline_tab(self):
        """Create timeline view tab."""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Timeline & Correlation")
        
        # Timeline text
        timeline_frame = tk.Frame(tab_frame)
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(timeline_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timeline_text = tk.Text(
            timeline_frame,
            font=("Courier", 9),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.timeline_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.timeline_text.yview)
        
        # Configure text tags for highlighting
        self.timeline_text.tag_config("mismatch", background="#ffe6e6", foreground="#c0392b")
        self.timeline_text.tag_config("match", background="#e6ffe6", foreground="#27ae60")
        self.timeline_text.tag_config("header", font=("Courier", 10, "bold"))
    
    def _load_sessions(self):
        """Load boot sessions into the listbox."""
        self.session_listbox.delete(0, tk.END)
        
        sessions = self.session_tracker.get_boot_history(count=5)
        
        if not sessions:
            self.session_listbox.insert(tk.END, "No boot sessions found")
            return
        
        for session in sessions:
            status = ""
            if session.boot_match_status == "MISMATCH":
                status = " ⚠ MISMATCH"
            elif session.boot_match_status == "MATCH":
                status = " ✓ MATCH"
            
            display = f"{session.get_formatted_time()}{status}"
            self.session_listbox.insert(tk.END, display)
        
        # Select first session by default
        if sessions:
            self.session_listbox.selection_set(0)
            self._on_session_select(None)
    
    def _on_session_select(self, event):
        """Handle boot session selection."""
        selection = self.session_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        sessions = self.session_tracker.get_boot_history(count=5)
        
        if idx < len(sessions):
            self.current_session = sessions[idx]
            self._update_session_info()
            self._load_operation_logs()
            self._load_event_logs()
            self._update_timeline()
    
    def _update_session_info(self):
        """Update session information display."""
        if not self.current_session:
            return
        
        info = f"Session ID: {self.current_session.session_id}\n"
        info += f"Boot Time: {self.current_session.get_formatted_time()}\n"
        info += f"Status: {self.current_session.boot_match_status}\n"
        
        if self.current_session.actual_boot_entry:
            info += f"Actual Boot: {self.current_session.actual_boot_entry}\n"
        
        if self.current_session.expected_boot_entry:
            info += f"Expected Boot: {self.current_session.expected_boot_entry}\n"
        
        if self.current_session.diagnosis:
            info += f"Diagnosis: {self.current_session.diagnosis}\n"
        
        info += f"Previous Operations: {len(self.current_session.previous_operations)}"
        
        self.session_info_label.config(text=info)
    
    def _load_operation_logs(self):
        """Load operation logs for current session."""
        # Clear existing
        for item in self.ops_tree.get_children():
            self.ops_tree.delete(item)
        
        if not self.current_session:
            return
        
        # Get logs for this session
        logs = self.log_manager.get_logs_by_session(self.current_session.session_id)
        
        # Apply category filter
        category = self.category_var.get()
        if category != "ALL":
            logs = [log for log in logs if log.category == category]
        
        # Populate treeview
        for log in logs:
            values = (
                log.get_formatted_time(),
                log.log_level,
                log.category,
                log.message
            )
            
            # Add color tags for errors
            tag = 'error' if log.log_level == 'ERROR' else ''
            self.ops_tree.insert("", tk.END, values=values, tags=(tag,))
        
        # Configure error tag
        self.ops_tree.tag_configure('error', background='#ffe6e6')
    
    def _load_event_logs(self):
        """Load Windows Event Logs for current session."""
        # Clear existing
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        if not self.current_session:
            return
        
        # Load events from storage
        events = self.event_collector.load_events_for_session(self.current_session.session_id)
        
        # Populate treeview
        for event in events:
            values = (
                event.event_id,
                event.get_formatted_time(),
                event.level,
                event.source,
                event.message[:100]  # Truncate long messages
            )
            self.events_tree.insert("", tk.END, values=values)
    
    def _update_timeline(self):
        """Update timeline view with operation correlation."""
        self.timeline_text.delete('1.0', tk.END)
        
        if not self.current_session:
            return
        
        # Header
        self.timeline_text.insert(tk.END, f"BOOT SESSION TIMELINE\n", "header")
        self.timeline_text.insert(tk.END, f"{'=' * 80}\n\n")
        
        # Boot time
        self.timeline_text.insert(tk.END, f"Boot Time: {self.current_session.get_formatted_time()}\n")
        self.timeline_text.insert(tk.END, f"Session ID: {self.current_session.session_id}\n\n")
        
        # Previous operations
        if self.current_session.previous_operations:
            self.timeline_text.insert(tk.END, "PREVIOUS OPERATIONS:\n", "header")
            self.timeline_text.insert(tk.END, f"{'-' * 80}\n")
            
            for op in self.current_session.previous_operations:
                op_time = datetime.fromtimestamp(op['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                self.timeline_text.insert(tk.END, f"{op_time} - {op['operation_type']}\n")
                self.timeline_text.insert(tk.END, f"  Target: {op['target_entry']}\n\n")
        
        # Boot result
        self.timeline_text.insert(tk.END, "\nBOOT RESULT:\n", "header")
        self.timeline_text.insert(tk.END, f"{'-' * 80}\n")
        
        if self.current_session.actual_boot_entry:
            self.timeline_text.insert(tk.END, f"Actual Boot Entry: {self.current_session.actual_boot_entry}\n")
        
        if self.current_session.expected_boot_entry:
            self.timeline_text.insert(tk.END, f"Expected Boot Entry: {self.current_session.expected_boot_entry}\n")
        
        # Match status
        status_text = f"\nStatus: {self.current_session.boot_match_status}\n"
        tag = "match" if self.current_session.boot_match_status == "MATCH" else "mismatch"
        self.timeline_text.insert(tk.END, status_text, tag)
        
        # Diagnosis
        if self.current_session.diagnosis:
            self.timeline_text.insert(tk.END, f"\nDiagnosis: {self.current_session.diagnosis}\n", "mismatch")
    
    def _on_category_change(self, event):
        """Handle category filter change."""
        self._load_operation_logs()
    
    def _on_log_select(self, event):
        """Handle log entry selection to show details."""
        selection = self.ops_tree.selection()
        if not selection:
            return
        
        # Get the selected log entry
        item = self.ops_tree.item(selection[0])
        timestamp_str = item['values'][0]
        
        # Find matching log entry
        if self.current_session:
            logs = self.log_manager.get_logs_by_session(self.current_session.session_id)
            
            for log in logs:
                if log.get_formatted_time() == timestamp_str:
                    # Display details
                    self.log_details_text.delete('1.0', tk.END)
                    
                    details_text = f"Operation ID: {log.operation_id}\n"
                    details_text += f"Timestamp: {log.get_formatted_time()}\n"
                    details_text += f"Level: {log.log_level}\n"
                    details_text += f"Category: {log.category}\n"
                    details_text += f"Message: {log.message}\n\n"
                    details_text += "Details:\n"
                    
                    import json
                    details_text += json.dumps(log.details, indent=2)
                    
                    self.log_details_text.insert('1.0', details_text)
                    break
    
    def _export_diagnostics(self):
        """Export all diagnostic data to a ZIP file."""
        # Ask for save location
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"pybootmanager_diagnostics_{timestamp}.zip"
        
        file_path = filedialog.asksaveasfilename(
            parent=self.window,
            title="Export Diagnostics",
            defaultextension=".zip",
            initialfile=default_name,
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Create ZIP file
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add log directory contents
                log_dir = self.log_manager.get_log_directory()
                
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        file_path_abs = os.path.join(root, file)
                        arcname = os.path.relpath(file_path_abs, log_dir)
                        zipf.write(file_path_abs, arcname)
            
            messagebox.showinfo(
                "Export Successful",
                f"Diagnostics exported successfully to:\n{file_path}",
                parent=self.window
            )
        except Exception as e:
            messagebox.showerror(
                "Export Failed",
                f"Failed to export diagnostics:\n{str(e)}",
                parent=self.window
            )
