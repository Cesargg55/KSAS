import numpy as np
import logging
from scipy import stats
from ksas.config import (
    VETTING_ODD_EVEN_TOLERANCE,
    VETTING_SHAPE_THRESHOLD,
    VETTING_SECONDARY_THRESHOLD,
    VETTING_MAX_DEPTH_DURATION_RATIO
)

logger = logging.getLogger(__name__)

class VettingResult:
    """Results from candidate vetting."""
    def __init__(self, passed, reasons, metrics):
        self.passed = passed  # Boolean: True if passed all tests
        self.reasons = reasons  # List of failure reasons
        self.metrics = metrics  # Dict of computed metrics
    
    def __str__(self):
        if self.passed:
            return "✓ PASSED all vetting tests"
        else:
            return f"✗ FAILED: {', '.join(self.reasons)}"

class CandidateVetting:
    """
    Advanced vetting to distinguish planets from false positives (especially eclipsing binaries).
    """
    
    def __init__(self):
        pass
    
    def vet_candidate(self, lc, period, t0, duration):
        """
        Runs all vetting tests on a candidate.
        
        Args:
            lc: LightCurve object
            period: Detected period (days)
            t0: Transit epoch
            duration: Transit duration (days)
            
        Returns:
            VettingResult
        """
        reasons = []
        metrics = {}
        
        logger.info("Running vetting tests...")
        
        # 1. Odd/Even Test
        odd_even_pass, odd_even_metric = self.odd_even_test(lc, period, t0, duration)
        metrics['odd_even_diff'] = odd_even_metric
        if not odd_even_pass:
            reasons.append(f"Odd/Even mismatch ({odd_even_metric:.3f})")
        
        # 2. Shape Test (V vs U)
        shape_pass, shape_metric = self.shape_test(lc, period, t0, duration)
        metrics['shape_metric'] = shape_metric
        if not shape_pass:
            reasons.append(f"V-shaped transit (binary-like, metric={shape_metric:.3f})")
        
        # 3. Secondary Transit Test
        secondary_pass, secondary_metric = self.secondary_transit_test(lc, period, t0)
        metrics['secondary_depth'] = secondary_metric
        if not secondary_pass:
            reasons.append(f"Secondary transit detected ({secondary_metric:.4f})")
        
        # 4. Depth/Duration Ratio
        ratio_pass, ratio_metric = self.depth_duration_ratio_test(lc, period, t0, duration)
        metrics['depth_duration_ratio'] = ratio_metric
        if not ratio_pass:
            reasons.append(f"Unusual depth/duration ratio ({ratio_metric:.3f})")
        
        passed = len(reasons) == 0
        
        return VettingResult(passed, reasons, metrics)
    
    def odd_even_test(self, lc, period, t0, duration):
        """
        Compares odd-numbered transits vs even-numbered transits.
        If they're significantly different, it's likely an eclipsing binary.
        
        Returns:
            (pass: bool, metric: float)
        """
        try:
            # Fold the light curve
            folded = lc.fold(period=period, epoch_time=t0)
            
            # Identify transit region
            in_transit = np.abs(folded.time.value) < 0.5 * duration
            
            # Get original time indices for odd/even separation
            # We need to track which orbit number each point belongs to
            time_from_t0 = lc.time.value - t0
            orbit_number = np.round(time_from_t0 / period).astype(int)
            
            # Separate odd and even
            odd_mask = (orbit_number % 2 == 1) & in_transit
            even_mask = (orbit_number % 2 == 0) & in_transit
            
            if np.sum(odd_mask) < 5 or np.sum(even_mask) < 5:
                # Not enough data
                return True, 0.0
            
            odd_depths = 1 - lc.flux.value[odd_mask]
            even_depths = 1 - lc.flux.value[even_mask]
            
            odd_mean = np.median(odd_depths)
            even_mean = np.median(even_depths)
            
            # Difference metric
            diff = np.abs(odd_mean - even_mean)
            
            # STRICTER: if difference > tolerance of deeper depth, fail
            threshold = VETTING_ODD_EVEN_TOLERANCE * max(np.abs(odd_mean), np.abs(even_mean))
            
            passed = diff < threshold
            
            logger.info(f"Odd/Even Test: diff={diff:.4f}, threshold={threshold:.4f}, passed={passed}")
            
            return passed, diff
            
        except Exception as e:
            logger.warning(f"Odd/Even test failed: {e}")
            return True, 0.0  # If test fails, don't penalize
    
    def shape_test(self, lc, period, t0, duration):
        """
        Checks if transit is V-shaped (binary) or U-shaped (planet).
        
        V-shaped: sharp ingress/egress, flat bottom
        U-shaped: smooth, rounded bottom
        
        Returns:
            (pass: bool, metric: float)
        """
        try:
            folded = lc.fold(period=period, epoch_time=t0)
            
            # Focus on transit region
            in_transit = np.abs(folded.time.value) < 0.6 * duration
            
            if np.sum(in_transit) < 10:
                return True, 0.0
            
            transit_flux = folded.flux.value[in_transit]
            transit_time = folded.time.value[in_transit]
            
            # Sort by time
            sort_idx = np.argsort(transit_time)
            transit_flux = transit_flux[sort_idx]
            transit_time = transit_time[sort_idx]
            
            # Find minimum
            min_idx = np.argmin(transit_flux)
            
            # Check if bottom is flat vs pointed
            # For U-shape, points near bottom should be similar
            # For V-shape, there's a sharp minimum
            
            # Take central 20% of transit
            n = len(transit_flux)
            central_start = int(0.4 * n)
            central_end = int(0.6 * n)
            
            if central_end - central_start < 3:
                return True, 0.0
            
            central_flux = transit_flux[central_start:central_end]
            central_std = np.std(central_flux)
            
            # Also check curvature by fitting quadratic to bottom
            # V-shape would have high curvature (positive second derivative)
            # U-shape would have low curvature
            
            # Simple metric: std of central region
            # Low std = flat bottom = U-shape (planet)
            # High std = V-shape (binary)
            
            # Normalize by depth
            depth = 1 - np.min(transit_flux)
            if depth < 0.001:
                return True, 0.0
            
            normalized_std = central_std / depth
            
            # STRICTER: if normalized std > threshold, it's V-shaped
            passed = normalized_std < VETTING_SHAPE_THRESHOLD
            
            logger.info(f"Shape Test: normalized_std={normalized_std:.4f}, threshold={VETTING_SHAPE_THRESHOLD:.4f}, passed={passed}")
            
            return passed, normalized_std
            
        except Exception as e:
            logger.warning(f"Shape test failed: {e}")
            return True, 0.0
    
    def secondary_transit_test(self, lc, period, t0):
        """
        Searches for secondary eclipse at phase 0.5.
        Planets don't have secondary eclipses (or very shallow ones).
        Binaries have deep secondary eclipses.
        
        Returns:
            (pass: bool, secondary_depth: float)
        """
        try:
            # Fold at phase 0.5 (secondary eclipse position)
            secondary_t0 = t0 + period * 0.5
            folded_secondary = lc.fold(period=period, epoch_time=secondary_t0)
            
            # Look at central region
            central_mask = np.abs(folded_secondary.time.value) < 0.1
            
            if np.sum(central_mask) < 5:
                return True, 0.0
            
            central_flux = folded_secondary.flux.value[central_mask]
            secondary_depth = 1 - np.median(central_flux)
            
            # Get baseline flux (out of transit)
            out_mask = np.abs(folded_secondary.time.value) > 0.2
            if np.sum(out_mask) > 0:
                baseline = np.median(folded_secondary.flux.value[out_mask])
                secondary_depth = baseline - np.median(central_flux)
            
            # Threshold: if secondary depth > threshold, it's suspicious
            passed = secondary_depth < VETTING_SECONDARY_THRESHOLD
            
            logger.info(f"Secondary Transit Test: depth={secondary_depth:.4f}, threshold={VETTING_SECONDARY_THRESHOLD:.4f}, passed={passed}")
            
            return passed, secondary_depth
            
        except Exception as e:
            logger.warning(f"Secondary transit test failed: {e}")
            return True, 0.0
    
    def depth_duration_ratio_test(self, lc, period, t0, duration):
        """
        Checks if depth/duration ratio is physically plausible.
        
        Very deep + very short = likely grazing binary
        Very shallow + very long = unlikely
        
        Returns:
            (pass: bool, ratio: float)
        """
        try:
            folded = lc.fold(period=period, epoch_time=t0)
            in_transit = np.abs(folded.time.value) < 0.5 * duration
            
            if np.sum(in_transit) < 3:
                return True, 0.0
            
            depth = 1 - np.min(folded.flux.value[in_transit])
            
            # Ratio: depth/duration
            # For planets, typical range is ~0.001 to ~0.1
            ratio = depth / duration
            
            # Very loose bounds
            min_ratio = 0.0001
            max_ratio = VETTING_MAX_DEPTH_DURATION_RATIO
            
            passed = min_ratio < ratio < max_ratio
            
            logger.info(f"Depth/Duration Ratio Test: ratio={ratio:.4f}, passed={passed}")
            
            return passed, ratio
            
        except Exception as e:
            logger.warning(f"Depth/Duration ratio test failed: {e}")
            return True, 0.0
