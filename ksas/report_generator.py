import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import os
from datetime import datetime
from ksas.config import CURRENT_VERSION

class ExoFOPReportGenerator:
    """
    Generates professional PDF reports for ExoFOP submission.
    Includes comprehensive transit parameters and high-quality plots.
    """
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Set style for professional look
        plt.style.use('default') # Use default white background for PDF
        
    def generate_report(self, tic_id, candidate_data, lc_data, bls_result=None):
        """
        Generate a PDF report.
        
        Args:
            tic_id: TIC ID string
            candidate_data: Dictionary of candidate parameters
            lc_data: Tuple (time, flux)
            bls_result: Optional BLS result object for periodogram data
        """
        try:
            safe_id = tic_id.replace(" ", "_")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = os.path.join(self.output_dir, f"{safe_id}_ExoFOP_Report_{timestamp}.pdf")
            
            # Create Figure (A4 size approx: 8.27 x 11.69 inches)
            fig = plt.figure(figsize=(8.27, 11.69)) # Exact A4
            # Increased hspace to 0.6 to prevent overlap
            gs = GridSpec(5, 2, figure=fig, height_ratios=[0.6, 0.8, 1, 1, 1], hspace=0.6)
            
            # --- 1. Header (with Banner) ---
            ax_header = fig.add_subplot(gs[0, :])
            ax_header.axis('off')
            
            # Add a colored banner
            from matplotlib.patches import Rectangle
            rect = Rectangle((0, 0.6), 1, 0.4, transform=ax_header.transAxes, 
                           facecolor='#0066cc', alpha=0.1, clip_on=False)
            ax_header.add_patch(rect)
            
            title = f"TRANSIT CANDIDATE REPORT"
            subtitle = f"TIC {tic_id}"
            
            # Adjusted vertical positions to separate title and subtitle
            ax_header.text(0.5, 0.90, title, ha='center', va='center', fontsize=18, fontweight='bold', color='#003366')
            ax_header.text(0.5, 0.70, subtitle, ha='center', va='center', fontsize=16, fontweight='bold', color='black')
            
            # --- 2. Parameters Table ---
            ax_table = fig.add_subplot(gs[1, :])
            ax_table.axis('off')
            
            # Extract data
            period = candidate_data.get('period', 0)
            epoch = candidate_data.get('t0', 0)
            depth = candidate_data.get('depth', 0)
            duration = candidate_data.get('duration', 0)
            snr = candidate_data.get('snr', 0)
            score = candidate_data.get('score', 0)
            
            # Format data
            # Depth: Convert to ppm (parts per million)
            # If depth is < 1 (e.g. 0.01), it's relative flux. 0.01 = 10 ppt = 10000 ppm.
            depth_ppm = depth * 1e6 if depth < 1 else depth
            
            # Epoch: Convert BTJD to BJD (TESS offset is 2457000)
            epoch_bjd = epoch + 2457000 if epoch < 2400000 else epoch
            
            # Duration: Keep in hours for readability, but maybe show days too?
            duration_hours = duration * 24
            
            # Table Data (ExoFOP Compliant)
            col_labels = ["Parameter", "Value", "Unit", "Description"]
            table_data = [
                ["TIC ID", tic_id, "-", "TESS Input Catalog ID"],
                ["Orbital Period", f"{period:.6f}", "days", "Time between transits"],
                ["Transit Epoch (T0)", f"{epoch_bjd:.6f}", "BJD", "Midpoint time (Barycentric Julian Date)"],
                ["Transit Duration", f"{duration_hours:.2f}", "hours", f"({duration:.4f} days)"],
                ["Transit Depth", f"{depth_ppm:.0f}", "ppm", "Flux drop (parts per million)"],
                ["SNR", f"{snr:.1f}", "-", "Signal-to-Noise Ratio"],
                ["KSAS Score", f"{score}/100", "-", "Automated Quality Assessment"]
            ]
            
            # Create table with fixed column widths to prevent overflow
            table = ax_table.table(cellText=table_data, colLabels=col_labels, 
                                 loc='center', cellLoc='left',
                                 colWidths=[0.2, 0.25, 0.15, 0.4]) # Total = 1.0
            
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.6) # Reduced scaling slightly to prevent overlap with plot below
            
            # Style table
            for (row, col), cell in table.get_celld().items():
                cell.set_edgecolor('#dddddd')
                if row == 0:
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('#0066cc') # Match banner color
                elif col == 0: # First column (Parameter names)
                    cell.set_text_props(weight='bold')
                    cell.set_facecolor('#f8f9fa')
            
            # --- 3. Full Light Curve ---
            ax_lc = fig.add_subplot(gs[2, :])
            if lc_data:
                time, flux = lc_data
                ax_lc.scatter(time, flux, s=0.5, color='black', alpha=0.6, label='Flux')
                ax_lc.set_title("Full Light Curve (Detrended)", fontsize=10, fontweight='bold')
                ax_lc.set_xlabel("Time [BTJD]")
                ax_lc.set_ylabel("Normalized Flux")
                ax_lc.grid(True, alpha=0.3)
                
                # Mark transits if period is known
                if period > 0 and epoch > 0:
                    # Find transit times in range
                    t_min, t_max = np.min(time), np.max(time)
                    # Start from epoch and go forward/backward
                    n = 0
                    while True:
                        t = epoch + n * period
                        if t > t_max: break
                        if t >= t_min:
                            ax_lc.axvline(t, color='red', alpha=0.3, lw=1)
                        n += 1
                    n = -1
                    while True:
                        t = epoch + n * period
                        if t < t_min: break
                        if t <= t_max:
                            ax_lc.axvline(t, color='red', alpha=0.3, lw=1)
                        n -= 1
            
            # --- 4. Phase Folded Light Curve ---
            ax_fold = fig.add_subplot(gs[3, :])
            if lc_data and period > 0:
                time, flux = lc_data
                # Simple folding
                t0 = epoch if epoch > 0 else 0
                phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
                
                # Sort for plotting line if needed, but scatter is better
                ax_fold.scatter(phase * 24, flux, s=1, color='blue', alpha=0.5, label='Folded Flux')
                ax_fold.set_title(f"Phase Folded Light Curve (Period: {period:.5f} d)", fontsize=10, fontweight='bold')
                ax_fold.set_xlabel("Time from Transit Center [Hours]")
                ax_fold.set_ylabel("Normalized Flux")
                ax_fold.grid(True, alpha=0.3)
                ax_fold.set_xlim(-5, 5) # Zoom to +/- 5 hours around transit
                
                # Add binning for clarity (optional, simple binning)
                # ... (skipping complex binning for speed, scatter is usually fine for reports)
                
            # --- 5. Periodogram (Placeholder if no data, or plot if provided) ---
            ax_per = fig.add_subplot(gs[4, :])
            if bls_result and hasattr(bls_result, 'periodogram'):
                # If we passed the full object with periodogram data
                # This requires changing how we call this function
                pass 
            else:
                # Placeholder text
                ax_per.text(0.5, 0.5, "Periodogram not available in this report version", 
                           ha='center', va='center', color='gray')
                ax_per.set_title("Periodogram", fontsize=10, fontweight='bold')
                ax_per.axis('off')

            # --- Footer ---
            # Add GitHub link
            from ksas.config import GITHUB_REPO
            footer_text = f"Generated by KSAS v{CURRENT_VERSION} | {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | {GITHUB_REPO}"
            
            # Add separator line
            line = plt.Line2D([0.05, 0.95], [0.04, 0.04], transform=fig.transFigure, color='#0066cc', linewidth=1)
            fig.add_artist(line)
            
            # Use fig.text for footer to ensure it's at the absolute bottom
            fig.text(0.5, 0.02, footer_text, ha='center', va='bottom', fontsize=8, color='gray')
            
            # Adjust layout to leave room for footer and header
            # rect = [left, bottom, right, top]
            plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
            
            # Save
            plt.savefig(filename, dpi=300)
            plt.close(fig)
            
            return filename
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
