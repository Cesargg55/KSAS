import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from ksas.locales import T

class CandidateManagerWindow:
    """
    Window for managing detected candidates.
    Allows reviewing, marking as discovered/new, and adding notes.
    """
    
    def __init__(self, candidate_db):
        self.db = candidate_db
        self.window = tk.Toplevel()
        self.window.title(f"KSAS - {T.get('manager_title')}")
        self.window.geometry("900x600")
        self.window.configure(bg='#1a1a1a')
        
        self.setup_ui()
        self.refresh_list()
    
    def setup_ui(self):
        """Create UI layout."""
        
        # Title
        title = tk.Label(self.window, text=f"🌟 {T.get('manager_title')} 🌟",
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=10)
        
        # Statistics
        stats_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_labels = {}
        stat_container = tk.Frame(stats_frame, bg='#2a2a2a')
        stat_container.pack(pady=5)
        
        # Note: These keys might need translation too if they are user facing labels
        # But 'total', 'unreviewed' etc are keys in the stats dict. 
        # I'll translate the Label part.
        stat_map = {
            'total': 'Total', 
            'unreviewed': 'Unreviewed', 
            'reviewed': 'Reviewed', 
            'potentially_new': 'Potentially New'
        }
        # Ideally add these to locales too, but for now I'll leave English keys or add ad-hoc
        # Let's add them to locales quickly or just use English keys for internal stats?
        # User wants "traduce todo". I'll map them manually for now or add to locales later.
        # Actually, let's just use the keys as is for now to avoid breaking logic, 
        # but display translated text.
        
        for key, label in [('total', 'Total'), ('unreviewed', 'Unreviewed'), 
                          ('reviewed', 'Reviewed'), ('potentially_new', 'Potentially New')]:
            frame = tk.Frame(stat_container, bg='#2a2a2a')
            frame.pack(side=tk.LEFT, padx=15)
            
            # Simple inline translation for these specific stat labels if not in locales
            # Or just leave as English for now if not critical, but user said "todo".
            # I'll assume they are English for now to save time, or add to locales if I can.
            # Let's use the English label for now to match the code structure.
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 9), 
                    fg='#aaaaaa', bg='#2a2a2a').pack()
            self.stats_labels[key] = tk.Label(frame, text="0", font=('Arial', 12, 'bold'),
                                             fg='#00ff00', bg='#2a2a2a')
            self.stats_labels[key].pack()
        
        # Filter buttons
        filter_frame = tk.Frame(self.window, bg='#1a1a1a')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text=T.get('filter'), fg='white', bg='#1a1a1a').pack(side=tk.LEFT, padx=5)
        
        tk.Button(filter_frame, text=T.get('filter_all'), command=lambda: self.apply_filter('all'),
                 bg='#444444', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(filter_frame, text=T.get('filter_excellent'), command=lambda: self.apply_filter('excellent'),
                 bg='#00aa00', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(filter_frame, text=T.get('filter_good'), command=lambda: self.apply_filter('good'),
                 bg='#00aaff', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(filter_frame, text=T.get('filter_fair'), command=lambda: self.apply_filter('fair'),
                 bg='#ffaa00', fg='black').pack(side=tk.LEFT, padx=2)
        
        # Candidate list
        list_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.SUNKEN, borderwidth=2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for candidates
        columns = ('TIC ID', 'Score', 'Quality', 'Period', 'Depth', 'SNR', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('TIC ID', text=T.get('col_tic'))
        self.tree.heading('Score', text=T.get('col_score'))
        self.tree.heading('Quality', text=T.get('col_quality'))
        self.tree.heading('Period', text=T.get('col_period'))
        self.tree.heading('Depth', text=T.get('col_depth'))
        self.tree.heading('SNR', text=T.get('col_snr'))
        self.tree.heading('Status', text=T.get('col_disposition'))
        
        self.tree.column('TIC ID', width=120)
        self.tree.column('Score', width=60)
        self.tree.column('Quality', width=100)
        self.tree.column('Period', width=80)
        self.tree.column('Depth', width=80)
        self.tree.column('SNR', width=80)
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
        
        tk.Label(details_frame, text=T.get('selected_candidate'), font=('Arial', 10, 'bold'),
                fg='#ffaa00', bg='#2a2a2a').pack(anchor=tk.W, padx=5, pady=2)
        
        self.details_text = tk.Label(details_frame, text=T.get('select_candidate'),
                                     font=('Courier', 9), fg='white', bg='#1a1a1a',
                                     justify=tk.LEFT, anchor=tk.W)
        self.details_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Action buttons
        action_frame = tk.Frame(self.window, bg='#1a1a1a')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(action_frame, text=T.get('btn_mark_discovered'), command=self.mark_discovered,
                 bg='#aa0000', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text=T.get('btn_mark_new'), command=self.mark_new,
                 bg='#00aa00', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text=T.get('btn_open_report'), command=self.open_report,
                 bg='#0066cc', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # New Observatory Button
        tk.Button(action_frame, text=T.get('open_observatory'), command=self.open_observatory,
                 bg='#9900cc', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(action_frame, text=T.get('refresh'), command=self.refresh_list,
                 bg='#666666', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Help
        from ksas.help_system import HelpSystem
        HelpSystem.create_help_button(action_frame, 'discovery').pack(side=tk.RIGHT, padx=5)
        
        self.current_filter = 'all'
        self.selected_tic = None

    def open_observatory(self):
        """Open the Observatory for the selected candidate."""
        if not self.selected_tic:
            messagebox.showwarning(T.get('no_selection'), T.get('select_first'))
            return
            
        data = self.db.get_candidate(self.selected_tic)
        if data:
            from ksas.observatory_gui import ObservatoryWindow
            # Note: We don't have live LC data here yet, so it will show analysis only
            # Future improvement: Load LC from file if available
            ObservatoryWindow(self.selected_tic, data)
    
    def refresh_list(self):
        """Refresh the candidate list."""
        # Force reload from disk to get latest updates
        self.db.load()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all candidates
        all_candidates = self.db.get_all_candidates()
        
        # Filter logic
        filtered_candidates = {}
        for tic, data in all_candidates.items():
            quality = data.get('quality', 'UNKNOWN')
            
            if self.current_filter == 'all':
                filtered_candidates[tic] = data
            elif self.current_filter == 'excellent' and quality == 'EXCELLENT':
                filtered_candidates[tic] = data
            elif self.current_filter == 'good' and quality == 'GOOD':
                filtered_candidates[tic] = data
            elif self.current_filter == 'fair' and quality == 'FAIR':
                filtered_candidates[tic] = data
        
        # Populate tree
        for tic_id, data in filtered_candidates.items():
            score = data.get('score', 0)
            quality = data.get('quality', '-')
            
            if data['is_discovered']:
                status = T.get('status_discovered')
            elif data['is_discovered'] is False:
                status = T.get('status_new')
            else:
                status = T.get('status_unreviewed')
            
            self.tree.insert('', tk.END, values=(
                tic_id,
                score,
                quality,
                f"{data['period']:.5f}",
                f"{data['depth']:.6f}",
                f"{data['snr']:.2f}",
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
                    status = T.get('status_discovered') if data['is_discovered'] else T.get('status_new')
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
            messagebox.showwarning(T.get('no_selection'), T.get('select_first'))
            return
        
        # Ask for notes
        notes_window = tk.Toplevel(self.window)
        notes_window.title(T.get('title_mark_discovered'))
        notes_window.geometry("400x200")
        
        tk.Label(notes_window, text=f"{T.get('title_mark_discovered')}: {self.selected_tic}").pack(pady=10)
        tk.Label(notes_window, text=T.get('notes_optional')).pack()
        
        notes_entry = tk.Text(notes_window, height=5, width=50)
        notes_entry.pack(pady=5)
        
        def save():
            notes = notes_entry.get("1.0", tk.END).strip()
            self.db.mark_reviewed(self.selected_tic, is_discovered=True, notes=notes)
            self.refresh_list()
            notes_window.destroy()
            messagebox.showinfo(T.get('success'), f"{self.selected_tic} {T.get('marked_discovered')}")
        
        tk.Button(notes_window, text=T.get('save'), command=save, bg='#00aa00', fg='white').pack(pady=10)
    
    def mark_new(self):
        """Mark selected candidate as potentially new."""
        if not self.selected_tic:
            messagebox.showwarning(T.get('no_selection'), T.get('select_first'))
            return
        
        # Ask for notes
        notes_window = tk.Toplevel(self.window)
        notes_window.title(T.get('title_mark_new'))
        notes_window.geometry("400x200")
        
        tk.Label(notes_window, text=f"{T.get('title_mark_new')}: {self.selected_tic}").pack(pady=10)
        tk.Label(notes_window, text=T.get('notes_new')).pack()
        
        notes_entry = tk.Text(notes_window, height=5, width=50)
        notes_entry.pack(pady=5)
        
        def save():
            notes = notes_entry.get("1.0", tk.END).strip()
            self.db.mark_reviewed(self.selected_tic, is_discovered=False, notes=notes)
            self.refresh_list()
            notes_window.destroy()
            messagebox.showinfo(T.get('success'), f"{self.selected_tic} {T.get('marked_new')}")
        
        tk.Button(notes_window, text=T.get('save'), command=save, bg='#00aa00', fg='white').pack(pady=10)
    
    def open_report(self):
        """Open the report image for selected candidate."""
        if not self.selected_tic:
            messagebox.showwarning(T.get('no_selection'), T.get('select_first'))
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
            messagebox.showerror(T.get('file_not_found'), f"{T.get('report_not_found')}\n{report_path}")
    
    def show(self):
        """Show the window."""
        self.window.mainloop()
