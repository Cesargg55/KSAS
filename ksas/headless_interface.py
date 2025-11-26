import time
import logging

logger = logging.getLogger(__name__)

class HeadlessInterface:
    """
    Console-only interface for servers without GUI capabilities (Linux headless).
    """
    
    def __init__(self):
        self.stats = {
            'analyzed': 0,
            'total_analyzed': 0,
            'skipped': 0,
            'candidates': 0,
            'rejected': 0
        }
        self.current_target = "Waiting..."
        self.status = "Idle"
        self.start_time = time.time()
        
        print("="*70)
        print("   KSAS v3.0 - HEADLESS MODE (Server)")
        print("   Running in console-only mode (no GUI)")
        print("="*70)
        print()
    
    def send_update(self, update_type, value=None, **kwargs):
        """Handle updates in console mode."""
        if update_type == 'target':
            self.current_target = value
            print(f"\n{'='*70}")
            print(f"TARGET: {value}")
        elif update_type == 'status':
            self.status = value
        elif update_type == 'stats':
            self.stats.update(value)
            self._print_stats()
        elif update_type == 'log':
            # Don't print all logs in headless, too verbose
            # Only important ones
            if any(x in value for x in ['CANDIDATO', 'CONFIRMED', 'REJECTED', 'ERROR']):
                print(f"  {value}")
        elif update_type == 'results':
            print(f"\nRESULTS:")
            print(f"{value}")
        elif update_type == 'lightcurve':
            # Can't display in console
            pass
    
    def _print_stats(self):
        """Print statistics."""
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        
        rate = self.stats['analyzed'] / (elapsed / 60) if elapsed > 0 else 0
        
        print(f"\n--- STATISTICS (Runtime: {hours}h {minutes}m) ---")
        print(f"  Session Analyzed: {self.stats['analyzed']}")
        print(f"  Total Historical: {self.stats['total_analyzed']}")
        print(f"  Skipped (no data): {self.stats['skipped']}")
        print(f"  Candidates Found: {self.stats['candidates']}")
        print(f"  Rejected (vetting): {self.stats['rejected']}")
        print(f"  Analysis Rate: {rate:.2f} stars/min")
        
        # Estimate
        if rate > 0 and self.stats['candidates'] == 0:
            # Rough estimate: ~1 candidate per 500-1000 stars on average
            avg_to_candidate = 750
            remaining = avg_to_candidate - self.stats['analyzed']
            if remaining > 0:
                eta_minutes = remaining / rate
                eta_hours = eta_minutes / 60
                print(f"  Estimated time to next candidate: ~{eta_hours:.1f} hours")
        print("-" * 50)
    
    def is_paused(self):
        """Headless mode doesn't pause."""
        return False
    
    def run(self):
        """Headless doesn't need to run event loop."""
        pass
    
    def start_in_thread(self):
        """No thread needed for headless."""
        return None
