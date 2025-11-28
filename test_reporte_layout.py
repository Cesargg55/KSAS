import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os

# Mock data para simular un reporte
class MockLightCurve:
    def __init__(self):
        self.time = type('obj', (object,), {'value': np.linspace(0, 27, 1000)})()
        self.flux = type('obj', (object,), {'value': np.random.normal(1, 0.001, 1000)})()
        # Añadir transits simulados
        for i in range(5):
            transit_center = 5 + i * 5.4
            transit_mask = np.abs(self.time.value - transit_center) < 0.1
            self.flux.value[transit_mask] *= 0.995
        self.meta = {'OBJECT': 'TIC 123456789'}
    
    def scatter(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.scatter(self.time.value, self.flux.value, **kwargs)
        return ax
    
    def fold(self, period, epoch_time):
        folded_time = ((self.time.value - epoch_time + 0.5 * period) % period) - 0.5 * period
        folded_lc = type('obj', (object,), {
            'time': type('obj', (object,), {'value': folded_time})(),
            'flux': self.flux
        })()
        folded_lc.scatter = lambda ax=None, **kwargs: ax.scatter(folded_time, self.flux.value, **kwargs) if ax else None
        return folded_lc

class MockPeriodogram:
    def __init__(self):
        self.period = np.linspace(0.5, 15, 500)
        self.power = np.random.random(500) * 10
        # Añadir pico principal
        self.power[200] = 50
    
    def plot(self, ax=None, view='period'):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(self.period, self.power)
        ax.set_xlabel('Period (days)')
        ax.set_ylabel('Power')
        return ax

class MockResult:
    def __init__(self):
        self.target_id = "TIC 123456789"
        self.period = 5.4123
        self.t0 = 1350.234
        self.duration = 0.08
        self.depth = 0.005
        self.power = 50.2
        self.sde = 12.3

# Crear directorio de salida
os.makedirs("test_output", exist_ok=True)

# Simular el código actual de visualizer.py
lc = MockLightCurve()
periodogram = MockPeriodogram()
result = MockResult()

target_id = result.target_id
safe_id = target_id.replace(" ", "_")
filename = os.path.join("test_output", f"{safe_id}_report_test.png")

print("Generando reporte de prueba...")

# Código ACTUAL del visualizer
fig = Figure(figsize=(10, 15), constrained_layout=True)
canvas = FigureCanvasAgg(fig)

# Create subplots manually
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

# 1. Light Curve
lc.scatter(ax=ax1, label="Flux", s=1, alpha=0.6)
ax1.set_title(f"{target_id} - Light Curve")
ax1.set_xlabel("Time (BJD - 2457000)")
ax1.set_ylabel("Normalized Flux")

# 2. Periodogram
periodogram.plot(ax=ax2, view='period')
power = result.power if hasattr(result, 'power') else result.sde
ax2.set_title(f"BLS Periodogram (Max Power: {power:.2f})")
ax2.set_xlabel("Period (days)")
ax2.set_ylabel("Power")

# 3. Folded Light Curve
folded = lc.fold(period=result.period, epoch_time=result.t0)
folded.scatter(ax=ax3, label=f"Period: {result.period:.4f} d", s=2, alpha=0.5)
ax3.set_title(f"Folded Light Curve")
ax3.set_xlabel("Phase")
ax3.set_ylabel("Normalized Flux")

fig.savefig(filename, dpi=150, bbox_inches='tight')
plt.close(fig)

print(f"✅ Reporte generado: {filename}")
print(f"Tamaño del archivo: {os.path.getsize(filename)} bytes")
print("\nRevisa la imagen para verificar si hay overlapping de texto.")
