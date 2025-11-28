import matplotlib.pyplot as plt
import numpy as np
from unittest.mock import MagicMock

# Mock LightCurve
class MockLightCurve:
    def __init__(self):
        self.time = MagicMock()
        self.flux = MagicMock()
        self.time.value = np.linspace(0, 27, 1000)
        self.flux.value = np.random.normal(1, 0.001, 1000)
        self.meta = {'OBJECT': 'TestStar'}
    
    def scatter(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(self.time.value, self.flux.value, **kwargs)
        return ax

    def fold(self, **kwargs):
        return self

# Mock Periodogram
class MockPeriodogram:
    def plot(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(np.linspace(0.5, 10, 100), np.random.random(100))
        return ax

# Mock Result
class MockResult:
    def __init__(self):
        self.target_id = "TIC 123456789"
        self.period = 3.14159
        self.t0 = 1350.0
        self.duration = 0.1
        self.depth = 0.005
        self.power = 50.0
        self.sde = 10.0

def reproduce_issue():
    print("Generating reproduction plot...")
    
    lc = MockLightCurve()
    periodogram = MockPeriodogram()
    result = MockResult()
    
    # Copy of the show_plots code from visualizer.py
    target_id = result.target_id
    
    # Create figure with constrained_layout for better automatic spacing
    # This fixes the overlapping text and whitespace issues
    fig = plt.figure(figsize=(14, 16), constrained_layout=True)
    gs = fig.add_gridspec(4, 1, height_ratios=[1, 1, 1, 0.4])
    
    # 1. Light Curve
    ax1 = fig.add_subplot(gs[0])
    lc.scatter(ax=ax1, label="Normalized Flux")
    ax1.set_title(f"{target_id} - RAW LIGHT CURVE", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Time (BJD - 2457000)")
    ax1.set_ylabel("Normalized Flux")
    ax1.grid(alpha=0.3)
    
    # Explanation text for light curve - Moved to right side to avoid overlapping data
    ax1.text(1.02, 0.5, 
            "¿QUÉ ES ESTO?\n"
            "Esta es la curva de luz:\nmuestra el brillo de la estrella\na lo largo del tiempo.\n"
            "Las caídas periódicas indican\nun posible planeta.",
            transform=ax1.transAxes, fontsize=9, verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    # 2. Periodogram
    ax2 = fig.add_subplot(gs[1])
    periodogram.plot(ax=ax2, view='period')
    ax2.set_title(f"BLS PERIODOGRAM - Búsqueda de Periodicidad", fontsize=14, fontweight='bold')
    ax2.axvline(result.period, color='red', linestyle='--', linewidth=2, label=f'Detected Period: {result.period:.4f} d')
    ax2.legend(loc='upper right')
    ax2.grid(alpha=0.3)
    
    # Explanation for periodogram
    ax2.text(1.02, 0.5,
            "¿QUÉ ES ESTO?\n"
            f"Muestra la 'potencia' de\ndiferentes periodos.\n"
            f"Pico alto = Señal fuerte\nen {result.period:.4f} días.",
            transform=ax2.transAxes, fontsize=9, verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.3))
    
    # 3. Folded Light Curve
    ax3 = fig.add_subplot(gs[2])
    folded = lc.fold(period=result.period, epoch_time=result.t0)
    folded.scatter(ax=ax3)
    ax3.set_title(f"CURVA DE LUZ PLEGADA - Periodo: {result.period:.4f} días", fontsize=14, fontweight='bold')
    ax3.set_xlabel("Fase del Periodo")
    ax3.set_ylabel("Normalized Flux")
    ax3.grid(alpha=0.3)
    
    # Mark the transit
    ax3.axvline(0, color='red', linestyle='--', alpha=0.5, label='Centro del Tránsito')
    ax3.legend(loc='upper right')
    
    # Explanation for folded light curve
    ax3.text(1.02, 0.5,
            "¿QUÉ ES ESTO?\n"
            f"Órbitas 'apiladas'.\n"
            f"Una forma de 'U' clara\nindica un planeta.",
            transform=ax3.transAxes, fontsize=9, verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='lime', alpha=0.3))
    
    # 4. Summary Box
    ax4 = fig.add_subplot(gs[3])
    ax4.axis('off')
    
    summary_text = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         🌟 CANDIDATO DETECTADO 🌟                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Target ID:       {target_id:<40}                    ║
║  Periodo:         {result.period:.6f} días                                          ║
║  Profundidad:     {result.depth:.6f} (Δ Brillo)                                    ║
║  SNR (Power):     {result.power:.2f}                                                ║
║  Duración:        {result.duration*24:.2f} horas                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    
    ax4.text(0.5, 0.5, summary_text, fontsize=10, family='monospace',
            ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='orange', alpha=0.5))
    
    # Main title
    fig.suptitle(f"⭐ KSAS - REPORTE DE CANDIDATO EXOPLANET ⭐\n{target_id}", 
                fontsize=16, fontweight='bold', color='white')
    
    # No tight_layout needed with constrained_layout
    
    plt.savefig("reproduce_plot.png", dpi=100, facecolor='#1a1a1a')
    print("Plot saved to reproduce_plot.png")

if __name__ == "__main__":
    reproduce_issue()
