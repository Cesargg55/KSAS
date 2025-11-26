import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os

class CandidateManagerWindow:
    """
    Window for managing detected candidates.
    Allows reviewing, marking as discovered/new, and adding notes.
    """
    
    def __init__(self, candidate_db):
        self.db = candidate_db
        self.window = tk.Toplevel()
        self.window.title("KSAS - Candidate Manager")
        self.window.geometry("900x600")
        self.window.configure(bg='#1a1a1a')
        
        self.setup_ui()
        self.refresh_list()
    
    def setup_ui(self):
        """Create UI layout."""
        
        # Title
        title = tk.Label(self.window, text="🌟 Candidate Manager 🌟",
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=10)
        
        # Statistics
        stats_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_labels = {}
        stat_container = tk.Frame(stats_frame, bg='#2a2a2a')
        stat_container.pack(pady=5)
        
        for key, label in [('total', 'Total'), ('unreviewed', 'Unreviewed'), 
                          ('reviewed', 'Reviewed'), ('potentially_new', 'Potentially New')]:
            frame = tk.Frame(stat_container, bg='#2a2a2a')
            frame.pack(side=tk.LEFT, padx=15)
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 9), 
                    fg='#aaaaaa', bg='#2a2a2a').pack()
            self.stats_labels[key] = tk.Label(frame, text="0", font=('Arial', 12, 'bold'),
                                             fg='#00ff00', bg='#2a2a2a')
            self.stats_labels[key].pack()
        
        # Filter buttons
        filter_frame = tk.Frame(self.window, bg='#1a1a1a')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter:", fg='white', bg='#1a1a1a').pack(side=tk.LEFT, padx=5)
        
        tk.Button(filter_frame, text="All", command=lambda: self.apply_filter('all'),
                 bg='#444444', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(filter_frame, text="Unreviewed", command=lambda: self.apply_filter('unreviewed'),
                 bg='#ff6600', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(filter_frame, text="Reviewed", command=lambda: self.apply_filter('reviewed'),
                 bg='#00aa00', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(filter_frame, text="Potentially New", command=lambda: self.apply_filter('new'),
                 bg='#ffaa00', fg='black').pack(side=tk.LEFT, padx=2)
        
        # Candidate list
        list_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.SUNKEN, borderwidth=2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for candidates
        columns = ('TIC ID', 'Period', 'Depth', 'SNR', 'Reviewed', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('TIC ID', text='TIC ID')
        self.tree.heading('Period', text='Period (d)')
        self.tree.heading('Depth', text='Depth')
        self.tree.heading('SNR', text='SNR')
        self.tree.heading('Reviewed', text='Reviewed')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('TIC ID', width=150)
        self.tree.column('Period', width=100)
        self.tree.column('Depth', width=100)
        self.tree.column('SNR', width=80)
        self.tree.column('Reviewed', width=100)
        self.tree.column('Status', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Details panel
        details_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(details_frame, text="Selected Candidate:", font=('Arial', 10, 'bold'),
                fg='#ffaa00', bg='#2a2a2a').pack(anchor=tk.W, padx=5, pady=2)
        
        self.details_text = tk.Label(details_frame, text="Select a candidate to view details",
                                     font=('Courier', 9), fg='white', bg='#1a1a1a',
                                     justify=tk.LEFT, anchor=tk.W)
        self.details_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Action buttons
        action_frame = tk.Frame(self.window, bg='#1a1a1a')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(action_frame, text="✓ Mark as Discovered", command=self.mark_discovered,
                 bg='#aa0000', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="★ Mark as NEW", command=self.mark_new,
                 bg='#00aa00', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="📂 Open Report", command=self.open_report,
                 bg='#0066cc', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="🔄 Refresh", command=self.refresh_list,
                 bg='#666666', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Help
        from ksas.help_system import HelpSystem
        HelpSystem.create_help_button(action_frame, 'discovery').pack(side=tk.RIGHT, padx=5)
        
        self.current_filter = 'all'
        self.selected_tic = None
    
    def refresh_list(self):
        """Refresh the candidate list."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get candidates based on filter
        if self.current_filter == 'all':
            candidates = self.db.get_all_candidates()
        elif self.current_filter == 'unreviewed':
            candidates = self.db.get_unreviewed()
        elif self.current_filter == 'reviewed':
            candidates = self.db.get_reviewed()
        elif self.current_filter == 'new':
            candidates = self.db.get_potentially_new()
        else:
            candidates = self.db.get_all_candidates()
        
        # Populate tree
        for tic_id, data in candidates.items():
            reviewed = "Yes" if data['reviewed'] else "No"
            
            if data['is_discovered'] is None:
                status = "Unknown"
            elif data['is_discovered']:
                status = "Already Discovered"
            else:
                status = "⭐ POTENTIALLY NEW"
            
            self.tree.insert('', tk.END, values=(
                tic_id,
                f"{data['period']:.5f}",
                f"{data['depth']:.6f}",
                f"{data['snr']:.2f}",
                reviewed,
                status
            ))
        
        # Update stats
        stats = self.db.get_stats()
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))
    
    def apply_filter(self, filter_type):
        """Apply filter to candidate list."""
        self.current_filter = filter_type
        self.refresh_list()
    
    def on_select(self, event):
        """Handle selection event."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            tic_id = item['values'][0]
            self.selected_tic = tic_id
            
            # Show details
            data = self.db.get_candidate(tic_id)
            if data:
                details = f"TIC ID: {tic_id}\n"
                details += f"Period: {data['period']:.5f} days\n"
                details += f"Depth: {data['depth']:.6f}\n"
                details += f"SNR: {data['snr']:.2f}\n"
                details += f"Detection Time: {data['detection_time']}\n"
                details += f"Reviewed: {'Yes' if data['reviewed'] else 'No'}\n"
                if data['reviewed']:
                    status = "Already Discovered" if data['is_discovered'] else "⭐ Potentially NEW"
                    details += f"Status: {status}\n"
                    details += f"Review Time: {data['review_time']}\n"
                    if data['notes']:
                        details += f"Notes: {data['notes']}\n"
                
                self.details_text.config(text=details)
    
    def on_double_click(self, event):
        """Handle double-click to open report."""
        self.open_report()
    
    def mark_discovered(self):
        """Mark selected candidate as already discovered."""
        if not self.selected_tic:
            messagebox.showwarning("No Selection", "Please select a candidate first.")
            return
        
        # Ask for notes
        notes_window = tk.Toplevel(self.window)
        notes_window.title("Mark as Discovered")
        notes_window.geometry("400x200")
        
        tk.Label(notes_window, text=f"Marking {self.selected_tic} as DISCOVERED").pack(pady=10)
        tk.Label(notes_window, text="Notes (optional):").pack()
        
        notes_entry = tk.Text(notes_window, height=5, width=50)
        notes_entry.pack(pady=5)
        
        def save():
            notes = notes_entry.get("1.0", tk.END).strip()
            self.db.mark_reviewed(self.selected_tic, is_discovered=True, notes=notes)
            self.refresh_list()
            notes_window.destroy()
            messagebox.showinfo("Success", f"{self.selected_tic} marked as discovered.")
        
        tk.Button(notes_window, text="Save", command=save, bg='#00aa00', fg='white').pack(pady=10)
    
    def mark_new(self):
        """Mark selected candidate as potentially new."""
        if not self.selected_tic:
            messagebox.showwarning("No Selection", "Please select a candidate first.")
            return
        
        # Ask for notes
        notes_window = tk.Toplevel(self.window)
        notes_window.title("Mark as Potentially NEW")
        notes_window.geometry("400x200")
        
        tk.Label(notes_window, text=f"Marking {self.selected_tic} as POTENTIALLY NEW ⭐").pack(pady=10)
        tk.Label(notes_window, text="Notes (verification steps, observations, etc.):").pack()
        
        notes_entry = tk.Text(notes_window, height=5, width=50)
        notes_entry.pack(pady=5)
        
        def save():
            notes = notes_entry.get("1.0", tk.END).strip()
            self.db.mark_reviewed(self.selected_tic, is_discovered=False, notes=notes)
            self.refresh_list()
            notes_window.destroy()
            messagebox.showinfo("Success", f"{self.selected_tic} marked as potentially NEW!")
        
        tk.Button(notes_window, text="Save", command=save, bg='#00aa00', fg='white').pack(pady=10)
    
    def open_report(self):
        """Open the report image for selected candidate."""
        if not self.selected_tic:
            messagebox.showwarning("No Selection", "Please select a candidate first.")
            return
        
        # Find report file
        safe_id = self.selected_tic.replace(" ", "_")
        report_path = os.path.join("output", f"{safe_id}_report.png")
        
        if os.path.exists(report_path):
            # Open with default image viewer
            import platform
            if platform.system() == 'Windows':
                os.startfile(report_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{report_path}"')
            else:  # Linux
                os.system(f'xdg-open "{report_path}"')
        else:
            messagebox.showerror("File Not Found", f"Report not found:\n{report_path}")
    
    def show(self):
        """Show the window."""
        self.window.mainloop()
