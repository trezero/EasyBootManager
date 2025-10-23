"""
GUI - Main application window and user interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from bcd_manager import BCDManager, BootEntry
from backup_manager import BackupManager, BackupInfo
from privilege_manager import PrivilegeManager


class PyBootManagerGUI:
    """Main GUI application for PyBootManager."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PyBootManager v1.0")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Initialize managers
        self.bcd_manager = BCDManager()
        self.backup_manager = BackupManager()
        
        # Variables
        self.selected_entry = None
        self.boot_entries = []
        
        # Create UI
        self._create_ui()
        
        # Load initial data
        self.refresh_boot_entries()
        
    def _create_ui(self):
        """Create the user interface."""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="PyBootManager",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main content area
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current Configuration Panel
        config_frame = tk.LabelFrame(
            content_frame,
            text="Current Configuration",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.default_label = tk.Label(
            config_frame,
            text="Default: Loading...",
            font=("Arial", 9)
        )
        self.default_label.pack(anchor=tk.W)
        
        self.timeout_label = tk.Label(
            config_frame,
            text="Timeout: Loading...",
            font=("Arial", 9)
        )
        self.timeout_label.pack(anchor=tk.W)
        
        # Boot Entries List
        entries_frame = tk.LabelFrame(
            content_frame,
            text="Available Boot Entries",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        entries_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create Treeview for boot entries
        columns = ("Description", "Identifier", "Status")
        self.entries_tree = ttk.Treeview(
            entries_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Configure columns
        self.entries_tree.heading("Description", text="Description")
        self.entries_tree.heading("Identifier", text="Identifier")
        self.entries_tree.heading("Status", text="Status")
        
        self.entries_tree.column("Description", width=200)
        self.entries_tree.column("Identifier", width=250)
        self.entries_tree.column("Status", width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=scrollbar.set)
        
        self.entries_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.entries_tree.bind('<<TreeviewSelect>>', self._on_entry_select)
        
        # Action Buttons Frame
        buttons_frame = tk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Row 1 buttons
        row1_frame = tk.Frame(buttons_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.boot_once_btn = tk.Button(
            row1_frame,
            text="Boot Once",
            command=self.boot_once,
            width=15,
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.boot_once_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.set_default_btn = tk.Button(
            row1_frame,
            text="Set Default",
            command=self.set_default,
            width=15,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.set_default_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.timeout_btn = tk.Button(
            row1_frame,
            text="Configure Timeout",
            command=self.configure_timeout,
            width=15,
            bg="#f39c12",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.timeout_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_btn = tk.Button(
            row1_frame,
            text="Refresh",
            command=self.refresh_boot_entries,
            width=15,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.refresh_btn.pack(side=tk.LEFT)
        
        # Row 2 buttons
        row2_frame = tk.Frame(buttons_frame)
        row2_frame.pack(fill=tk.X)
        
        self.backup_btn = tk.Button(
            row2_frame,
            text="Create Backup",
            command=self.create_backup,
            width=15,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.backup_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.restore_btn = tk.Button(
            row2_frame,
            text="Restore Backup",
            command=self.restore_backup,
            width=15,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.restore_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.view_backups_btn = tk.Button(
            row2_frame,
            text="View Backups",
            command=self.view_backups,
            width=15,
            bg="#34495e",
            fg="white",
            font=("Arial", 9, "bold")
        )
        self.view_backups_btn.pack(side=tk.LEFT)
        
        # Status Bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _on_entry_select(self, event):
        """Handle boot entry selection."""
        selection = self.entries_tree.selection()
        if selection:
            item = self.entries_tree.item(selection[0])
            values = item['values']
            # Find the corresponding boot entry
            for entry in self.boot_entries:
                if entry.description == values[0]:
                    self.selected_entry = entry
                    break
    
    def refresh_boot_entries(self):
        """Refresh the boot entries list."""
        self.status_bar.config(text="Loading boot entries...")
        self.root.update()
        
        # Clear existing entries
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        # Get boot entries
        self.boot_entries = self.bcd_manager.get_boot_entries()
        
        # Get current configuration
        default_id = self.bcd_manager.get_current_default()
        timeout = self.bcd_manager.get_timeout()
        
        # Update configuration labels
        default_desc = "Unknown"
        for entry in self.boot_entries:
            if entry.is_default:
                default_desc = entry.description
                break
        
        self.default_label.config(text=f"Default: {default_desc}")
        self.timeout_label.config(text=f"Timeout: {timeout if timeout is not None else 'Unknown'} seconds")
        
        # Populate treeview
        for entry in self.boot_entries:
            status = "DEFAULT" if entry.is_default else ""
            self.entries_tree.insert(
                "",
                tk.END,
                values=(entry.description, entry.identifier, status)
            )
        
        self.status_bar.config(text=f"Ready - {len(self.boot_entries)} boot entries found")
    
    def boot_once(self):
        """Set the selected entry to boot once."""
        if not self.selected_entry:
            messagebox.showwarning("No Selection", "Please select a boot entry first.")
            return
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Boot Once",
            f"Boot '{self.selected_entry.description}' on next restart?\n\n"
            f"The system will boot this OS once, then return to the default."
        )
        
        if not result:
            return
        
        # Create automatic backup
        self.status_bar.config(text="Creating automatic backup...")
        self.root.update()
        backup = self.backup_manager.create_auto_backup()
        
        if not backup:
            messagebox.showerror("Backup Failed", "Failed to create automatic backup. Operation cancelled.")
            self.status_bar.config(text="Ready")
            return
        
        # Set boot once
        self.status_bar.config(text="Setting boot once...")
        self.root.update()
        
        success = self.bcd_manager.set_boot_once(self.selected_entry.identifier)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"'{self.selected_entry.description}' will boot on next restart.\n\n"
                f"Backup created: {backup.name}"
            )
            self.status_bar.config(text="Boot once configured successfully")
        else:
            messagebox.showerror("Error", "Failed to set boot once. Check administrator privileges.")
            self.status_bar.config(text="Operation failed")
    
    def set_default(self):
        """Set the selected entry as default."""
        if not self.selected_entry:
            messagebox.showwarning("No Selection", "Please select a boot entry first.")
            return
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Set Default",
            f"Set '{self.selected_entry.description}' as the default boot OS?\n\n"
            f"This will be the permanent default until changed."
        )
        
        if not result:
            return
        
        # Create automatic backup
        self.status_bar.config(text="Creating automatic backup...")
        self.root.update()
        backup = self.backup_manager.create_auto_backup()
        
        if not backup:
            messagebox.showerror("Backup Failed", "Failed to create automatic backup. Operation cancelled.")
            self.status_bar.config(text="Ready")
            return
        
        # Set default
        self.status_bar.config(text="Setting default boot entry...")
        self.root.update()
        
        success = self.bcd_manager.set_default(self.selected_entry.identifier)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"'{self.selected_entry.description}' is now the default boot OS.\n\n"
                f"Backup created: {backup.name}"
            )
            self.refresh_boot_entries()
        else:
            messagebox.showerror("Error", "Failed to set default. Check administrator privileges.")
            self.status_bar.config(text="Operation failed")
    
    def configure_timeout(self):
        """Configure boot menu timeout."""
        current_timeout = self.bcd_manager.get_timeout()
        
        # Ask for new timeout value
        new_timeout = simpledialog.askinteger(
            "Configure Timeout",
            f"Enter boot menu timeout in seconds (0-999):\n\nCurrent: {current_timeout if current_timeout is not None else 'Unknown'}",
            minvalue=0,
            maxvalue=999,
            initialvalue=current_timeout if current_timeout is not None else 30
        )
        
        if new_timeout is None:
            return
        
        # Create automatic backup
        self.status_bar.config(text="Creating automatic backup...")
        self.root.update()
        backup = self.backup_manager.create_auto_backup()
        
        if not backup:
            messagebox.showerror("Backup Failed", "Failed to create automatic backup. Operation cancelled.")
            self.status_bar.config(text="Ready")
            return
        
        # Set timeout
        self.status_bar.config(text="Setting timeout...")
        self.root.update()
        
        success = self.bcd_manager.set_timeout(new_timeout)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"Boot menu timeout set to {new_timeout} seconds.\n\n"
                f"Backup created: {backup.name}"
            )
            self.refresh_boot_entries()
        else:
            messagebox.showerror("Error", "Failed to set timeout. Check administrator privileges.")
            self.status_bar.config(text="Operation failed")
    
    def create_backup(self):
        """Create a manual backup."""
        # Ask for backup name
        name = simpledialog.askstring(
            "Create Backup",
            "Enter a name for this backup:",
            initialvalue=f"manual_backup"
        )
        
        if not name:
            return
        
        self.status_bar.config(text="Creating backup...")
        self.root.update()
        
        backup = self.backup_manager.create_backup(name, "Manual backup")
        
        if backup:
            messagebox.showinfo(
                "Success",
                f"Backup created successfully!\n\n"
                f"Name: {backup.name}\n"
                f"Time: {backup.get_formatted_time()}"
            )
            self.status_bar.config(text="Backup created successfully")
        else:
            messagebox.showerror("Error", "Failed to create backup. Check administrator privileges.")
            self.status_bar.config(text="Backup failed")
    
    def restore_backup(self):
        """Restore from a backup."""
        backups = self.backup_manager.list_backups()
        
        if not backups:
            messagebox.showinfo("No Backups", "No backups available to restore.")
            return
        
        # Create backup selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Restore Backup")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select a backup to restore:", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Create listbox for backups
        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 9))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate backups
        for backup in backups:
            listbox.insert(tk.END, f"{backup.name} - {backup.get_formatted_time()}")
        
        selected_backup = [None]
        
        def on_restore():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a backup to restore.")
                return
            
            idx = selection[0]
            selected_backup[0] = backups[idx]
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Restore", command=on_restore, width=15, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel, width=15, bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        if not selected_backup[0]:
            return
        
        # Confirm restoration
        result = messagebox.askyesno(
            "Confirm Restore",
            f"Restore backup '{selected_backup[0].name}'?\n\n"
            f"Created: {selected_backup[0].get_formatted_time()}\n\n"
            f"WARNING: This will replace your current boot configuration!"
        )
        
        if not result:
            return
        
        # Restore backup
        self.status_bar.config(text="Restoring backup...")
        self.root.update()
        
        success = self.backup_manager.restore_backup(selected_backup[0].name)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"Backup restored successfully!\n\n"
                f"Your boot configuration has been restored to:\n{selected_backup[0].get_formatted_time()}"
            )
            self.refresh_boot_entries()
        else:
            messagebox.showerror("Error", "Failed to restore backup. Check administrator privileges.")
            self.status_bar.config(text="Restore failed")
    
    def view_backups(self):
        """View all available backups."""
        backups = self.backup_manager.list_backups()
        
        if not backups:
            messagebox.showinfo("No Backups", "No backups available.")
            return
        
        # Create backup viewer dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("View Backups")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        
        tk.Label(dialog, text="Available Backups", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create treeview for backups
        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("Name", "Timestamp", "Description")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        tree.heading("Name", text="Name")
        tree.heading("Timestamp", text="Created")
        tree.heading("Description", text="Description")
        
        tree.column("Name", width=150)
        tree.column("Timestamp", width=150)
        tree.column("Description", width=250)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate backups
        for backup in backups:
            tree.insert(
                "",
                tk.END,
                values=(backup.name, backup.get_formatted_time(), backup.description)
            )
        
        tk.Button(dialog, text="Close", command=dialog.destroy, width=15).pack(pady=10)


def main():
    """Main entry point for GUI application."""
    # Check for admin privileges
    if not PrivilegeManager.is_admin():
        messagebox.showerror(
            "Administrator Required",
            "PyBootManager requires administrator privileges to manage boot configuration.\n\n"
            "Please restart the application as administrator."
        )
        sys.exit(1)
    
    # Create and run GUI
    root = tk.Tk()
    app = PyBootManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
