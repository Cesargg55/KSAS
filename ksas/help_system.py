"""
KSAS Help System
Provides professional guidance and context-sensitive help for the user.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from ksas.config import COLORS, FONTS

class HelpSystem:
    """Manages help content and display."""
    
    TOPICS = {
        "general": {
            "title": "How KSAS Works",
            "content": """
KSAS (Kaesar Star Analysis System) is an autonomous exoplanet hunter.

1. 📥 DOWNLOAD: It downloads light curves from the TESS mission (NASA).
2. 🧹 PROCESS: It cleans the data, removing trends and outliers.
3. 🔍 ANALYZE: It uses two algorithms:
   - BLS (Box Least Squares): Fast initial search.
   - TLS (Transit Least Squares): Accurate confirmation using physical models.
4. 🛡️ VETTING: It applies strict filters to reject false positives (eclipsing binaries, noise).
5. 💾 SAVE: Promising candidates are saved to the database.

Use the 'Scan Candidates' button to rank and review your findings.
            """
        },
        "discovery": {
            "title": "I found a candidate! Now what?",
            "content": """
Congratulations! If you have a 'HIGHLY PROMISING' candidate:

1. 🔍 VERIFY: Click 'TIC Verifier' and check:
   - ExoFOP: Is it already a TOI (TESS Object of Interest)?
   - NASA Archive: Is it a confirmed planet?
   
2. 👁️ INSPECT: Look at the report image.
   - Does it have a clear 'U' shape?
   - Is the Odd/Even test consistent?
   
3. 📝 REPORT: If it is NOT in ExoFOP/NASA and looks good:
   - You may have found a new planet candidate!
   - Mark it as 'NEW' in the Candidate Manager.
   - Consider submitting a report to the TESS Follow-up Observing Program (TFOP).
            """
        },
        "vetting": {
            "title": "Understanding Vetting",
            "content": """
KSAS uses strict vetting to ensure quality.

- Odd/Even Test: Checks if odd and even transits have different depths. If they do, it's likely an Eclipsing Binary (two stars), not a planet.
- Shape Test: Planets usually make a 'U' shape. Binaries often make a 'V' shape.
- Secondary Eclipse: If there is a dip at phase 0.5, it's likely a binary star.

Candidates that fail these tests are marked as 'FAILED VETTING'.
            """
        },
        "scoring": {
            "title": "Candidate Scoring",
            "content": """
Candidates are scored (0-100) based on:

- SNR (Signal-to-Noise Ratio): Strength of the signal (60%).
- Depth: Clarity of the transit (25%).
- Period: Likelihood of being a physical orbit (15%).

⚠️ PENALTY: If a candidate fails vetting, its score is capped at 60 (GOOD/FAIR) regardless of SNR, to warn you it might be a false positive.
            """
        }
    }

    @staticmethod
    def show_help(parent, topic_key):
        """Show a help window for the given topic."""
        if topic_key not in HelpSystem.TOPICS:
            return
            
        topic = HelpSystem.TOPICS[topic_key]
        
        window = tk.Toplevel(parent)
        window.title(f"Help - {topic['title']}")
        window.geometry("600x450")
        window.configure(bg=COLORS['bg_dark'])
        
        # Header
        header_frame = tk.Frame(window, bg=COLORS['bg_panel'], pady=10)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text=f"❓ {topic['title']}", 
                font=FONTS['header'], fg=COLORS['accent'], bg=COLORS['bg_panel']).pack()
        
        # Content
        content_frame = tk.Frame(window, bg=COLORS['bg_dark'], padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(content_frame, font=FONTS['normal'], bg=COLORS['bg_dark'], 
                      fg=COLORS['text_main'], relief=tk.FLAT, wrap=tk.WORD)
        text.insert(tk.END, topic['content'].strip())
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        footer_frame = tk.Frame(window, bg=COLORS['bg_panel'], pady=10)
        footer_frame.pack(fill=tk.X)
        
        tk.Button(footer_frame, text="Close", command=window.destroy,
                 bg=COLORS['secondary'], fg='white', font=FONTS['normal']).pack()

    @staticmethod
    def create_help_button(parent, topic_key):
        """Create a standard '?' help button."""
        return tk.Button(parent, text="?", width=3,
                        command=lambda: HelpSystem.show_help(parent, topic_key),
                        bg=COLORS['info'], fg='white', font=('Arial', 10, 'bold'))
