"""
Re-scan all candidates in candidates.json and update their metrics.
This script re-analyzes each TIC to get accurate BLS power and TLS SDE values.
"""

import json
import os
import sys
import logging
from ksas.downloader import DataDownloader
from ksas.processor import DataProcessor
from ksas.analyzer import Analyzer
from ksas.tls_analyzer import TLSAnalyzer
from ksas.vetting import CandidateVetting
from ksas.candidate_db import CandidateDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def rescan_candidate(tic_id, downloader, processor, bls_analyzer, tls_analyzer, vetting):
    """Re-analyze a single candidate to get updated metrics."""
    try:
        logger.info(f"Re-scanning {tic_id}...")
        
        # 1. Download
        lc = downloader.download_lightcurve(tic_id)
        if lc is None:
            logger.warning(f"No data found for {tic_id}")
            return None
        
        # 2. Process
        clean_lc = processor.process_lightcurve(lc)
        if clean_lc is None:
            logger.warning(f"Processing failed for {tic_id}")
            return None
        
        # 3. BLS Analysis
        bls_result, bls_periodogram = bls_analyzer.analyze(clean_lc, tic_id)
        if bls_result is None:
            logger.warning(f"BLS analysis failed for {tic_id}")
            return None
        
        # 4. TLS Analysis (if BLS found something)
        tls_result = None
        if bls_result.is_candidate:
            tls_result, tls_obj = tls_analyzer.analyze(clean_lc, tic_id)
        
        # 5. Vetting
        period = tls_result.period if tls_result else bls_result.period
        t0 = tls_result.t0 if tls_result else bls_result.t0
        duration = tls_result.duration if tls_result else bls_result.duration
        
        vet_result = vetting.vet_candidate(clean_lc, period, t0, duration)
        
        # Return updated metrics
        return {
            'period': period,
            'depth': tls_result.depth if tls_result else bls_result.depth,
            'bls_power': bls_result.power,
            'tls_sde': tls_result.sde if tls_result else None,
            'vet_passed': vet_result.passed,
            'vet_metrics': vet_result.metrics
        }
        
    except Exception as e:
        logger.error(f"Error re-scanning {tic_id}: {e}")
        return None

def main():
    print("="*60)
    print("   KSAS - Candidate Re-Scanner")
    print("="*60)
    print()
    print("This will re-analyze all candidates and update their metrics")
    print("with accurate BLS power and TLS SDE values.")
    print()
    
    # Load candidates
    candidate_db = CandidateDatabase()
    candidates = candidate_db.get_all_candidates()
    
    if not candidates:
        print("No candidates found in candidates.json")
        return
    
    print(f"Found {len(candidates)} candidates to re-scan")
    print()
    
    # Ask for confirmation
    response = input("Proceed with re-scan? (y/n): ")
    if response.lower() != 'y':
        print("Canceled.")
        return
    
    # Initialize components
    print("\nInitializing analysis components...")
    downloader = DataDownloader()
    processor = DataProcessor()
    bls_analyzer = Analyzer()
    tls_analyzer = TLSAnalyzer()
    vetting = CandidateVetting()
    
    # Re-scan each candidate
    print("\nStarting re-scan...\n")
    
    updated = 0
    failed = 0
    
    for i, (tic_id, data) in enumerate(candidates.items(), 1):
        print(f"[{i}/{len(candidates)}] {tic_id}...")
        
        new_metrics = rescan_candidate(
            tic_id, downloader, processor, 
            bls_analyzer, tls_analyzer, vetting
        )
        
        if new_metrics:
            # Update candidate
            candidate_db.add_candidate(
                tic_id=tic_id,
                period=new_metrics['period'],
                depth=new_metrics['depth'],
                bls_power=new_metrics['bls_power'],
                tls_sde=new_metrics['tls_sde'],
                vetting_passed=new_metrics['vet_passed'],  # Save vetting status
                detection_time=data.get('detection_time')  # Preserve original detection time
            )
            
            # Log changes
            old_snr = data.get('snr', 0)
            new_snr = max(new_metrics['bls_power'], new_metrics['tls_sde'] or 0)
            
            print(f"  ✓ Updated: SNR {old_snr:.2f} → {new_snr:.2f} "
                  f"(BLS: {new_metrics['bls_power']:.2f}, TLS: {new_metrics['tls_sde'] or 0:.2f})")
            print(f"  Vetting: {'PASSED' if new_metrics['vet_passed'] else 'FAILED'}")
            
            updated += 1
        else:
            print(f"  ✗ Failed to re-scan")
            failed += 1
    
    print()
    print("="*60)
    print("Re-scan complete!")
    print(f"  Updated: {updated}")
    print(f"  Failed: {failed}")
    print("="*60)
    print()
    print("candidates.json has been updated with correct metrics.")
    print("Run 'Scan Candidates' in GUI to see updated scores.")

if __name__ == "__main__":
    main()
