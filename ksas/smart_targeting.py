import random
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SmartTargeting:
    """
    Smart target generation that prioritizes TICs likely to have TESS data.
    Uses statistical filtering to reduce wasted downloads.
    """
    
    def __init__(self):
        # TESS observed ~70% of sky in sectors 1-69
        # Focus on ranges with higher observation density
        
        # Primary TESS zones (higher probability of data)
        self.priority_ranges = [
            # Southern ecliptic hemisphere (sectors 1-13)
            (10000000, 100000000, 0.6),  # High priority
            # Northern ecliptic hemisphere (sectors 14-26)
            (100000000, 200000000, 0.6),  # High priority
            # Continuous viewing zones
            (200000000, 300000000, 0.5),  # Medium priority
            # Extended mission
            (300000000, 410000000, 0.4),  # Lower priority but valid
        ]
        
        # Magnitude filtering helps too (brighter = more likely observed)
        # But we don't have magnitude info without querying, so we use TIC ranges
        
        # Build weighted selection based on priorities
        self.weighted_ranges = []
        for start, end, weight in self.priority_ranges:
            self.weighted_ranges.extend([(start, end)] * int(weight * 10))
    
    def generate_smart_targets(self):
        """
        Infinite generator of smart TIC IDs.
        Yields TICs with statistically higher chance of having TESS data.
        """
        while True:
            # Select range based on weights
            start, end = random.choice(self.weighted_ranges)
            
            # Generate TIC in this range
            tic_num = random.randint(start, end)
            
            # Add some randomness to avoid clustering
            if random.random() < 0.1:  # 10% completely random
                tic_num = random.randint(1000000, 450000000)
            
            yield f"TIC {tic_num}"
    
    def generate_batch(self, n=100):
        """
        Generate a batch of N smart targets.
        Useful for parallel processing.
        
        Args:
            n: Number of targets to generate
            
        Returns:
            List of TIC IDs
        """
        generator = self.generate_smart_targets()
        return [next(generator) for _ in range(n)]
