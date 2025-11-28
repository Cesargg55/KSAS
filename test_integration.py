import logging
import time
import sys
import os
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

from ksas.worker_pool import WorkerPool
from ksas.config import BLS_SNR_THRESHOLD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

# Mock components to avoid external dependencies during test
class MockLightCurve:
    def __init__(self):
        self.time = MagicMock()
        self.flux = MagicMock()
        self.time.value = [1, 2, 3]
        self.flux.value = [1, 1, 0.99]
        self.meta = {'OBJECT': 'TestStar'}
    def remove_nans(self): return self
    def normalize(self): return self
    def remove_outliers(self, **kwargs): return self
    def flatten(self, **kwargs): return self
    def to_periodogram(self, **kwargs):
        p = MagicMock()
        p.period_at_max_power.value = 1.0
        p.transit_time_at_max_power.value = 0.5
        p.duration_at_max_power.value = 0.1
        p.depth_at_max_power.value = 0.01
        p.max_power.value = 100
        return p
    def fold(self, **kwargs):
        f = MagicMock()
        f.time.value = [0]
        f.flux.value = [1]
        return f

def mock_init_worker():
    # Initialize mocks in worker
    import ksas.main as main_module
    main_module.worker_components = {}
    main_module.worker_components['downloader'] = MagicMock()
    main_module.worker_components['downloader'].download_lightcurve.return_value = MockLightCurve()
    
    main_module.worker_components['processor'] = MagicMock()
    main_module.worker_components['processor'].process_lightcurve.return_value = MockLightCurve()
    
    analyzer = MagicMock()
    analyzer.analyze.return_value = (MagicMock(is_candidate=True, period=1.0, power=100, depth=0.01), MagicMock())
    main_module.worker_components['bls_analyzer'] = analyzer
    
    tls = MagicMock()
    tls.analyze.return_value = (MagicMock(period=1.0, sde=10, depth=0.01), MagicMock())
    tls.is_significant.return_value = True
    main_module.worker_components['tls_analyzer'] = tls
    
    vetting = MagicMock()
    vetting.vet_candidate.return_value = MagicMock(passed=True)
    main_module.worker_components['vetting'] = vetting

def test_pipeline():
    print("Testing full pipeline with multiprocessing...")
    
    # We need to import main to access analyze_single_target
    import main
    
    # Patch the init_worker in main to use our mock
    # Actually, we can just pass our mock_init_worker to the pool
    # But analyze_single_target expects worker_components to be in main's scope
    # So we need to make sure mock_init_worker sets main.worker_components
    
    pool = WorkerPool(num_workers=2, initializer=mock_init_worker)
    
    print("Submitting task...")
    future = pool.submit_work(main.analyze_single_target, "TIC 123456")
    
    print("Waiting for result...")
    result = future.result(timeout=10)
    
    if result['status'] == 'candidate_confirmed':
        print("✅ SUCCESS: Pipeline processed target and found candidate")
    else:
        print(f"❌ FAILED: Status was {result['status']}")
        print(result)

    pool.shutdown()

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
