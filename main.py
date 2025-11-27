import time
import logging
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from ksas.downloader import DataDownloader
from ksas.processor import DataProcessor
from ksas.analyzer import Analyzer
from ksas.tls_analyzer import TLSAnalyzer
from ksas.vetting import CandidateVetting
from ksas.visualizer import Visualizer
from ksas.tracking import StarTracker
from ksas.candidate_db import CandidateDatabase
from ksas.smart_targeting import SmartTargeting
from ksas.worker_pool import WorkerPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [KSAS] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("KSAS_Main")

# Global components (shared across threads)
downloader = None
processor = None
bls_analyzer = None
tls_analyzer = None
vetting = None
visualizer = None
tracker = None
candidate_db = None

# Thread locks
tracker_lock = threading.Lock()
candidate_lock = threading.Lock()
stats_lock = threading.Lock()

def can_use_gui():
    """Detect if GUI is available."""
    if sys.platform.startswith('linux'):
        if 'DISPLAY' not in os.environ:
            return False
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        return True
    except Exception:
        return False

def analyze_single_target(target, stats):
    """
    Analyze a single target (called by worker threads).
    Returns result dict for main thread to process.
    """
    global downloader, processor, bls_analyzer, tls_analyzer, vetting, tracker, candidate_db
    
    result = {
        'target': target,
        'status': 'init',
        'lc': None,
        'bls_result': None,
        'tls_result': None,
        'vet_result': None,
        'candidate': False
    }
    
    try:
        # Check if already analyzed
        with tracker_lock:
            if tracker.is_analyzed(target):
                result['status'] = 'already_analyzed'
                return result
        
        # 1. Download
        lc = downloader.download_lightcurve(target)
        if lc is None:
            result['status'] = 'no_data'
            with tracker_lock:
                tracker.mark_analyzed(target)
            return result
        
        result['lc'] = lc
        
        # 2. Process
        clean_lc = processor.process_lightcurve(lc)
        if clean_lc is None:
            result['status'] = 'processing_failed'
            with tracker_lock:
                tracker.mark_analyzed(target)
            return result
        
        result['lc'] = clean_lc
        
        # 3. BLS Analysis
        bls_result, bls_periodogram = bls_analyzer.analyze(clean_lc, target)
        
        if bls_result is None:
            result['status'] = 'bls_failed'
            with tracker_lock:
                tracker.mark_analyzed(target)
            return result
        
        result['bls_result'] = bls_result
        result['bls_periodogram'] = bls_periodogram
        
        # 4. TLS Analysis (if BLS found something)
        tls_result = None
        if bls_result.is_candidate:
            tls_result, tls_obj = tls_analyzer.analyze(clean_lc, target)
            result['tls_result'] = tls_result
        
        # Mark as analyzed
        with tracker_lock:
            tracker.mark_analyzed(target)
            with stats_lock:
                stats['analyzed'] += 1
                stats['total_analyzed'] += 1
        
        # 5. Check if candidate
        if bls_result.is_candidate or (tls_result and tls_analyzer.is_significant(tls_result)):
            # Use TLS results if available, otherwise BLS
            period = tls_result.period if tls_result else bls_result.period
            t0 = tls_result.t0 if tls_result else bls_result.t0
            duration = tls_result.duration if tls_result else bls_result.duration
            
            # 6. Vetting
            vet_result = vetting.vet_candidate(clean_lc, period, t0, duration)
            result['vet_result'] = vet_result
            
            if vet_result.passed:
                result['status'] = 'candidate_confirmed'
                result['candidate'] = True
                
                # Save to candidate database (thread-safe)
                with candidate_lock:
                    candidate_db.add_candidate(
                        tic_id=target,
                        period=period,
                        depth=tls_result.depth if tls_result else bls_result.depth,
                        bls_power=bls_result.power,  # Always save BLS power
                        tls_sde=tls_result.sde if tls_result else None,  # Save TLS SDE if available
                        vetting_passed=vet_result.passed,  # Save vetting status
                        t0=t0,
                        duration=duration
                    )
                
                with stats_lock:
                    stats['candidates'] += 1
            else:
                result['status'] = 'candidate_rejected'
                with stats_lock:
                    stats['rejected'] += 1
        else:
            result['status'] = 'analyzed_no_signal'
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing {target}: {e}")
        result['status'] = 'error'
        result['error'] = str(e)
        return result

