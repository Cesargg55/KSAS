import numpy as np
import logging
from transitleastsquares import transitleastsquares

from ksas.config import TLS_SDE_THRESHOLD

logger = logging.getLogger(__name__)

class TLSResult:
    """Result from TLS analysis."""
    def __init__(self, period, t0, duration, depth, power, snr, sde):
        self.period = period
        self.t0 = t0
        self.duration = duration
        self.depth = depth
        self.power = power
        self.snr = snr
        self.sde = sde  # Signal Detection Efficiency
    
    def __str__(self):
        return f"TLS: Period={self.period:.4f}d, Depth={self.depth:.4f}, SDE={self.sde:.2f}"

class TLSAnalyzer:
    """
    Transit Least Squares analyzer.
    More sophisticated than BLS, specifically designed for exoplanet detection.
    """
    
    def __init__(self, sde_threshold=TLS_SDE_THRESHOLD):
        """
        Args:
            sde_threshold: Signal Detection Efficiency threshold (>7 is significant)
        """
        self.sde_threshold = sde_threshold
    
    def analyze(self, lc, target_id):
        """
        Run TLS on light curve.
        
        Args:
            lc: LightCurve object
            target_id: Target ID
            
        Returns:
            (TLSResult, tls_results_object) or (None, None)
        """
        try:
            logger.info(f"Running TLS analysis for {target_id}...")
            
            # Prepare data
            time = lc.time.value
            flux = lc.flux.value
            
            # Remove NaNs
            mask = np.isfinite(time) & np.isfinite(flux)
            time = time[mask]
            flux = flux[mask]
            
            if len(time) < 100:
                logger.warning("Not enough data points for TLS")
                return None, None
            
            # Initialize TLS
            model = transitleastsquares(time, flux)
            
            # Run search
            # TLS automatically determines good period/duration ranges
            results = model.power()
            
            # Extract results
            period = results.period
            t0 = results.T0
            duration = results.duration
            depth = results.depth
            power = results.power.max()
            snr = results.snr
            sde = results.SDE
            
            logger.info(f"TLS for {target_id}: Period={period:.4f}d, SDE={sde:.2f}")
            
            tls_result = TLSResult(
                period=period,
                t0=t0,
                duration=duration,
                depth=depth,
                power=power,
                snr=snr,
                sde=sde
            )
            
            return tls_result, results
            
        except Exception as e:
            logger.error(f"TLS analysis failed for {target_id}: {e}")
            return None, None
    
    def is_significant(self, tls_result):
        """Check if TLS result is significant."""
        if tls_result is None:
            return False
        return tls_result.sde > self.sde_threshold
