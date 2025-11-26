import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles processing and cleaning of LightCurve data.
    """
    
    def __init__(self):
        pass
        
    def process_lightcurve(self, lc):
        """
        Cleans and flattens the light curve.
        
        Args:
            lc (lightkurve.LightCurve): The raw light curve.
            
        Returns:
            lightkurve.LightCurve: The processed light curve ready for analysis.
        """
        if lc is None:
            return None
            
        try:
            logger.info("Processing light curve...")
            
            # 1. Remove NaNs
            lc = lc.remove_nans()
            
            # 2. Normalize (if not already)
            lc = lc.normalize()
            
            # 3. Remove outliers (sigma clipping)
            # We want to keep the transits (dips), so we are careful with sigma_lower
            # But we definitely want to remove high outliers (flares)
            lc = lc.remove_outliers(sigma_upper=3, sigma_lower=float('inf'))
            
            # 4. Flatten
            # Removing low-frequency trends (stellar rotation, instrument drift)
            # window_length needs to be larger than the transit duration
            # A typical transit is a few hours. 
            # TESS 2-min cadence. 1 day = 720 points.
            # window_length=1001 is roughly 1.4 days, good for preserving transits < 1 day
            flat_lc = lc.flatten(window_length=1001)
            
            logger.info("Light curve processed successfully.")
            return flat_lc
            
        except Exception as e:
            logger.error(f"Error processing light curve: {e}")
            return None
