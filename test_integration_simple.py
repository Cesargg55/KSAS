import logging
import sys
import os
import time

# Add current directory to path
sys.path.append(os.getcwd())

from ksas.worker_pool import WorkerPool

# Configure logging
logging.basicConfig(level=logging.INFO)

def simple_task(x):
    return x * x

def test_worker_pool():
    print("Testing WorkerPool with simple task...")
    
    try:
        pool = WorkerPool(num_workers=2)
        
        print("Submitting tasks...")
        futures = [pool.submit_work(simple_task, i) for i in range(5)]
        
        results = []
        for f in futures:
            results.append(f.result(timeout=5))
            
        print(f"Results: {results}")
        
        if results == [0, 1, 4, 9, 16]:
            print("[SUCCESS] WorkerPool is working correctly with multiprocessing.")
        else:
            print("[FAIL] Results do not match expected.")
            
        pool.shutdown()
        
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        # On Windows, multiprocessing needs this
        import multiprocessing
        multiprocessing.freeze_support()
        
    test_worker_pool()
