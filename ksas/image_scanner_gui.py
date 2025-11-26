import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from ksas.candidate_quality_analyzer import CandidateQualityAnalyzer

class CandidateScannerWindow:
    """
    GUI window for automatic candidate analysis.
    Uses scientific metrics (SNR, depth, period) for accurate ranking.
    """
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("KSAS - Candidate Quality Scanner")
        self.window.geometry("1100x700")
        self.window.configure(bg='#1a1a1a')
        
        self.analyzer = CandidateQualityAnalyzer()
        self.results = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create UI layout."""
        
        # Title
        title = tk.Label(self.window, text="📊 Candidate Quality Scanner 📊",
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.window, 
                               text="Analyze all candidates using scientific metrics (SNR, depth, period)",
                               font=('Arial', 10), fg='#aaaaaa', bg='#1a1a1a')
        instructions.pack(pady=5)
        
        # Scan button
        scan_btn = tk.Button(self.window, text="🔍 Scan All Candidates",
                           command=self.scan_candidates,
                           font=('Arial', 12, 'bold'), bg='#00aa00', fg='white')
        scan_btn.pack(pady=10)
        
        # Help
        from ksas.help_system import HelpSystem
        help_frame = tk.Frame(self.window, bg='#1a1a1a')
        help_frame.pack(pady=5)
        HelpSystem.create_help_button(help_frame, 'scoring').pack(side=tk.LEFT, padx=5)
        tk.Label(help_frame, text="How scoring works", fg='#aaaaaa', bg='#1a1a1a').pack(side=tk.LEFT)
        
        # Results list
        results_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.SUNKEN, borderwidth=2)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="Results (Best First):", font=('Arial', 11, 'bold'),
                fg='#ffaa00', bg='#2a2a2a').pack(anchor=tk.W, padx=10, pady=5)
        
        # Treeview for results
        columns = ('TIC ID', 'Score', 'Quality', 'SNR', 'Period', 'Depth %', 'Recommendation')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.tree.heading('TIC ID', text='TIC ID')
        self.tree.heading('Score', text='Score')
        self.tree.heading('Quality', text='Quality')
        self.tree.heading('SNR', text='SNR/SDE')
        self.tree.heading('Period', text='Period (d)')
        self.tree.heading('Depth %', text='Depth %')
        self.tree.heading('Recommendation', text='Recommendation')
        
        self.tree.column('TIC ID', width=120)
        self.tree.column('Score', width=60)
        self.tree.column('Quality', width=90)
        self.tree.column('SNR', width=80)
        self.tree.column('Period', width=90)
        self.tree.column('Depth %', width=80)
        self.tree.column('Recommendation', width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to open image
        self.tree.bind('<Double-1>', self.open_image)
        
        # Summary
        self.summary_label = tk.Label(self.window, text="",
                                     font=('Arial', 10, 'bold'), fg='#00ff00', bg='#1a1a1a')
        self.summary_label.pack(pady=10)
    
    def scan_candidates(self):
        """Scan all candidates using scientific metrics."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.summary_label.config(text="Analyzing candidates...")
        self.window.update()
        
        # Scan
        self.results = self.analyzer.scan_all_candidates()
        
        if not self.results:
            self.summary_label.config(text="No candidates found in candidates.json")
            return
        
        # Populate tree
        excellent = 0
        good = 0
        fair = 0
        poor = 0
        
        for result in self.results:
            if 'error' in result:
                continue
            
            # Count quality
            quality = result['quality']
            if quality == 'EXCELLENT':
                excellent += 1
                tag = 'excellent'
            elif quality == 'GOOD':
                good += 1
                tag = 'good'
            elif quality == 'FAIR':
                fair += 1
                tag = 'fair'
            else:
                poor += 1
                tag = 'poor'
            
            self.tree.insert('', tk.END, values=(
                result['tic_id'],
                result['score'],
                result['quality'],
                f"{result['snr']:.2f}",
                f"{result['period']:.4f}",
                f"{result['depth_percent']:.4f}",
                result['recommendation']
            ), tags=(tag,))
        
        # Configure tags for colors
        self.tree.tag_configure('excellent', background='#004400', foreground='#00ff00')
        self.tree.tag_configure('good', background='#004400', foreground='#88ff88')
        self.tree.tag_configure('fair', background='#333300', foreground='#ffff00')
        self.tree.tag_configure('poor', background='#440000', foreground='#ff8888')
        
        # Update summary
        stats = self.analyzer.get_summary_stats(self.results)
        summary = (f"Analyzed {stats['total']} candidates | "
                  f"⭐⭐⭐ Excellent: {excellent} | "
                  f"⭐⭐ Good: {good} | "
                  f"⭐ Fair: {fair} | "
                  f"❌ Poor: {poor} | "
                  f"Max SNR: {stats['max_snr']:.1f}")
        self.summary_label.config(text=summary)
    
    def open_image(self, event):
        """Open selected image."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        tic_id = item['values'][0]
        
        # Find filename
        for result in self.results:
            if result.get('tic_id') == tic_id:
                filename = result.get('filename')
                filepath = os.path.join('output', filename)
                
                if os.path.exists(filepath):
                    # Open with default viewer
                    import platform
                    if platform.system() == 'Windows':
                        os.startfile(filepath)
                    elif platform.system() == 'Darwin':  # macOS
                        os.system(f'open "{filepath}"')
                    else:  # Linux
                        os.system(f'xdg-open "{filepath}"')
                break
    
    def run(self):
        """Run the window."""
        self.window.mainloop()

# Standalone execution
if __name__ == "__main__":
    app = CandidateScannerWindow()
    app.run()
