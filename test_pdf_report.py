import matplotlib.pyplot as plt
import numpy as np
from unittest.mock import MagicMock
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from ksas.visualizer import Visualizer

# Mock Objects
class MockLightCurve:
    def __init__(self):
        self.time = MagicMock()
        self.flux = MagicMock()
        self.time.value = np.linspace(0, 27, 1000)
        self.flux.value = np.random.normal(1, 0.001, 1000)
        self.meta = {'OBJECT': 'TestStar_PDF'}
    
    def scatter(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.scatter(self.time.value, self.flux.value, **kwargs)
        return ax

    def fold(self, **kwargs):
        return self

class MockPeriodogram:
    def plot(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(np.linspace(0.5, 10, 100), np.random.random(100))
        return ax

class MockResult:
    def __init__(self):
        self.target_id = "TIC 987654321"
        self.period = 3.14159
        self.t0 = 1350.0
        self.duration = 0.1
        self.depth = 0.005
        self.power = 50.0
        self.sde = 10.0

def test_pdf_generation():
    print("Testing PDF report generation...")
    
    viz = Visualizer(output_dir="test_output")
    
    lc = MockLightCurve()
    periodogram = MockPeriodogram()
    result = MockResult()
    
    try:
        viz.save_plots(lc, periodogram, result)
        
        expected_file = os.path.join("test_output", "TIC_987654321_report.pdf")
        if os.path.exists(expected_file):
            print(f"[SUCCESS] PDF report generated at {expected_file}")
            print(f"Size: {os.path.getsize(expected_file)} bytes")
        else:
            print(f"[FAIL] File not found at {expected_file}")
            
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
