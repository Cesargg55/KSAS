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
        Generate a 2-page PDF report.
        Page 1: Header + Parameters Table
        Page 2: Plots (Full LC, Folded LC, Periodogram)
        
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
            
            from matplotlib.backends.backend_pdf import PdfPages
            
            # Create multi-page PDF
            with PdfPages(filename) as pdf:
                
                # ==================== PAGE 1: HEADER + TABLE ====================
                fig1 = plt.figure(figsize=(8.27, 11.69))  # A4
                gs1 = GridSpec(2, 1, figure=fig1, 
                              height_ratios=[0.15, 0.85],
                              hspace=0.3,
                              top=0.96, bottom=0.06, left=0.08, right=0.92)
                
                # --- Header ---
                ax_header = fig1.add_subplot(gs1[0])
                ax_header.axis('off')
                
                from matplotlib.patches import Rectangle
                rect = Rectangle((0, 0.2), 1, 0.8, transform=ax_header.transAxes, 
                               facecolor='#0066cc', alpha=0.12, clip_on=False)
                ax_header.add_patch(rect)
                
                title = f"TRANSIT CANDIDATE REPORT"
                subtitle = f"{tic_id}"
                
                ax_header.text(0.5, 0.75, title, ha='center', va='center', 
                              fontsize=18, fontweight='bold', color='#003366')
                ax_header.text(0.5, 0.30, subtitle, ha='center', va='center', 
                              fontsize=16, fontweight='bold', color='#333333')
                
                # --- Parameters Table ---
                ax_table = fig1.add_subplot(gs1[1])
                ax_table.axis('off')
                
                # Extract and format data
                period = candidate_data.get('period', 0)
                epoch = candidate_data.get('t0', 0)
                depth = candidate_data.get('depth', 0)
                duration = candidate_data.get('duration', 0)
                snr = candidate_data.get('snr', 0)
                score = candidate_data.get('score', 0)
                
                depth_val = depth if depth is not None else 0
                depth_ppm = depth_val * 1e6 if depth_val < 1 else depth_val
                
                epoch_val = epoch if epoch is not None else 0
                epoch_bjd = epoch_val + 2457000 if epoch_val < 2400000 else epoch_val
                
                duration_val = duration if duration is not None else 0
                duration_hours = duration_val * 24
                
                disposition = candidate_data.get('disposition', 'PC')
                tag = candidate_data.get('tag', 'KSAS_Candidate')
                notes = candidate_data.get('notes', '-')
                if len(notes) > 50: notes = notes[:47] + "..."

                # Derived Parameters
                r_planet = candidate_data.get('r_planet_earth', 0)
                rp_rs = candidate_data.get('rp_rs', 0)
                a_au = candidate_data.get('a_au', 0)
                a_rs = candidate_data.get('a_rs', 0)
                teq = candidate_data.get('teq', 0)
                insolation = candidate_data.get('insolation', 0)
                inclination = candidate_data.get('inclination', 0)
                impact = candidate_data.get('impact_parameter', 0)

                # Table Data
                col_labels = ["Parameter", "Value", "Unit", "Description"]
                table_data = [
                    ["TIC ID", tic_id, "-", "TESS Input Catalog ID"],
                    ["Disposition", disposition, "-", "PC=Candidate, FP=False Positive"],
                    ["Orbital Period", f"{period:.6f}", "days", "Time between transits"],
                    ["Transit Epoch (T0)", f"{epoch_bjd:.6f}", "BJD", "Midpoint time (Barycentric Julian Date)"],
                    ["Transit Duration", f"{duration_hours:.2f}", "hours", f"({duration_val:.4f} days)"],
                    ["Transit Depth", f"{depth_ppm:.0f}", "ppm", "Flux drop (parts per million)"],
                    ["SNR", f"{snr:.1f}", "-", "Signal-to-Noise Ratio"],
                    ["KSAS Score", f"{score}/100", "-", "Automated Quality Assessment"],
                    ["Tag", tag, "-", "Upload Tag"],
                    ["Notes", notes, "-", "Candidate Notes"],
                    ["Planet Radius", f"{r_planet:.2f}", "R_Earth", "Estimated Size"],
                    ["Rp / R*", f"{rp_rs:.4f}", "-", "Radius Ratio"],
                    ["Semi-major Axis", f"{a_au:.4f}", "AU", "Orbital Distance"],
                    ["a / R*", f"{a_rs:.2f}", "-", "Scaled Distance"],
                    ["Equilibrium Temp", f"{teq:.0f}", "K", "Estimated Surface Temp"],
                    ["Insolation Flux", f"{insolation:.2f}", "S_Earth", "Incident Flux"],
                    ["Inclination", f"{inclination:.1f}", "deg", "Orbital Inclination (Est.)"],
                    ["Impact Parameter", f"{impact:.2f}", "-", "Impact Parameter (Est.)"]
                ]
                
                # Create table
                table = ax_table.table(cellText=table_data, colLabels=col_labels, 
                                     loc='center', cellLoc='left',
                                     colWidths=[0.26, 0.23, 0.11, 0.40])
                
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 1.4)  # More vertical space on page 1
                
                # Style table
                for (row, col), cell in table.get_celld().items():
                    cell.set_edgecolor('#cccccc')
                    cell.set_linewidth(0.5)
                    if row == 0:  # Header
                        cell.set_text_props(weight='bold', color='white', fontsize=9)
                        cell.set_facecolor('#0066cc')
                    elif col == 0:  # Parameter column
                        cell.set_text_props(weight='bold', fontsize=8)
                        cell.set_facecolor('#f5f5f5')
                    else:
                        cell.set_facecolor('white')
                
                # Footer for page 1
                from ksas.config import GITHUB_REPO
                footer_text = f"Generated by KSAS v{CURRENT_VERSION} | Page 1/2"
                fig1.text(0.5, 0.03, footer_text, ha='center', va='center', 
                         fontsize=8, color='#666666', style='italic')
                
                # Save page 1
                pdf.savefig(fig1, bbox_inches=None, pad_inches=0)
                plt.close(fig1)
                
                # ==================== PAGE 2: GRAPHS ====================
                fig2 = plt.figure(figsize=(8.27, 11.69))  # A4
                gs2 = GridSpec(3, 1, figure=fig2,
                              height_ratios=[1.2, 1.2, 0.8],
                              hspace=0.5,
                              top=0.95, bottom=0.06, left=0.08, right=0.92)
                
                # --- Full Light Curve ---
                ax_lc = fig2.add_subplot(gs2[0])
                if lc_data:
                    time, flux = lc_data
                    ax_lc.scatter(time, flux, s=0.3, color='#333333', alpha=0.5, rasterized=True)
                    ax_lc.set_title("Full Light Curve (Detrended)", fontsize=12, 
                                   fontweight='bold', pad=12, color='#0066cc')
                    ax_lc.set_xlabel("Time [BTJD]", fontsize=10, labelpad=8)
                    ax_lc.set_ylabel("Normalized Flux", fontsize=10, labelpad=8)
                    ax_lc.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
                    ax_lc.tick_params(labelsize=9)
                    
                    # Mark transits
                    if period is not None and period > 0 and epoch_val > 0:
                        t_min, t_max = np.min(time), np.max(time)
                        n = 0
                        while True:
                            t = epoch_val + n * period
                            if t > t_max: break
                            if t >= t_min:
                                ax_lc.axvline(t, color='#ff4444', alpha=0.2, lw=0.8, linestyle='--')
                            n += 1
                        n = -1
                        while True:
                            t = epoch_val + n * period
                            if t < t_min: break
                            if t <= t_max:
                                ax_lc.axvline(t, color='#ff4444', alpha=0.2, lw=0.8, linestyle='--')
                            n -= 1
                
                for spine in ax_lc.spines.values():
                    spine.set_edgecolor('#999999')
                    spine.set_linewidth(0.8)
                
                # --- Phase Folded Light Curve ---
                ax_fold = fig2.add_subplot(gs2[1])
                if lc_data and period is not None and period > 0:
                    time, flux = lc_data
                    t0 = epoch_val if epoch_val > 0 else 0
                    phase = ((time - t0 + 0.5 * period) % period) - 0.5 * period
                    
                    ax_fold.scatter(phase * 24, flux, s=0.8, color='#0066cc', alpha=0.4, rasterized=True)
                    ax_fold.set_title(f"Phase Folded Light Curve (Period: {period:.5f} d)", 
                                     fontsize=12, fontweight='bold', pad=12, color='#0066cc')
                    ax_fold.set_xlabel("Time from Transit Center [Hours]", fontsize=10, labelpad=8)
                    ax_fold.set_ylabel("Normalized Flux", fontsize=10, labelpad=8)
                    ax_fold.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
                    ax_fold.tick_params(labelsize=9)
                    ax_fold.set_xlim(-5, 5)
                    
                    ax_fold.axvline(0, color='#ff4444', alpha=0.4, lw=1.5, linestyle='--', 
                                   label='Transit Center')
                    ax_fold.legend(fontsize=9, loc='upper right', framealpha=0.9)
                    
                for spine in ax_fold.spines.values():
                    spine.set_edgecolor('#999999')
                    spine.set_linewidth(0.8)
                    
                # --- Periodogram Placeholder ---
                ax_per = fig2.add_subplot(gs2[2])
                ax_per.text(0.5, 0.5, "Periodogram not available in this report version", 
                           ha='center', va='center', color='#666666', fontsize=10, style='italic')
                ax_per.set_title("Periodogram", fontsize=12, fontweight='bold', 
                                pad=12, color='#0066cc')
                ax_per.axis('off')

                # Footer for page 2
                footer_text = f"Generated by KSAS v{CURRENT_VERSION} | {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | Page 2/2 | {GITHUB_REPO}"
                fig2.text(0.5, 0.03, footer_text, ha='center', va='center', 
                         fontsize=7, color='#666666', style='italic')
                
                # Save page 2
                pdf.savefig(fig2, bbox_inches=None, pad_inches=0)
                plt.close(fig2)
            
            return filename
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
