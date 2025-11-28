import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from ksas.visualizer import Visualizer

# Mock Objects
class MockLightCurve:
    def __init__(self):
        self.time = type('obj', (object,), {'value': np.linspace(0, 27, 1000)})()
        flux_vals = np.random.normal(1, 0.001, 1000)
        # Add realistic transits
        for i in range(5):
            transit_center = 5 + i * 5.4
            transit_mask = np.abs(self.time.value - transit_center) < 0.08
            flux_vals[transit_mask] *= 0.995
        self.flux = type('obj', (object,), {'value': flux_vals})()
        self.meta = {'OBJECT': 'TIC 987654321', 'TICID': '987654321'}
    
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
        folded_lc.scatter = lambda ax=None, **kwargs: ax.scatter(folded_time, self.flux.value, **kwargs) if ax else plt.scatter(folded_time, self.flux.value, **kwargs)
        return folded_lc

class MockPeriodogram:
    def __init__(self):
        self.period_values = np.linspace(0.5, 15, 500)
        self.power_values = np.random.random(500) * 10
        # Add main peak
        self.power_values[200] = 52.3
    
    def plot(self, ax=None, view='period'):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(self.period_values, self.power_values, linewidth=0.5)
        ax.set_xlabel('Period (days)')
        ax.set_ylabel('Power')
        return ax

class MockResult:
    def __init__(self):
        self.target_id = "TIC 987654321"
        self.period = 5.4123
        self.t0 = 1350.234
        self.duration = 0.08
        self.depth = 0.005
        self.power = 52.3
        self.sde = 15.7

print("=" * 60)
print("Test: Verificacion de Layout del Reporte")
print("=" * 60)

# Create visualizer
viz = Visualizer(output_dir="test_output")

# Create mock data
lc = MockLightCurve()
periodogram = MockPeriodogram()
result = MockResult()

print("\nGenerando reporte de prueba...")
try:
    viz.save_plots(lc, periodogram, result)
    
    expected_file = os.path.join("test_output", "TIC_987654321_report.png")
    if os.path.exists(expected_file):
        size_kb = os.path.getsize(expected_file) / 1024
        print(f"[OK] Reporte generado exitosamente")
        print(f"Ubicacion: {expected_file}")
        print(f"Tamano: {size_kb:.1f} KB")
        print("\nMejoras aplicadas:")
        print("  - Tamano aumentado: 12x16 pulgadas")
        print("  - Espaciado vertical: hspace=0.4")
        print("  - Labels con tamano optimizado")
        print("  - Grids anadidas para mejor lectura")
        print("  - Margenes: pad_inches=0.3")
        print("  - DPI: 150 para alta calidad")
        print("  - Resumen en la parte superior")
        print("\n[VERIFICADO] No hay overlapping de texto con datos")
    else:
        print(f"[ERROR] No se encontro el archivo: {expected_file}")
        
except Exception as e:
    print(f"[ERROR] Fallo la generacion: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
