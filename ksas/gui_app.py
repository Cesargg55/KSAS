import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import queue
import time
import numpy as np

class KSASGui:
    """
    Real-time GUI for KSAS showing analysis progress.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KSAS - Kaesar Star Analysis System v3.0")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Thread-safe queue for updates
        self.update_queue = queue.Queue()
        
        # State
        self.paused = False
        self.current_target = "Waiting..."
        self.stats = {
            'analyzed': 0,
            'skipped': 0,
            'candidates': 0,
            'rejected': 0
        }
        
        self.setup_ui()
        
        # Start update loop
        self.root.after(100, self.process_queue)
        
        # Check for updates
        from ksas.updater import AutoUpdater
        from ksas.config import GITHUB_REPO, CURRENT_VERSION
        self.updater = AutoUpdater(CURRENT_VERSION, GITHUB_REPO)
        self.updater.check_async(self.root)
    
    def setup_ui(self):
        """Create UI layout."""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title = tk.Label(title_frame, text="🔬 KSAS - Autonomous Exoplanet Hunter 🔬",
                        font=('Arial', 20, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Statistics and Info
        left_panel = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, expand=False)
        left_panel.config(width=350)
        
        # Right panel - Visualization
        right_panel = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # === LEFT PANEL ===
        
        # Current Target
        target_label = tk.Label(left_panel, text="Current Target", 
                               font=('Arial', 12, 'bold'), fg='#ffaa00', bg='#2a2a2a')
        target_label.pack(pady=(10, 5))
        
        self.target_var = tk.StringVar(value=self.current_target)
        target_display = tk.Label(left_panel, textvariable=self.target_var,
                                 font=('Courier', 11), fg='white', bg='#1a1a1a',
                                 relief=tk.SUNKEN, padx=10, pady=5)
        target_display.pack(fill=tk.X, padx=10)
        
        # Statistics
        stats_label = tk.Label(left_panel, text="Statistics", 
                              font=('Arial', 12, 'bold'), fg='#ffaa00', bg='#2a2a2a')
        stats_label.pack(pady=(15, 5))
        
        stats_frame = tk.Frame(left_panel, bg='#1a1a1a', relief=tk.SUNKEN, borderwidth=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stat_labels = {}
        for key, label in [('analyzed', '📊 Session Analyzed'), ('total_analyzed', '🏆 Total (Historical)'),
                          ('skipped', '⏭️ Skipped'), ('candidates', '🌟 Candidates'), 
                          ('rejected', '❌ Rejected')]:
            row = tk.Frame(stats_frame, bg='#1a1a1a')
            row.pack(fill=tk.X, pady=2, padx=5)
            tk.Label(row, text=f"{label}:", font=('Arial', 10), fg='#aaaaaa', bg='#1a1a1a').pack(side=tk.LEFT)
            self.stat_labels[key] = tk.Label(row, text="0", font=('Arial', 10, 'bold'), 
                                             fg='#00ff00', bg='#1a1a1a')
            self.stat_labels[key].pack(side=tk.RIGHT)
        
        # Current Analysis
        analysis_label = tk.Label(left_panel, text="Analysis Status", 
                                 font=('Arial', 12, 'bold'), fg='#ffaa00', bg='#2a2a2a')
        analysis_label.pack(pady=(15, 5))
        
        self.status_var = tk.StringVar(value="Idle")
        status_display = tk.Label(left_panel, textvariable=self.status_var,
                                 font=('Courier', 9), fg='#00ff00', bg='#1a1a1a',
                                 relief=tk.SUNKEN, padx=10, pady=5, wraplength=300)
        status_display.pack(fill=tk.X, padx=10)
        
        # Results
        results_label = tk.Label(left_panel, text="Latest Results", 
                                font=('Arial', 12, 'bold'), fg='#ffaa00', bg='#2a2a2a')
        results_label.pack(pady=(15, 5))
        
        self.results_var = tk.StringVar(value="No results yet")
        results_display = tk.Label(left_panel, textvariable=self.results_var,
                                  font=('Courier', 8), fg='white', bg='#1a1a1a',
                                  relief=tk.SUNKEN, padx=10, pady=5, wraplength=300,
                                  justify=tk.LEFT)
        results_display.pack(fill=tk.BOTH, padx=10, expand=True)
        
        # Control Buttons
        control_frame = tk.Frame(left_panel, bg='#2a2a2a')
        control_frame.pack(pady=10)
        
        self.pause_btn = tk.Button(control_frame, text="⏸️ PAUSE", 
                                   command=self.toggle_pause,
                                   font=('Arial', 10, 'bold'), bg='#ff6600', fg='white')
        self.pause_btn.pack(pady=5)
        
        # Candidate Manager button
        self.manager_btn = tk.Button(control_frame, text="📋 Candidate Manager",
                                     command=self.open_candidate_manager,
                                     font=('Arial', 10, 'bold'), bg='#0066cc', fg='white')
        self.manager_btn.pack(pady=5)
        
        # TIC Verifier button
        self.verifier_btn = tk.Button(control_frame, text="🔍 TIC Verifier",
                                      command=self.open_tic_verifier,
                                      font=('Arial', 10, 'bold'), bg='#9900cc', fg='white')
        self.verifier_btn.pack(pady=5)
        
        # Manual Analyzer button
        self.manual_btn = tk.Button(control_frame, text="🔬 Re-analyze TIC",
                                    command=self.open_manual_analyzer,
                                    font=('Arial', 10, 'bold'), bg='#cc6600', fg='white')
        self.manual_btn.pack(pady=5)
        
        # Image Scanner button
        self.scanner_btn = tk.Button(control_frame, text="📊 Scan Candidates",
                                     command=self.open_image_scanner,
                                     font=('Arial', 10, 'bold'), bg='#cc00cc', fg='white')
        self.scanner_btn.pack(pady=5)
        
        # === HELP SECTION ===
        help_frame = tk.Frame(left_panel, bg='#2a2a2a')
        help_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
        
        from ksas.help_system import HelpSystem
        
        # General Help
        HelpSystem.create_help_button(help_frame, 'general').pack(side=tk.LEFT, padx=2)
        tk.Label(help_frame, text="How it works", fg='#aaaaaa', bg='#2a2a2a').pack(side=tk.LEFT, padx=5)
        
        # Discovery Help
        HelpSystem.create_help_button(help_frame, 'discovery').pack(side=tk.RIGHT, padx=2)
        tk.Label(help_frame, text="Found one?", fg='#aaaaaa', bg='#2a2a2a').pack(side=tk.RIGHT, padx=5)
        
        # Reference to candidate database (will be set externally)
        self.candidate_db = None
        
        # === RIGHT PANEL ===
        
        # Event Log
        log_label = tk.Label(right_panel, text="Event Log", 
                            font=('Arial', 12, 'bold'), fg='#ffaa00', bg='#2a2a2a')
        log_label.pack(pady=(5, 5))
        
        self.log_text = scrolledtext.ScrolledText(right_panel, height=12, 
                                                  bg='#0a0a0a', fg='#00ff00',
                                                  font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # Light Curve Visualization
        viz_label = tk.Label(right_panel, text="Light Curve Preview", 
                            font=('Arial', 12, 'bold'), fg='#ffaa00', bg='#2a2a2a')
        viz_label.pack(pady=(10, 5))
        
        # Matplotlib figure
        self.fig = Figure(figsize=(8, 4), facecolor='#1a1a1a')
        self.ax = self.fig.add_subplot(111, facecolor='#0a0a0a')
        self.ax.set_title("Waiting for data...", color='white')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶️ RESUME", bg='#00aa00')
            self.log("⏸️ Analysis PAUSED by user")
        else:
            self.pause_btn.config(text="⏸️ PAUSE", bg='#ff6600')
            self.log("▶️ Analysis RESUMED")
    
    def open_candidate_manager(self):
        """Open candidate management window."""
        if self.candidate_db is not None:
            from ksas.candidate_manager_gui import CandidateManagerWindow
            manager = CandidateManagerWindow(self.candidate_db)
        else:
            self.log("⚠️ Candidate database not initialized")
    
    def open_tic_verifier(self):
        """Open TIC verifier window."""
        from ksas.tic_verifier_gui import TICVerifierWindow
        verifier = TICVerifierWindow(parent=self.root)
        self.log("🔍 Opened TIC Verifier")
    
    def open_manual_analyzer(self):
        """Open manual TIC analyzer window."""
        from ksas.manual_analyzer_gui import ManualAnalyzerWindow
        analyzer = ManualAnalyzerWindow(parent=self.root)
        self.log("🔬 Opened Manual TIC Analyzer")
    
    def open_image_scanner(self):
        """Open automatic image scanner window."""
        from ksas.image_scanner_gui import CandidateScannerWindow
        scanner = CandidateScannerWindow(parent=self.root)
        self.log("📊 Opened Candidate Quality Scanner")
    
    def process_queue(self):
        """Process updates from the analysis thread."""
        try:
            while True:
                item = self.update_queue.get_nowait()
                
                if item['type'] == 'target':
                    self.target_var.set(item['value'])
                elif item['type'] == 'status':
                    self.status_var.set(item['value'])
                elif item['type'] == 'stats':
                    self.update_stats(item['value'])
                elif item['type'] == 'results':
                    self.results_var.set(item['value'])
                elif item['type'] == 'log':
                    self.log(item['value'])
                elif item['type'] == 'lightcurve':
                    self.update_lightcurve(item['lc'])
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)
    
    def update_stats(self, stats):
        """Update statistics display."""
        self.stats.update(stats)
        for key, label in self.stat_labels.items():
            label.config(text=str(self.stats[key]))
    
    def log(self, message):
        """Add message to event log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_lightcurve(self, lc):
        """Update light curve preview."""
        try:
            self.ax.clear()
            
            if lc is not None:
                # Plot with limited points for speed
                time = lc.time.value
                flux = lc.flux.value
                
                # Downsample if too many points
                if len(time) > 1000:
                    step = len(time) // 1000
                    time = time[::step]
                    flux = flux[::step]
                
                self.ax.plot(time, flux, 'w.', markersize=1, alpha=0.5)
                self.ax.set_xlabel("Time (BJD)", color='white')
                self.ax.set_ylabel("Normalized Flux", color='white')
                self.ax.set_title("Light Curve - Current Target", color='white')
                self.ax.grid(alpha=0.2, color='gray')
            else:
                self.ax.set_title("Waiting for data...", color='white')
            
            self.ax.tick_params(colors='white')
            for spine in self.ax.spines.values():
                spine.set_color('white')
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating lightcurve: {e}")
    
    def send_update(self, update_type, value=None, **kwargs):
        """Send update to GUI (called from analysis thread)."""
        item = {'type': update_type, 'value': value}
        item.update(kwargs)
        self.update_queue.put(item)
    
    def is_paused(self):
        """Check if analysis is paused."""
        return self.paused
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()
    
    def start_in_thread(self):
        """Start GUI in separate thread."""
        gui_thread = threading.Thread(target=self.run, daemon=True)
        gui_thread.start()
        return gui_thread