def parallel_analysis_loop(interface, use_gui=True, num_workers=4):
    """
    Main analysis loop with parallel processing.
    
    Args:
        interface: GUI or headless interface
        use_gui: Whether GUI is available
        num_workers: Number of parallel workers
    """
    global downloader, processor, bls_analyzer, tls_analyzer, vetting, visualizer, tracker, candidate_db
    
    logger.info("Initializing KSAS components...")
    interface.send_update('log', "🔧 Initializing components...")
    
    # Initialize components (shared across threads)
    downloader = DataDownloader()
    processor = DataProcessor()
    bls_analyzer = Analyzer(snr_threshold=10)
    tls_analyzer = TLSAnalyzer(sde_threshold=7.0)
    vetting = CandidateVetting()
    visualizer = Visualizer()
    tracker = StarTracker()
    candidate_db = CandidateDatabase()
    
    interface.send_update('log', f"✓ Loaded {tracker.get_count()} previously analyzed stars")
    interface.send_update('log', f"🚀 Starting {num_workers} parallel workers...")
    
    # Statistics
    stats = {
        'analyzed': 0,
        'total_analyzed': tracker.get_count(),
        'skipped': 0,
        'candidates': 0,
        'rejected': 0
    }
    interface.send_update('stats', stats)
    
    # Smart targeting
    smart_targeting = SmartTargeting()
    target_generator = smart_targeting.generate_smart_targets()
    
    # Worker pool
    pool = WorkerPool(num_workers=num_workers)
    
    interface.send_update('log', "🎯 Starting autonomous search mode...")
    
    start_time = time.time()
    last_stats_update = time.time()
    
    try:
        # Keep submitting work to pool
        targets_submitted = 0
        
        while True:
            # Check if paused
            while interface.is_paused():
                time.sleep(0.5)
            
            # Submit new work if pool has capacity
            if pool.get_active_count() < num_workers:
                target = next(target_generator)
                
                # Check if already analyzed before submitting
                with tracker_lock:
                    if tracker.is_analyzed(target):
                        continue
                
                # Submit to pool
                pool.submit_work(analyze_single_target, target, stats)
                targets_submitted += 1
                
                interface.send_update('target', f"{target} (Worker pool: {pool.get_active_count()}/{num_workers})")
            
            # Process results
            result = pool.get_result(timeout=0.1)
            if result:
                handle_result(result, interface, use_gui, stats)
            
            # Update stats periodically
            if time.time() - last_stats_update > 2.0:
                interface.send_update('stats', stats.copy())
                last_stats_update = time.time()
                
                # Calculate rate
                elapsed = time.time() - start_time
                if elapsed > 60:  # After 1 minute
                    rate = stats['analyzed'] / (elapsed / 60)
                    interface.send_update('log', f"📊 Analysis rate: {rate:.1f} stars/min")
            
            time.sleep(0.05)  # Small delay to prevent CPU spinning
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        interface.send_update('log', f"❌ CRITICAL ERROR: {e}")
    finally:
        # Shutdown pool
        interface.send_update('log', "🛑 Shutting down worker pool...")
        pool.shutdown(wait=True)
        
        # Save tracker
        tracker.save()
        interface.send_update('log', "🛑 Analysis stopped")
        interface.send_update('status', "Stopped")

def handle_result(result, interface, use_gui, stats):
    """Handle a completed analysis result."""
    target = result['target']
    status = result['status']
    
    if status == 'no_data':
        with stats_lock:
            stats['skipped'] += 1
        interface.send_update('log', f"⏭️ No data for {target}")
        
    elif status == 'already_analyzed':
        interface.send_update('log', f"⏭️ {target} already analyzed")
        
    elif status == 'processing_failed' or status == 'bls_failed':
        with stats_lock:
            stats['skipped'] += 1
        interface.send_update('log', f"⚠️ Analysis failed for {target}")
        
    elif status == 'candidate_confirmed':
        interface.send_update('log', f"🌟🌟🌟 EXOPLANET CANDIDATE: {target} 🌟🌟🌟")
        interface.send_update('log', f"✓ Passed all vetting tests")
        
        # Show visualization (threadsafe)
        if use_gui and result.get('lc') and result.get('bls_periodogram'):
            tls_result = result.get('tls_result')
            bls_result = result.get('bls_result')
            result_to_show = tls_result if tls_result and tls_analyzer.is_significant(tls_result) else bls_result
            
            # Save plots (show_plots might block, so just save)
            visualizer.save_plots(result['lc'], result['bls_periodogram'], result_to_show)
            interface.send_update('log', f"Report saved to output/ folder")
        
    elif status == 'candidate_rejected':
        interface.send_update('log', f"❌ Candidate rejected: {target}")
        
    elif status == 'analyzed_no_signal':
        interface.send_update('log', f"✓ Analyzed {target}. No significant signals.")
        
    elif status == 'error':
        interface.send_update('log', f"❌ Error with {target}: {result.get('error', 'Unknown')}")

