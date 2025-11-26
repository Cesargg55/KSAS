import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ksas.observatory_logic import ObservatoryLogic
from ksas.config import COLORS, FONTS
from ksas.locales import T
import numpy as np

import threading
from ksas.downloader import DataDownloader
from ksas.processor import DataProcessor

class ObservatoryWindow:
    """
    The Observatory: Professional Analysis Dashboard.
    """
    
    def __init__(self, tic_id, data, lc_data=None):
        self.tic_id = tic_id
        self.data = data
        self.lc_data = lc_data # (time, flux) tuple if available
        
        self.window = tk.Toplevel()
        self.window.title(f"{T.get('observatory_title')} - {tic_id}")
        self.window.geometry("1200x800")
        self.window.configure(bg=COLORS['bg_dark'])
        
        self.setup_ui()
        self.analyze()
        
        # Load data if not provided
        if self.lc_data is None:
            self.load_data()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=COLORS['bg_panel'], height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(header, text=f"{T.get('target_label')} {self.tic_id}", font=FONTS['title'],
                fg=COLORS['accent'], bg=COLORS['bg_panel']).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Score Badge
        score = self.data.get('score', 0)
        color = COLORS['success'] if score >= 80 else (COLORS['warning'] if score >= 50 else COLORS['danger'])
        self.score_label = tk.Label(header, text=f"{T.get('score_label')} {score}/100", font=('Arial', 16, 'bold'),
                fg=color, bg=COLORS['bg_panel'])
        self.score_label.pack(side=tk.RIGHT, padx=20)

        # Main Content (Split Pane)
        content = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg=COLORS['bg_dark'])
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Visuals (Plots)
        self.plot_frame = tk.Frame(content, bg='black')
        content.add(self.plot_frame, minsize=600)
        
        # Right: Intelligence (Analysis)
        self.info_frame = tk.Frame(content, bg=COLORS['bg_panel'], relief=tk.RAISED)
        content.add(self.info_frame, minsize=300)
        
        # Setup Right Panel
        self.setup_info_panel()

    def setup_info_panel(self):
        # 1. Physics Section
        tk.Label(self.info_frame, text=T.get('physical_props'), font=FONTS['header'],
                fg=COLORS['info'], bg=COLORS['bg_panel']).pack(anchor=tk.W, padx=10, pady=(10,5))
        
        self.physics_label = tk.Label(self.info_frame, text=T.get('calculating'), font=FONTS['mono'],
                                     fg='white', bg=COLORS['bg_panel'], justify=tk.LEFT)
        self.physics_label.pack(anchor=tk.W, padx=20)
        
        # 2. AI Analysis Section
        tk.Label(self.info_frame, text=T.get('intelligent_analysis'), font=FONTS['header'],
                fg=COLORS['accent'], bg=COLORS['bg_panel']).pack(anchor=tk.W, padx=10, pady=(20,5))
        
        self.analysis_text = tk.Text(self.info_frame, height=15, width=40,
                                    font=('Arial', 10), bg=COLORS['bg_input'], fg='white',
                                    relief=tk.FLAT, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.X, padx=10)
        
        # 3. Vetting Status
        tk.Label(self.info_frame, text=T.get('vetting_status'), font=FONTS['header'],
                fg=COLORS['success'], bg=COLORS['bg_panel']).pack(anchor=tk.W, padx=10, pady=(20,5))
        
        self.vetting_label = tk.Label(self.info_frame, text=T.get('checking'), font=FONTS['mono'],
                                     fg='white', bg=COLORS['bg_panel'], justify=tk.LEFT)
        self.vetting_label.pack(anchor=tk.W, padx=20)

    def analyze(self):
        # 1. Run Logic Engine
        # Prepare data for logic engine (ensure depth is in percent)
        logic_data = self.data.copy()
        if 'depth' in logic_data and logic_data['depth'] < 1.0:
             logic_data['depth_percent'] = (1.0 - logic_data['depth']) * 100
        else:
             logic_data['depth_percent'] = logic_data.get('depth_percent', 0)

        analysis = ObservatoryLogic.generate_analysis_text(logic_data)
        
        # Update Analysis Text
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert('1.0', analysis)
        
        # 2. Calculate Physics
        r_p = ObservatoryLogic.calculate_planet_radius(logic_data['depth_percent'])
        teq, a_au = ObservatoryLogic.estimate_equilibrium_temp(5778, logic_data['period']) # Assume Sun-like
        
        physics_text = f"{T.get('radius')} {r_p:.2f} R_Earth\n"
        physics_text += f"{T.get('orbit')}  {a_au:.3f} AU\n"
        physics_text += f"{T.get('temp')}   {teq:.0f} K ({teq-273.15:.0f} °C)\n"
        physics_text += f"{T.get('type')}   {ObservatoryLogic.classify_planet(r_p)}"
        self.physics_label.config(text=physics_text)
        
        # 3. Update Vetting
        vet_passed = self.data.get('vetting_passed', False)
        vet_text = T.get('passed_tests') if vet_passed else T.get('failed_tests')
        self.vetting_label.config(text=vet_text, fg=COLORS['success'] if vet_passed else COLORS['danger'])
        
        # 4. Update Score Badge (in case it was calculated on the fly)
        final_score = logic_data.get('score', 0)
        score_color = COLORS['success'] if final_score >= 80 else (COLORS['warning'] if final_score >= 50 else COLORS['danger'])
        self.score_label.config(text=f"{T.get('score_label')} {final_score}/100", fg=score_color)
        
        # 4. Plotting
        self.plot_graphs()

    def load_data(self):
        """Load lightcurve data in background."""
        def _load():
            try:
                downloader = DataDownloader()
                processor = DataProcessor()
                
                # Download (will use cache if available)
                lc = downloader.download_lightcurve(self.tic_id)
                if lc:
                    # Process
                    clean_lc = processor.process_lightcurve(lc)
                    if clean_lc:
                        self.lc_data = (clean_lc.time.value, clean_lc.flux.value)
                        # Update plots in main thread
                        self.window.after(0, self.plot_graphs)
            except Exception as e:
                print(f"Error loading data: {e}")

        thread = threading.Thread(target=_load)
        thread.daemon = True
        thread.start()

    def show_graph_guide(self):
        """Show explanation of graphs."""
        guide = tk.Toplevel(self.window)
        guide.title(T.get('guide_title'))
        guide.geometry("600x600")
        guide.configure(bg=COLORS['bg_dark'])
        
        # Get dynamic explanation
        explanation = ObservatoryLogic.generate_graph_explanation(self.data)
        
        text_widget = tk.Text(guide, font=('Arial', 11), bg=COLORS['bg_dark'], fg='#eeeeee',
                             wrap=tk.WORD, padx=20, pady=20, relief=tk.FLAT)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.insert('1.0', explanation)
        text_widget.config(state=tk.DISABLED) # Read-only
        
        tk.Button(guide, text=T.get('got_it'), command=guide.destroy,
                 bg=COLORS['accent'], fg='white', font=('Arial', 11, 'bold')).pack(pady=10)

    def plot_graphs(self):
        # Clear previous plots if any (re-creating figure is easiest for now)
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig = plt.Figure(figsize=(6, 8), dpi=100, facecolor='black')
        
        # Plot 1: Phase Fold
        ax1 = fig.add_subplot(211)
        ax1.set_facecolor('black')
        ax1.set_title(T.get('graph_phase'), color='white')
        ax1.tick_params(colors='white')
        ax1.spines['bottom'].set_color('white')
        ax1.spines['left'].set_color('white')
        
        if self.lc_data:
            time, flux = self.lc_data
            period = self.data.get('period', 1.0)
            t0 = 0 # Simplified, ideally we need t0 from data
            
            # If we don't have t0, phase folding might be messy. 
            # But for now let's try 0. If it looks bad, we might need t0 from DB.
            # Actually, ManualAnalyzer saves period/t0/duration to DB? 
            # candidate_db only saves period/depth/snr. It SHOULD save t0.
            # For now, just folding by period is better than nothing, but might be shifted.
            
            phase = ((time - t0) % period) / period
            phase[phase > 0.5] -= 1.0
            
            ax1.scatter(phase, flux, s=1, c=COLORS['accent'], alpha=0.5)
            ax1.set_xlim(-0.5, 0.5) # Show full phase
        else:
            ax1.text(0.5, 0.5, T.get('loading_data'), color='white', ha='center')

        # Plot 2: Full Lightcurve
        ax2 = fig.add_subplot(212)
        ax2.set_facecolor('black')
        ax2.set_title(T.get('graph_full'), color='white')
        ax2.tick_params(colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        
        if self.lc_data:
            ax2.plot(time, flux, '.', color='white', markersize=1)
        else:
             ax2.text(0.5, 0.5, T.get('loading_data'), color='white', ha='center')
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, self.plot_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add Graph Guide Button to Toolbar or below
        btn_frame = tk.Frame(self.plot_frame, bg='black')
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text=T.get('btn_graph_guide'), command=self.show_graph_guide,
                 bg='#333333', fg='white', font=('Arial', 9)).pack(side=tk.RIGHT, padx=10)
