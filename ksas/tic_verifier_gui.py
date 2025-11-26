import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from ksas.tic_verifier import TICVerifier

class TICVerifierWindow:
    """
    GUI window for verifying TIC IDs against discovery databases.
    """
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("KSAS - TIC Verifier")
        self.window.geometry("700x600")
        self.window.configure(bg='#1a1a1a')
        
        self.verifier = TICVerifier()
        self.setup_ui()
    
    def setup_ui(self):
        """Create UI layout."""
        
        # Title
        title = tk.Label(self.window, text="🔍 TIC Discovery Verifier 🔍",
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.window, 
                               text="Enter a TIC ID to check if it's already discovered",
                               font=('Arial', 10), fg='#aaaaaa', bg='#1a1a1a')
        instructions.pack(pady=5)
        
        # Input frame
        input_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="TIC ID:", font=('Arial', 11, 'bold'),
                fg='white', bg='#2a2a2a').pack(side=tk.LEFT, padx=10, pady=10)
        
        self.tic_entry = tk.Entry(input_frame, font=('Courier', 12), width=20)
        self.tic_entry.pack(side=tk.LEFT, padx=5, pady=10)
        self.tic_entry.insert(0, "TIC ")
        
        self.verify_btn = tk.Button(input_frame, text="🔍 Verify", 
                                    command=self.verify_tic,
                                    font=('Arial', 11, 'bold'), bg='#0066cc', fg='white')
        self.verify_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status
        self.status_label = tk.Label(self.window, text="Ready", 
                                     font=('Arial', 10), fg='#00ff00', bg='#1a1a1a')
        self.status_label.pack(pady=5)
        
        # Results frame
        results_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.SUNKEN, borderwidth=2)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="Results:", font=('Arial', 11, 'bold'),
                fg='#ffaa00', bg='#2a2a2a').pack(anchor=tk.W, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                       font=('Courier', 9),
                                                       bg='#0a0a0a', fg='#00ff00',
                                                       height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Quick links
        links_frame = tk.Frame(self.window, bg='#1a1a1a')
        links_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(links_frame, text="Quick Links:", fg='#aaaaaa', bg='#1a1a1a').pack(side=tk.LEFT)
        
        tk.Button(links_frame, text="ExoFOP-TESS", command=lambda: self.open_link('exofop'),
                 bg='#444444', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(links_frame, text="NASA Archive", command=lambda: self.open_link('nasa'),
                 bg='#444444', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(links_frame, text="SIMBAD", command=lambda: self.open_link('simbad'),
                 bg='#444444', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.tic_entry.bind('<Return>', lambda e: self.verify_tic())
    
    def verify_tic(self):
        """Verify the entered TIC ID."""
        tic_id = self.tic_entry.get().strip()
        
        if not tic_id or tic_id == "TIC ":
            messagebox.showwarning("Input Required", "Please enter a TIC ID")
            return
        
        # Disable button
        self.verify_btn.config(state=tk.DISABLED, text="⏳ Checking...")
        self.status_label.config(text="Checking databases...", fg='#ffaa00')
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, "Querying databases, please wait...\n")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._verify_thread, args=(tic_id,))
        thread.daemon = True
        thread.start()
    
    def _verify_thread(self, tic_id):
        """Thread worker for verification."""
        try:
            result = self.verifier.verify_tic(tic_id)
            
            # Update UI in main thread
            self.window.after(0, self._display_result, result)
            
        except Exception as e:
            self.window.after(0, self._display_error, str(e))
    
    def _display_result(self, result):
        """Display verification result."""
        self.results_text.delete('1.0', tk.END)
        
        formatted = self.verifier.format_result(result)
        self.results_text.insert(tk.END, formatted)
        
        # Update status
        if result['is_discovered']:
            self.status_label.config(text="⚠️ Already Discovered", fg='#ff6600')
            # Highlight in red
            self.results_text.tag_add("discovered", "1.0", "4.0")
            self.results_text.tag_config("discovered", foreground='#ff6600')
        else:
            self.status_label.config(text="✅ Not Found (Potentially New!)", fg='#00ff00')
            # Highlight in green
            self.results_text.tag_add("new", "1.0", "4.0")
            self.results_text.tag_config("new", foreground='#00ff00')
        
        # Re-enable button
        self.verify_btn.config(state=tk.NORMAL, text="🔍 Verify")
    
    def _display_error(self, error):
        """Display error message."""
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, f"Error: {error}\n\nPlease check your internet connection.")
        self.status_label.config(text="❌ Error", fg='#ff0000')
        self.verify_btn.config(state=tk.NORMAL, text="🔍 Verify")
    
    def open_link(self, link_type):
        """Open relevant website."""
        import webbrowser
        
        tic_id = self.tic_entry.get().strip().replace("TIC", "").strip()
        
        if link_type == 'exofop':
            url = f"https://exofop.ipac.caltech.edu/tess/target.php?id={tic_id}"
        elif link_type == 'nasa':
            url = "https://exoplanetarchive.ipac.caltech.edu/"
        elif link_type == 'simbad':
            url = f"http://simbad.u-strasbg.fr/simbad/sim-id?Ident=TIC+{tic_id}"
        else:
            return
        
        webbrowser.open(url)
    
    def run(self):
        """Run the window."""
        self.window.mainloop()


# Standalone execution
if __name__ == "__main__":
    app = TICVerifierWindow()
    app.run()
