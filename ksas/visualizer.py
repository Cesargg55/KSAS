import matplotlib.pyplot as plt
import os
import logging

logger = logging.getLogger(__name__)

class Visualizer:
    """
    Generates and saves plots for analysis results.
    """
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        plt.style.use('dark_background')

    def save_plots(self, lc, periodogram, result):
        """
        Creates and saves a summary plot for a candidate.
        
        Args:
            lc (lightkurve.LightCurve): The processed light curve.
            periodogram (lightkurve.periodogram.Periodogram): The BLS periodogram.
            result (AnalysisResult or TLSResult): The analysis result.
        """
        try:
            # Get target_id from result or light curve metadata
            if hasattr(result, 'target_id'):
                target_id = result.target_id
            else:
                # Try to get from light curve metadata
                target_id = str(lc.meta.get('OBJECT', lc.meta.get('TICID', 'Unknown')))
                if not target_id.startswith('TIC'):
                    target_id = f"TIC {target_id}"
            
            safe_id = target_id.replace(" ", "_")
            filename = os.path.join(self.output_dir, f"{safe_id}_report.png")
            
            logger.info(f"Generating plot for {target_id}...")
            
            fig, axes = plt.subplots(3, 1, figsize=(10, 15))
            
            # 1. Light Curve
            lc.scatter(ax=axes[0], label="Flux")
            axes[0].set_title(f"{target_id} - Light Curve")
            
            # 2. Periodogram
            periodogram.plot(ax=axes[1], view='period')
            # Get power from result
            power = result.power if hasattr(result, 'power') else result.sde
            axes[1].set_title(f"BLS Periodogram (Max Power: {power:.2f})")
            
            # 3. Folded Light Curve
            folded = lc.fold(period=result.period, epoch_time=result.t0)
            folded.scatter(ax=axes[2], label=f"Period: {result.period:.4f} d")
            axes[2].set_title(f"Folded Light Curve")
            
            plt.tight_layout()
            plt.savefig(filename)
            plt.close(fig)
            
            logger.info(f"Plot saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error generating plot: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def show_plots(self, lc, periodogram, result):
        """
        Shows interactive plot window with detailed explanations.
        EDUCATIONAL: Explains what each graph means and what the data shows.
        
        Args:
            lc (lightkurve.LightCurve): The processed light curve.
            periodogram (lightkurve.periodogram.Periodogram): The BLS periodogram.
            result (AnalysisResult): The analysis result.
        """
        try:
            target_id = result.target_id
            
            logger.info(f"Opening interactive window for {target_id}...")
            
            # Create figure with larger size for readability
            fig = plt.figure(figsize=(14, 16))
            gs = fig.add_gridspec(4, 1, height_ratios=[1, 1, 1, 0.3], hspace=0.35)
            
            # 1. Light Curve
            ax1 = fig.add_subplot(gs[0])
            lc.scatter(ax=ax1, label="Normalized Flux", s=1, alpha=0.6)
            ax1.set_title(f"{target_id} - RAW LIGHT CURVE", fontsize=14, fontweight='bold')
            ax1.set_xlabel("Time (BJD - 2457000)")
            ax1.set_ylabel("Normalized Flux")
            ax1.grid(alpha=0.3)
            
            # Explanation text for light curve
            ax1.text(0.02, 0.98, 
                    "¿QUÉ ES ESTO?\n"
                    "Esta es la curva de luz: muestra el brillo de la estrella a lo largo del tiempo.\n"
                    "Las caídas periódicas en el brillo pueden indicar un planeta transitando.",
                    transform=ax1.transAxes, fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
            
            # 2. Periodogram
            ax2 = fig.add_subplot(gs[1])
            periodogram.plot(ax=ax2, view='period')
            ax2.set_title(f"BLS PERIODOGRAM - Búsqueda de Periodicidad", fontsize=14, fontweight='bold')
            ax2.axvline(result.period, color='red', linestyle='--', linewidth=2, label=f'Detected Period: {result.period:.4f} d')
            ax2.legend()
            ax2.grid(alpha=0.3)
            
            # Explanation for periodogram
            ax2.text(0.02, 0.98,
                    "¿QUÉ ES ESTO?\n"
                    f"Este gráfico muestra la 'potencia' de diferentes periodos.\n"
                    f"El pico más alto (Power={result.power:.1f}) está en {result.period:.4f} días.\n"
                    f"Esto significa que hay una señal que se repite cada {result.period:.4f} días.",
                    transform=ax2.transAxes, fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.3))
            
            # 3. Folded Light Curve
            ax3 = fig.add_subplot(gs[2])
            folded = lc.fold(period=result.period, epoch_time=result.t0)
            folded.scatter(ax=ax3, s=2, alpha=0.5)
            ax3.set_title(f"CURVA DE LUZ PLEGADA - Periodo: {result.period:.4f} días", fontsize=14, fontweight='bold')
            ax3.set_xlabel("Fase del Periodo")
            ax3.set_ylabel("Normalized Flux")
            ax3.grid(alpha=0.3)
            
            # Mark the transit
            ax3.axvline(0, color='red', linestyle='--', alpha=0.5, label='Centro del Tránsito')
            ax3.legend()
            
            # Explanation for folded light curve
            ax3.text(0.02, 0.98,
                    "¿QUÉ ES ESTO?\n"
                    f"Todas las órbitas están 'apiladas' una encima de otra.\n"
                    f"Si hay un planeta, verás una 'U' clara en el centro (profundidad={result.depth:.4f}).\n"
                    f"Una señal clara = POSIBLE EXOPLANETA!",
                    transform=ax3.transAxes, fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lime', alpha=0.3))
            
            # 4. Summary Box
            ax4 = fig.add_subplot(gs[3])
            ax4.axis('off')
            
            summary_text = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         🌟 CANDIDATO DETECTADO 🌟                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Target ID:       {target_id:<60} ║
║  Periodo:         {result.period:.6f} días                                          ║
║  Profundidad:     {result.depth:.6f} (Δ Brillo)                                    ║
║  SNR (Power):     {result.power:.2f}                                                ║
║  Duración:        {result.duration*24:.2f} horas                                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  SIGNIFICADO:                                                                 ║
║  - Un periodo de {result.period:.2f} días significa que el planeta orbita su estrella    ║
║    en aproximadamente {result.period:.2f} días.                                         ║
║  - La profundidad de {result.depth*100:.3f}% indica cuánto brillo bloquea el planeta.   ║
║  - SNR alto ({result.power:.1f}) = señal fuerte y confiable.                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
            """
            
            ax4.text(0.5, 0.5, summary_text, fontsize=10, family='monospace',
                    ha='center', va='center',
                    bbox=dict(boxstyle='round', facecolor='orange', alpha=0.5))
            
            # Main title
            fig.suptitle(f"⭐ KSAS - REPORTE DE CANDIDATO EXOPLANET ⭐\n{target_id}", 
                        fontsize=16, fontweight='bold', color='white')
            
            plt.tight_layout()
            
            # Save before showing
            safe_id = target_id.replace(" ", "_")
            filename = os.path.join(self.output_dir, f"{safe_id}_report.png")
            plt.savefig(filename, dpi=100, facecolor='#1a1a1a')
            logger.info(f"Plot saved to {filename}")
            
            # Show interactive window and PAUSE for user to see
            logger.info("⚠️  VENTANA ABIERTA - Cierra la ventana para continuar la búsqueda...")
            plt.show(block=True)  # This will block until user closes the window
            
        except Exception as e:
            logger.error(f"Error showing plot for {result.target_id}: {e}")