def check_missing_reports(candidate_db, interface):
    """
    Check for missing report images and optionally generate them.
    """
    import tkinter as tk
    from tkinter import messagebox
    from ksas.locales import T
    
    missing_tics = []
    for tic_id in candidate_db.candidates:
        safe_id = tic_id.replace(" ", "_")
        report_path = os.path.join("output", f"{safe_id}_report.png")
        if not os.path.exists(report_path):
            missing_tics.append(tic_id)
            
    if not missing_tics:
        return

    # Ask user
    # Use existing interface root if available, otherwise create one (headless case handled elsewhere)
    parent = getattr(interface, 'root', None)
    
    if parent:
        response = messagebox.askyesno(
            T.get('reports_missing_title'),
            T.get('reports_missing_prompt').format(count=len(missing_tics)),
            parent=parent
        )
    else:
        # Fallback for headless or pre-gui (should not happen in this flow)
        root = tk.Tk()
        root.withdraw()
        response = messagebox.askyesno(
            T.get('reports_missing_title'),
            T.get('reports_missing_prompt').format(count=len(missing_tics))
        )
        root.destroy()
    
    if response:
        print(T.get('generating_reports'))
        interface.send_update('log', T.get('generating_reports'))
        
        # Initialize components locally
        downloader = DataDownloader()
        processor = DataProcessor()
        bls_analyzer = Analyzer(snr_threshold=5) # Low threshold to ensure we get a plot
        visualizer = Visualizer()
        
        count = 0
        for tic in missing_tics:
            try:
                interface.send_update('log', f"Generating report for {tic}...")
                
                # 1. Download
                lc = downloader.download_lightcurve(tic)
                if lc is None:
                    continue
                
                # 2. Process
                clean_lc = processor.process_lightcurve(lc)
                if clean_lc is None:
                    continue
                
                # 3. BLS (to get periodogram)
                bls_result, bls_periodogram = bls_analyzer.analyze(clean_lc, tic)
                
                if bls_result:
                    # Use stored values from DB if possible to ensure consistency?
                    # Or just use the new analysis. 
                    # Let's use the new analysis for the plot, it should be similar.
                    # Ideally we would force the period/t0 from DB onto the plot, 
                    # but Visualizer takes a Result object.
                    # Let's just save what we find now.
                    visualizer.save_plots(clean_lc, bls_periodogram, bls_result)
                    count += 1
                    print(f"Generated: {tic}")
                    
            except Exception as e:
                logger.error(f"Error generating report for {tic}: {e}")
        
        msg = T.get('report_generation_complete')
        print(msg)
        interface.send_update('log', msg)
        messagebox.showinfo(T.get('success'), f"{msg} ({count}/{len(missing_tics)})", parent=parent)
    else:
        print(T.get('report_generation_skipped'))

def main():
    print("="*60)
    print("   KSAS v4.2 - Kaesar Star Analysis System")
    print("   PERFORMANCE OPTIMIZED - MULTI-THREADED")
    print("="*60)
    
    # Detect GUI availability
    use_gui = can_use_gui()
    
    # Determine number of workers (4-8 is optimal)
    num_workers = 6  # Good balance between speed and resource usage
    
    if use_gui:
        print()
        print("Features:")
        print(f"  - {num_workers} parallel workers for maximum throughput")
        print("  - Smart targeting (prioritizes TICs with TESS data)")
        print("  - Real-time GUI visualization")
        print("  - BLS + TLS dual analysis")
        print("  - Advanced anti-binary filtering")
        print()
        print(f"Expected throughput: ~800-2000 TICs/hour")
        print("Starting GUI...")
        print("="*60)
        
        from ksas.gui_app import KSASGui
        from ksas.candidate_db import CandidateDatabase
        
        interface = KSASGui()
        
        # Initialize candidate database and link to GUI
        candidate_db = CandidateDatabase()
        
        # Check for migration (CRITICAL: Do this before linking to GUI or starting threads)
        if not candidate_db.check_and_migrate():
            print("Migration cancelled or failed. Exiting.")
            sys.exit(0)
            
        interface.candidate_db = candidate_db
        
        # Check for missing reports (Optional)
        check_missing_reports(candidate_db, interface)
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(
            target=parallel_analysis_loop, 
            args=(interface, True, num_workers), 
            daemon=True
        )
        analysis_thread.start()
        
        # Run GUI (blocking)
        # Check for updates in background
        try:
            from ksas.updater import AutoUpdater
            from ksas.config import GITHUB_REPO, CURRENT_VERSION
            updater = AutoUpdater(CURRENT_VERSION, GITHUB_REPO)
            # Wait a bit for GUI to load then check
            interface.root.after(2000, lambda: updater.check_async(interface.root))
        except Exception as e:
            logger.error(f"Failed to start updater: {e}")

        interface.run()
        
    else:
        print()
        print("Running in HEADLESS mode (no GUI available)")
        print(f"Workers: {num_workers} parallel threads")
        print("Smart targeting enabled")
        print(f"Expected throughput: ~800-2000 TICs/hour")
        print()
        print("Starting analysis...")
        print("="*60)
        
        from ksas.headless_interface import HeadlessInterface
        interface = HeadlessInterface()
        
        # Run analysis in main thread for headless
        try:
            parallel_analysis_loop(interface, False, num_workers)
        except KeyboardInterrupt:
            print("\n\nStopped by user (Ctrl+C)")

if __name__ == "__main__":
    main()
