import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from ksas.downloader import DataDownloader
from ksas.processor import DataProcessor
from ksas.analyzer import Analyzer
from ksas.tls_analyzer import TLSAnalyzer
from ksas.vetting import CandidateVetting
from ksas.visualizer import Visualizer
from ksas.candidate_db import CandidateDatabase

class ManualAnalyzerWindow:
    """
    GUI window for manually analyzing specific TIC IDs.
    Re-analyzes and regenerates reports.
    """
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("KSAS - Manual TIC Analyzer")
        self.window.geometry("700x700")
        self.window.configure(bg='#1a1a1a')
        
        self.analyzing = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create UI layout."""
        
        # Title
        title = tk.Label(self.window, text="🔬 Manual TIC Analyzer 🔬",
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.window, 
                               text="Analyze a specific TIC and regenerate its report",
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
        
        self.analyze_btn = tk.Button(input_frame, text="🔬 Analyze", 
                                     command=self.analyze_tic,
                                     font=('Arial', 11, 'bold'), bg='#00aa00', fg='white')
        self.analyze_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = tk.Label(self.window, textvariable=self.progress_var,
                                 font=('Arial', 10, 'bold'), fg='#ffaa00', bg='#1a1a1a')
        progress_label.pack(pady=5)
        
        # Results frame
        results_frame = tk.Frame(self.window, bg='#2a2a2a', relief=tk.SUNKEN, borderwidth=2)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="Analysis Results:", font=('Arial', 11, 'bold'),
                fg='#ffaa00', bg='#2a2a2a').pack(anchor=tk.W, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(results_frame, 
                                                  font=('Courier', 9),
                                                  bg='#0a0a0a', fg='#00ff00',
                                                  height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind Enter key
        self.tic_entry.bind('<Return>', lambda e: self.analyze_tic())
    
    def log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.window.update()
    
    def analyze_tic(self):
        """Analyze the entered TIC ID."""
        if self.analyzing:
            messagebox.showwarning("Busy", "Analysis already in progress")
            return
        
        tic_id = self.tic_entry.get().strip()
        
        if not tic_id or tic_id == "TIC ":
            messagebox.showwarning("Input Required", "Please enter a TIC ID")
            return
        
        # Disable button
        self.analyze_btn.config(state=tk.DISABLED, text="⏳ Analyzing...")
        self.progress_var.set("Starting analysis...")
        self.log_text.delete('1.0', tk.END)
        self.analyzing = True
        
        # Run in thread
        thread = threading.Thread(target=self._analyze_thread, args=(tic_id,))
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self, tic_id):
        """Thread worker for analysis."""
        try:
            self.log("="*60)
            self.log(f"🎯 MANUAL ANALYSIS: {tic_id}")
            self.log("="*60)
            self.log("")
            
            # Initialize components
            self.progress_var.set("Initializing components...")
            self.log("🔧 Initializing analysis components...")
            
            downloader = DataDownloader()
            processor = DataProcessor()
            bls_analyzer = Analyzer(snr_threshold=10)
            tls_analyzer = TLSAnalyzer(sde_threshold=7.0)
            vetting = CandidateVetting()
            visualizer = Visualizer()
            candidate_db = CandidateDatabase()
            
            self.log("✓ Components initialized")
            self.log("")
            
            # 1. Download
            self.progress_var.set("Downloading light curve...")
            self.log(f"📥 Downloading data for {tic_id}...")
            
            lc = downloader.download_lightcurve(tic_id)
            if lc is None:
                self.log(f"❌ No data found for {tic_id}")
                self.log("")
                self.log("This TIC has no TESS observations.")
                self.window.after(0, self._analysis_complete, False)
                return
            
            self.log(f"✓ Downloaded {len(lc.flux)} data points")
            self.log("")
            
            # 2. Process
            self.progress_var.set("Processing light curve...")
            self.log("🔄 Processing light curve...")
            
            clean_lc = processor.process_lightcurve(lc)
            if clean_lc is None:
                self.log("❌ Processing failed")
                self.window.after(0, self._analysis_complete, False)
                return
            
            self.log("✓ Light curve processed")
            self.log("")
            
            # 3. BLS Analysis
            self.progress_var.set("Running BLS analysis...")
            self.log("📊 Running BLS analysis...")
            
            bls_result, bls_periodogram = bls_analyzer.analyze(clean_lc, tic_id)
            
            if bls_result is None:
                self.log("❌ BLS analysis failed")
                self.window.after(0, self._analysis_complete, False)
                return
            
            self.log(f"✓ BLS complete:")
            self.log(f"   Period: {bls_result.period:.5f} days")
            self.log(f"   Power (SNR): {bls_result.power:.2f}")
            self.log(f"   Depth: {bls_result.depth:.6f}")
            self.log(f"   Is Candidate: {bls_result.is_candidate}")
            self.log("")
            
            # 4. TLS Analysis (if BLS found something)
            tls_result = None
            if bls_result.is_candidate:
                self.progress_var.set("Running TLS analysis...")
                self.log("🔬 Running TLS analysis (more precise)...")
                
                tls_result, tls_obj = tls_analyzer.analyze(clean_lc, tic_id)
                
                if tls_result:
                    self.log(f"✓ TLS complete:")
                    self.log(f"   Period: {tls_result.period:.5f} days")
                    self.log(f"   SDE: {tls_result.sde:.2f}")
                    self.log(f"   Depth: {tls_result.depth:.6f}")
                    self.log("")
            
            # 5. Check if candidate
            is_candidate = bls_result.is_candidate or (tls_result and tls_analyzer.is_significant(tls_result))
            
            if is_candidate:
                self.progress_var.set("Vetting candidate...")
                self.log("🔎 Potential candidate detected! Running vetting tests...")
                
                # Use TLS results if available, otherwise BLS
                period = tls_result.period if tls_result else bls_result.period
                t0 = tls_result.t0 if tls_result else bls_result.t0
                duration = tls_result.duration if tls_result else bls_result.duration
                
                # 6. Vetting
                vet_result = vetting.vet_candidate(clean_lc, period, t0, duration)
                
                self.log("")
                self.log("VETTING RESULTS:")
                for metric, value in vet_result.metrics.items():
                    self.log(f"  {metric}: {value:.4f}")
                self.log("")
                
                if vet_result.passed:
                    self.log("🌟🌟🌟 CANDIDATE CONFIRMED! 🌟🌟🌟")
                    self.log("✓ Passed ALL vetting tests")
                    self.log("")
                    
                    # Save to candidate database (if not already there)
                    existing = candidate_db.get_candidate(tic_id)
                    if existing:
                        self.log(f"ℹ️ Already in candidate database (updating data)")
                    else:
                        self.log(f"✓ Added to candidate database")
                    
                    candidate_db.add_candidate(
                        tic_id=tic_id,
                        period=period,
                        depth=tls_result.depth if tls_result else bls_result.depth,
                        bls_power=bls_result.power,
                        tls_sde=tls_result.sde if tls_result else None,
                        vetting_passed=vet_result.passed
                    )
                    
                    # Calculate Score immediately
                    from ksas.candidate_quality_analyzer import CandidateQualityAnalyzer
                    quality_analyzer = CandidateQualityAnalyzer()
                    
                    # Create a temporary result dict for the analyzer
                    # Use MAX of BLS Power and TLS SDE to ensure consistent scoring with DB
                    best_snr = max(bls_result.power, tls_result.sde if tls_result else 0)
                    
                    temp_result = {
                        'tic_id': tic_id,
                        'period': period,
                        'depth': tls_result.depth if tls_result else bls_result.depth,
                        'snr': best_snr,
                        'vetting_passed': vet_result.passed
                    }
                    
                    score_data = quality_analyzer.analyze_candidate(tic_id, temp_result)
                    
                    # Update DB with score
                    candidate_db.update_candidate(tic_id, {
                        'score': score_data['score'],
                        'quality': score_data['quality'],
                        'analysis_summary': score_data['recommendation']
                    })
                    
                    self.log(f"✓ Scored: {score_data['score']}/100 ({score_data['quality']})")
                    self.log("")
                    
                    # Generate report
                    self.progress_var.set("Generating report...")
                    self.log("📊 Generating visual report...")
                    
                    result_to_show = tls_result if tls_result and tls_analyzer.is_significant(tls_result) else bls_result
                    visualizer.save_plots(clean_lc, bls_periodogram, result_to_show)
                    self.log("")
                    
                    self.window.after(0, self._analysis_complete, True)
                else:
                    self.log("❌ Candidate REJECTED by vetting")
                    self.log(f"   Reason: {vet_result}")
                    self.log("")
                    self.log("This is likely a false positive (eclipsing binary, noise, etc.)")
                    self.window.after(0, self._analysis_complete, False)
            else:
                self.log("ℹ️ No significant signal detected")
                self.log("")
                self.log("BLS/TLS did not find strong transit signal.")
                self.log("This star probably doesn't have detectable planets.")
                self.window.after(0, self._analysis_complete, False)
            
        except Exception as e:
            self.log("")
            self.log(f"❌ ERROR: {str(e)}")
            self.log("")
            import traceback
            self.log(traceback.format_exc())
            self.window.after(0, self._analysis_complete, False)
    
    def _analysis_complete(self, success):
        """Called when analysis finishes."""
        self.analyzing = False
        self.analyze_btn.config(state=tk.NORMAL, text="🔬 Analyze")
        
        if success:
            self.progress_var.set("✅ Analysis Complete - Candidate Confirmed!")
        else:
            self.progress_var.set("⚠️ Analysis Complete - No Candidate")
    
    def run(self):
        """Run the window."""
        self.window.mainloop()


# Standalone execution
if __name__ == "__main__":
    app = ManualAnalyzerWindow()
    app.run()
