import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

# Mock ksas modules to avoid full initialization
sys.modules['ksas.downloader'] = MagicMock()
sys.modules['ksas.processor'] = MagicMock()
sys.modules['ksas.analyzer'] = MagicMock()
sys.modules['ksas.tls_analyzer'] = MagicMock()
sys.modules['ksas.vetting'] = MagicMock()
sys.modules['ksas.visualizer'] = MagicMock()
sys.modules['ksas.tracking'] = MagicMock()
sys.modules['ksas.candidate_db'] = MagicMock()
sys.modules['ksas.smart_targeting'] = MagicMock()
sys.modules['ksas.worker_pool'] = MagicMock()

import main

def test_worker_logic():
    print("Testing main.py worker logic...")
    
    # 1. Test init_worker
    print("Running init_worker()...")
    try:
        main.init_worker()
        print("[OK] init_worker executed")
    except Exception as e:
        print(f"[FAIL] init_worker failed: {e}")
        return

    # Verify worker_components are populated
    components = main.worker_components
    expected_keys = ['downloader', 'processor', 'bls_analyzer', 'tls_analyzer', 'vetting']
    missing = [k for k in expected_keys if k not in components]
    
    if missing:
        print(f"[FAIL] Missing components: {missing}")
        return
    else:
        print(f"[OK] All components initialized: {list(components.keys())}")

    # 2. Test analyze_single_target
    print("Running analyze_single_target()...")
    
    # Setup mocks for components
    mock_downloader = components['downloader']
    mock_downloader.download_lightcurve.return_value = "mock_lc"
    
    mock_processor = components['processor']
    mock_processor.process_lightcurve.return_value = "clean_lc"
    
    mock_bls = components['bls_analyzer']
    mock_bls_result = MagicMock()
    mock_bls_result.is_candidate = False
    mock_bls_result.power = 5.0
    mock_bls_result.period = 1.0
    mock_bls_result.t0 = 0.0
    mock_bls_result.duration = 0.1
    mock_bls_result.depth = 0.01
    mock_bls.analyze.return_value = (mock_bls_result, "periodogram")
    
    try:
        result = main.analyze_single_target("TIC 123")
        print(f"[OK] Analysis result: {result['status']}")
        
        if result['status'] == 'analyzed_no_signal':
            print("[PASS] Logic flow correct for no signal")
        else:
            print(f"[FAIL] Unexpected status: {result['status']}")
            
    except Exception as e:
        print(f"[FAIL] analyze_single_target failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_worker_logic()
