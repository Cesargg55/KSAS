import threading
import queue
import time
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class WorkerPool:
    """
    Manages parallel workers for analyzing multiple stars simultaneously.
    Uses MULTIPROCESSING for true parallelism (bypassing GIL).
    """
    
    def __init__(self, num_workers=4, max_queue_size=50, initializer=None):
        """
        Args:
            num_workers: Number of parallel analysis processes
            max_queue_size: Maximum number of pending targets
            initializer: Function to initialize worker process
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        
        # Thread-safe queues (for communicating with main thread)
        self.work_queue = queue.Queue(maxsize=max_queue_size)
        self.result_queue = queue.Queue()
        
        # Process pool
        self.executor = ProcessPoolExecutor(max_workers=num_workers, initializer=initializer)
        
        # Active futures
        self.active_futures = set()
        self.lock = threading.Lock()
        
        # Stats
        self.stats = {
            'submitted': 0,
            'completed': 0,
            'in_progress': 0
        }
        self.stats_lock = threading.Lock()
        
        logger.info(f"Initialized worker pool with {num_workers} workers")
    
    def submit_work(self, func, *args, **kwargs):
        """
        Submit work to the pool.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Future object
        """
        future = self.executor.submit(func, *args, **kwargs)
        
        with self.lock:
            self.active_futures.add(future)
        
        with self.stats_lock:
            self.stats['submitted'] += 1
            self.stats['in_progress'] += 1
        
        # Add callback to handle completion
        future.add_done_callback(self._on_complete)
        
        return future
    
    def _on_complete(self, future):
        """Callback when a future completes."""
        with self.lock:
            self.active_futures.discard(future)
        
        with self.stats_lock:
            self.stats['completed'] += 1
            self.stats['in_progress'] -= 1
        
        # Put result in queue
        try:
            result = future.result()
            self.result_queue.put(result)
        except Exception as e:
            logger.error(f"Worker task failed: {e}")
            self.result_queue.put({'error': str(e)})
    
    def get_result(self, timeout=0.1):
        """
        Get a result from the queue (non-blocking).
        
        Args:
            timeout: How long to wait for result
            
        Returns:
            Result dict or None if queue empty
        """
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_active_count(self):
        """Get number of active workers."""
        with self.lock:
            return len(self.active_futures)
    
    def get_stats(self):
        """Get worker stats."""
        with self.stats_lock:
            return self.stats.copy()
    
    def wait_for_capacity(self, min_capacity=1):
        """
        Wait until there's capacity for more work.
        
        Args:
            min_capacity: Minimum number of free workers needed
        """
        while self.get_active_count() >= (self.num_workers - min_capacity + 1):
            time.sleep(0.1)
    
    def shutdown(self, wait=True):
        """Shutdown the worker pool."""
        logger.info("Shutting down worker pool...")
        self.executor.shutdown(wait=wait)
