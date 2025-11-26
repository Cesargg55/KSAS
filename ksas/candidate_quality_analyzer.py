import json
import os
import logging
from ksas.config import BLS_SNR_THRESHOLD

logger = logging.getLogger(__name__)

class CandidateQualityAnalyzer:
    """
    Analyzes candidates using scientific metrics (SNR, depth, vetting)
    instead of image analysis. Much more accurate and reliable.
    """
    
    def __init__(self):
        self.candidates_file = "candidates.json"
    
    def analyze_candidate(self, tic_id, candidate_data):
        """
        Analyze a single candidate using scientific metrics.
        
        Returns:
            dict with quality assessment
        """
        try:
            # Extract metrics
            snr = candidate_data.get('snr', 0)
            period = candidate_data.get('period', 0)
            depth = candidate_data.get('depth', 1.0)
            vetting_passed = candidate_data.get('vetting_passed', True)  # Default True for old entries
            
            # Calculate depth percentage
            depth_percent = abs(1.0 - depth) * 100
            
            # Score components
            snr_score = self._score_snr(snr)
            period_score = self._score_period(period)
            depth_score = self._score_depth(depth_percent)
            
            # Overall score (0-100) BEFORE vetting penalty
            base_score = int(
                snr_score * 60 +        # SNR is most important
                depth_score * 25 +      # Clear depth second
                period_score * 15       # Reasonable period
            )
            
            # CRITICAL: Heavy penalty for vetting failures
            if not vetting_passed:
                # If failed vetting, cap score at 60 maximum
                # This ensures failed candidates are NEVER "EXCELLENT"
                overall_score = min(base_score, 60)
                # Further reduce based on how high the base score was
                # High SNR but failed vetting = very suspicious
                if base_score > 80:
                    overall_score = min(overall_score, 50)  # Cap at FAIR
            else:
                overall_score = base_score
            
            # Quality classification
            quality = self._get_quality_label(overall_score)
            
            # Recommendation
            recommendation = self._get_recommendation(overall_score, snr, depth_percent, period, vetting_passed)
            
            # Additional flags
            has_strong_signal = snr > 15
            is_physical = 0.3 < period < 50  # Days
            has_measurable_depth = depth_percent > 0.01
            
            return {
                'tic_id': tic_id,
                'score': overall_score,
                'quality': quality,
                'snr': snr,
                'period': period,
                'depth_percent': depth_percent,
                'vetting_passed': vetting_passed,
                'has_strong_signal': has_strong_signal,
                'is_physical_period': is_physical,
                'has_measurable_depth': has_measurable_depth,
                'recommendation': recommendation,
                'snr_score': snr_score,
                'period_score': period_score,
                'depth_score': depth_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {tic_id}: {e}")
            return {'error': str(e), 'tic_id': tic_id}
    
    def _score_snr(self, snr):
        """
        Score SNR/SDE value (0-1).
        
        Scale:
        - 0-10: Poor (0-0.3)
        - 10-20: Good (0.3-0.7)
        - 20-50: Excellent (0.7-0.95)
        - 50+: Outstanding (0.95-1.0)
        """

        # Use config threshold as baseline for "Good"
        threshold = BLS_SNR_THRESHOLD
        
        if snr < threshold / 2:
            return 0.0
        elif snr < threshold:
            return 0.1 + (snr - (threshold/2)) / (threshold/2) * 0.2
        elif snr < threshold * 2:
            return 0.3 + (snr - threshold) / threshold * 0.4
        elif snr < threshold * 5:
            return 0.7 + (snr - (threshold*2)) / (threshold*3) * 0.25
        else:
            return min(1.0, 0.95 + (snr - (threshold*5)) / 100 * 0.05)
    
    def _score_period(self, period):
        """
        Score orbital period (0-1).
        Prefers physically reasonable periods.
        """
        if period <= 0:
            return 0.0
        
        # Very short periods (< 0.3 days = 7.2 hours): suspicious
        if period < 0.3:
            return 0.3
        
        # Good range: 0.3 - 50 days
        if 0.3 <= period <= 50:
            # Optimal around 1-10 days
            if 0.5 <= period <= 20:
                return 1.0
            else:
                return 0.8
        
        # Very long periods (> 50 days): possible but harder to detect
        if period > 50:
            return max(0.3, 1.0 - (period - 50) / 100)
        
        return 0.5
    
    def _score_depth(self, depth_percent):
        """
        Score transit depth (0-1).
        Deeper = more detectable, but too deep = likely binary.
        """
        if depth_percent <= 0:
            return 0.0
        
        # Too shallow (< 0.01%): hard to detect
        if depth_percent < 0.01:
            return 0.2
        
        # Good range: 0.01% - 5%
        if 0.01 <= depth_percent <= 5:
            # Optimal around 0.05% - 1%
            if 0.05 <= depth_percent <= 1.0:
                return 1.0
            else:
                return 0.8
        
        # Too deep (> 5%): likely eclipsing binary
        if depth_percent > 5:
            return max(0.2, 1.0 - (depth_percent - 5) / 10)
        
        return 0.5
    
    def _get_quality_label(self, score):
        """Get quality label from score."""
        if score >= 75:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "FAIR"
        elif score >= 20:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def _get_recommendation(self, score, snr, depth, period, vetting_passed=True):
        """Get recommendation text."""
        if not vetting_passed:
            return "⚠️ FAILED VETTING - High SNR but suspicious signal (likely false positive)"
        
        if score >= 75 and snr > 20:
            return "⭐⭐⭐ HIGHLY PROMISING - Strong signal, verify with TIC Verifier"
        elif score >= 65 and snr > 15:
            return "⭐⭐ VERY GOOD - Solid candidate, worth investigating"
        elif score >= 55 and snr > 12:
            return "⭐⭐ GOOD - Promising signal, check report manually"
        elif score >= 40:
            return "⭐ FAIR - Weak signal, likely false positive"
        else:
            return "❌ NOT RECOMMENDED - Very weak or inconsistent signal"
    
    def scan_all_candidates(self):
        """
        Scan all candidates from candidates.json.
        
        Returns:
            List of analysis results, sorted by score
        """
        results = []
        
        if not os.path.exists(self.candidates_file):
            logger.warning(f"{self.candidates_file} not found")
            return results
        
        try:
            with open(self.candidates_file, 'r') as f:
                candidates = json.load(f)
            
            for tic_id, data in candidates.items():
                analysis = self.analyze_candidate(tic_id, data)
                
                # Add filename info
                safe_id = tic_id.replace(" ", "_")
                analysis['filename'] = f"{safe_id}_report.png"
                analysis['has_report'] = os.path.exists(f"output/{safe_id}_report.png")
                
                results.append(analysis)
            
            # Sort by score (best first)
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"Analyzed {len(results)} candidates")
            
        except Exception as e:
            logger.error(f"Error scanning candidates: {e}")
        
        return results
    
    def get_summary_stats(self, results):
        """Get summary statistics."""
        if not results:
            return {}
        
        excellent = sum(1 for r in results if r.get('quality') == 'EXCELLENT')
        good = sum(1 for r in results if r.get('quality') == 'GOOD')
        fair = sum(1 for r in results if r.get('quality') == 'FAIR')
        poor = sum(1 for r in results if r.get('quality') in ['POOR', 'VERY_POOR'])
        
        avg_snr = sum(r.get('snr', 0) for r in results) / len(results)
        max_snr = max(r.get('snr', 0) for r in results)
        
        return {
            'total': len(results),
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor,
            'avg_snr': avg_snr,
            'max_snr': max_snr
        }
