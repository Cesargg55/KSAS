
import sys
import os
import numpy as np

# Add current directory to path
sys.path.append(os.getcwd())

from ksas.report_generator import ExoFOPReportGenerator
from ksas.observatory_logic import ObservatoryLogic

def test_refined_report():
    print("Testing refined report generation...")
    
    # Dummy data
    tic_id = "12345678"
    candidate_data = {
        'period': 11.9022,
        't0': 3912.0,
        'depth': 0.003,
        'duration': 0.166,
        'snr': 456.6,
        'score': 100,
        'r_star': 0.68,
        'm_star': 0.68,
        'teff': 4048,
        'disposition': 'PC',
        'tag': 'Test_Refined',
        'notes': 'Test Notes'
    }
    
    # 1. Run Calculation Logic
    print("Running calculations...")
    enriched_data = ObservatoryLogic.calculate_derived_parameters(candidate_data)
    
    print("Calculated Parameters:")
    print(f"Inclination: {enriched_data.get('inclination'):.1f} deg")
    print(f"Impact Param: {enriched_data.get('impact_parameter'):.2f}")
    
    # Dummy light curve
    time = np.linspace(3900, 3930, 1000)
    flux = np.ones_like(time)
    lc_data = (time, flux)
    
    # 2. Generate Report
    generator = ExoFOPReportGenerator(output_dir="test_output")
    
    try:
        filename = generator.generate_report(tic_id, enriched_data, lc_data)
        if filename:
            print(f"Success! Report generated: {filename}")
        else:
            print("Failed to generate report (returned None).")
    except Exception as e:
        print(f"Exception caught during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_refined_report()
