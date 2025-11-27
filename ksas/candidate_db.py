import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CandidateDatabase:
    """
    Tracks detected candidates with review status and discovery status.
    """
    
    def __init__(self, db_file="candidates.json"):
        self.db_file = db_file
        self.candidates = {}
        self.load()
    
    def load(self):
        """Load candidates from file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    self.candidates = json.load(f)
                logger.info(f"Loaded {len(self.candidates)} candidates from database.")
            except Exception as e:
                logger.warning(f"Could not load candidates database: {e}")
                self.candidates = {}
        else:
            logger.info("No previous candidates database found. Starting fresh.")
            self.candidates = {}
    
    def save(self):
        """Save candidates to file."""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.candidates, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save candidates database: {e}")
    
    def add_candidate(self, tic_id, period, depth, bls_power=None, tls_sde=None, vetting_passed=True, detection_time=None, t0=None, duration=None):
        """
        Add a new candidate or update existing.
        
        Args:
            tic_id: TIC ID (e.g., "TIC 34080274")
            period: Orbital period in days
            depth: Transit depth
            bls_power: BLS power/SNR
            tls_sde: TLS SDE (if TLS was run)
            vetting_passed: Whether candidate passed vetting tests
            detection_time: ISO timestamp (default: now)
            t0: Transit Epoch (BTJD)
            duration: Transit Duration (days)
        """
        if detection_time is None:
            detection_time = datetime.now().isoformat()
        
        # Calculate best SNR (use maximum of BLS and TLS)
        snr = max(bls_power or 0, tls_sde or 0)
        
        if tic_id not in self.candidates:
            self.candidates[tic_id] = {
                'tic_id': tic_id,
                'period': period,
                'depth': depth,
                'snr': snr,  # Best SNR for compatibility
                'bls_power': bls_power,  # Separate BLS power
                'tls_sde': tls_sde,  # Separate TLS SDE
                'vetting_passed': vetting_passed,  # Vetting status
                'detection_time': detection_time,
                'reviewed': False,
                'is_discovered': None,  # None = unknown, True = yes, False = no
                'notes': '',
                'review_time': None,
                't0': t0,
                'duration': duration
            }
            logger.info(f"Added new candidate: {tic_id} (BLS: {bls_power}, TLS: {tls_sde}, Vet: {vetting_passed})")
        else:
            # Update detection info but preserve review status
            self.candidates[tic_id].update({
                'period': period,
                'depth': depth,
                'snr': snr,
                'bls_power': bls_power,
                'tls_sde': tls_sde,
                'vetting_passed': vetting_passed,
                'detection_time': detection_time,
                't0': t0,
                'duration': duration
            })
        
        self.save()
        
    def update_candidate(self, tic_id, updates):
        """
        Update specific fields of a candidate.
        
        Args:
            tic_id: TIC ID
            updates: Dictionary of fields to update
        """
        if tic_id in self.candidates:
            self.candidates[tic_id].update(updates)
            self.save()
            logger.info(f"Updated fields for {tic_id}: {list(updates.keys())}")
    
    def mark_reviewed(self, tic_id, is_discovered, notes=""):
        """
        Mark a candidate as reviewed.
        
        Args:
            tic_id: TIC ID
            is_discovered: True if already discovered, False if potentially new
            notes: Optional notes
        """
        if tic_id in self.candidates:
            self.candidates[tic_id]['reviewed'] = True
            self.candidates[tic_id]['is_discovered'] = is_discovered
            self.candidates[tic_id]['notes'] = notes
            self.candidates[tic_id]['review_time'] = datetime.now().isoformat()
            self.save()
            logger.info(f"Marked {tic_id} as reviewed (discovered={is_discovered})")
    
    def get_candidate(self, tic_id):
        """Get candidate info."""
        return self.candidates.get(tic_id)
    
    def get_all_candidates(self):
        """Get all candidates."""
        return self.candidates
    
    def get_unreviewed(self):
        """Get list of unreviewed candidates."""
        return {k: v for k, v in self.candidates.items() if not v['reviewed']}
    
    def get_reviewed(self):
        """Get list of reviewed candidates."""
        return {k: v for k, v in self.candidates.items() if v['reviewed']}
    
    def get_potentially_new(self):
        """Get candidates marked as potentially new (not discovered)."""
        return {k: v for k, v in self.candidates.items() 
                if v['reviewed'] and v['is_discovered'] == False}
    
    def get_stats(self):
        """Get statistics."""
        total = len(self.candidates)
        reviewed = len(self.get_reviewed())
        unreviewed = len(self.get_unreviewed())
        potentially_new = len(self.get_potentially_new())
        
        return {
            'total': total,
            'reviewed': reviewed,
            'unreviewed': unreviewed,
            'potentially_new': potentially_new
        }

    def check_and_migrate(self):
        """
        Check for old data format and migrate if necessary.
        Returns True if safe to proceed, False if user cancelled.
        """
        needs_migration = False
        for tic, data in self.candidates.items():
            if 'score' not in data or 'quality' not in data:
                needs_migration = True
                break
        
        if not needs_migration:
            return True
            
        # Ask user
        import tkinter as tk
        from tkinter import messagebox
        from ksas.locales import T
        
        # Ensure we have a root window for the dialog if none exists
        root = tk.Tk()
        root.withdraw() # Hide main window
        
        response = messagebox.askyesno(
            T.get('migration_title'),
            T.get('migration_prompt')
        )
        
        if response:
            try:
                from ksas.candidate_quality_analyzer import CandidateQualityAnalyzer
                analyzer = CandidateQualityAnalyzer()
                
                count = 0
                for tic, data in self.candidates.items():
                    # Only update if missing fields
                    if 'score' not in data or 'quality' not in data:
                        # Analyze using existing data
                        # Note: analyze_candidate expects 'snr', 'period', 'depth' which should exist
                        # If 'snr' is missing in VERY old format, we might need to calc it from bls_power
                        if 'snr' not in data:
                            data['snr'] = max(data.get('bls_power', 0), data.get('tls_sde', 0))
                            
                        result = analyzer.analyze_candidate(tic, data)
                        
                        # Update fields
                        self.candidates[tic].update({
                            'score': result['score'],
                            'quality': result['quality'],
                            'analysis_summary': result['recommendation'],
                            'snr': result['snr'], # Ensure SNR is set
                            'depth_percent': result['depth_percent']
                        })
                        count += 1
                
                self.save()
                messagebox.showinfo(T.get('success'), f"{T.get('migration_success')} ({count} updated)")
                root.destroy()
                return True
                
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                messagebox.showerror("Error", f"Migration failed: {e}")
                root.destroy()
                return False
        else:
            messagebox.showinfo(T.get('warning'), T.get('migration_cancel'))
            root.destroy()
            return False
