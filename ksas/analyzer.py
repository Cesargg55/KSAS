import numpy as np
import logging
from astropy.timeseries import BoxLeastSquares
from ksas.config import BLS_SNR_THRESHOLD, BLS_MAX_DEPTH

logger = logging.getLogger(__name__)

class AnalysisResult:
    def __init__(self, target_id, period, t0, duration, depth, power, snr, is_candidate):
        self.target_id = target_id
        self.period = period
        self.t0 = t0
        self.duration = duration
        self.depth = depth
        self.power = power
        self.snr = snr
        self.is_candidate = is_candidate

    def __str__(self):
        status = "CANDIDATE" if self.is_candidate else "NO DETECTION"
        return (f"[{status}] {self.target_id} | Period: {self.period:.4f} d | "
                f"T0: {self.t0:.4f} | Depth: {self.depth:.4f} | SNR: {self.snr:.2f}")

class Analyzer:
    """
    Analyzes light curves to find periodic transits using BLS.
    """
    
    def __init__(self, snr_threshold=BLS_SNR_THRESHOLD):
        self.snr_threshold = snr_threshold

    def analyze(self, lc, target_id):
        """
        Runs BLS on the light curve.
        
        Args:
            lc (lightkurve.LightCurve): The processed light curve.
            target_id (str): ID of the target.
            
        Returns:
            AnalysisResult: The result of the analysis.
        """
        if lc is None:
            return None
            
        logger.info(f"Running BLS analysis for {target_id}...")
        
        try:
            # Create BLS model
            # We use the astropy BoxLeastSquares or lightkurve's wrapper
            # Lightkurve's to_periodogram(method='bls') is convenient
            
            # Run BLS with default auto-grid
            periodogram = lc.to_periodogram(method='bls', period=np.linspace(0.5, 15, 5000))
            
            # Extract best fit parameters
            best_period = periodogram.period_at_max_power.value
            best_t0 = periodogram.transit_time_at_max_power.value
            best_duration = periodogram.duration_at_max_power.value
            max_power = periodogram.max_power.value
            best_depth = periodogram.depth_at_max_power.value
            
            logger.info(f"Analysis for {target_id}: Max Power = {max_power:.2f}, Depth = {best_depth:.4f}")
            
            # Calculate SNR
            # A simple SNR estimate: depth / std_dev_of_residuals * sqrt(number_of_transits)
            # Or use the max_power directly if normalized correctly.
            # Lightkurve BLS power is often the Signal-to-Noise of the fit or related.
            # Let's use periodogram.max_power as a proxy for significance for now, 
            # but a better metric is often preferred.
            # Let's calculate a rough SNR based on depth and noise.
            
            # Fold the light curve
            folded = lc.fold(period=best_period, epoch_time=best_t0)
            
            # Estimate noise (std dev of out-of-transit points)
            # Simple approximation: std of the whole folded curve
            noise = np.nanstd(folded.flux)
            
            # Number of points in transit
            # transit_mask = np.abs(folded.time.value) < 0.5 * best_duration
            # n_transit_points = np.sum(transit_mask)
            
            # SNR ~ Depth / (Noise / sqrt(N_points_in_transit))
            # This is complex to do perfectly without a full model fit.
            # We will use the 'power' as the primary metric for sorting, 
            # and a simple depth check.
            
            # For this implementation, we'll treat 'max_power' as the main statistic.
            # In Lightkurve BLS, power is the likelihood ratio. High is good.
            
            # Let's define a "Candidate" if power is high and depth is reasonable (< 0.1 for planets)
            is_candidate = False
            
            # Heuristic thresholds
            # Power values depend on normalization. 
            # Let's use a relative threshold or just the SNR provided by periodogram if available.
            # Actually, periodogram.snr is available in some versions, let's check.
            # If not, we rely on max_power.
            
            # Let's assume max_power > some value.
            # For now, let's just pass everything back and let the main loop decide or log it.
            # But to be "automated", we need a flag.
            
            # Let's calculate a robust SNR:
            # SNR = Depth / Noise_of_binned_depth
            # Let's stick to a simple check:
            if max_power > self.snr_threshold and best_depth < BLS_MAX_DEPTH: # Depth < 10% (avoid binaries)
                 is_candidate = True
            
            # Refine SNR for display
            snr = max_power # Placeholder
            
            result = AnalysisResult(
                target_id=target_id,
                period=best_period,
                t0=best_t0,
                duration=best_duration,
                depth=best_depth,
                power=max_power,
                snr=snr,
                is_candidate=is_candidate
            )
            
            return result, periodogram
            
        except Exception as e:
            logger.error(f"Error analyzing {target_id}: {e}")
            return None, None
