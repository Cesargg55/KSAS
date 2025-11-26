import cv2
import numpy as np
import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImageQualityAnalyzer:
    """
    Analyzes PNG reports automatically to detect quality of transit signals.
    Uses computer vision to detect U-shape, symmetry, and noise.
    """
    
    def __init__(self):
        pass
    
    def analyze_report(self, image_path):
        """
        Analyze a report PNG and score it.
        
        Returns:
            dict with:
                - score: 0-100 quality score
                - has_u_shape: bool
                - symmetry_score: 0-1
                - noise_level: 0-1
                - recommendation: string
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Could not read image'}
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Get the folded light curve region (bottom third of image)
            height, width = gray.shape
            folded_region = gray[int(height * 0.66):height, :]
            
            # Analyze this region
            has_u, u_score = self._detect_u_shape(folded_region)
            symmetry = self._check_symmetry(folded_region)
            noise = self._measure_noise(folded_region)
            depth_clarity = self._measure_dip_clarity(folded_region)
            
            # Calculate overall score
            score = self._calculate_score(u_score, symmetry, noise, depth_clarity)
            
            # Recommendation
            recommendation = self._get_recommendation(score, has_u, symmetry, noise)
            
            return {
                'score': score,
                'has_u_shape': has_u,
                'u_shape_score': u_score,
                'symmetry_score': symmetry,
                'noise_level': noise,
                'depth_clarity': depth_clarity,
                'recommendation': recommendation,
                'quality': self._get_quality_label(score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {image_path}: {e}")
            return {'error': str(e)}
    
    def _detect_u_shape(self, region):
        """
        Detect if there's a clear U-shape in the center.
        Returns (has_u: bool, score: 0-1)
        """
        # Get center column profile (vertical slice at center)
        center_x = region.shape[1] // 2
        margin = region.shape[1] // 10
        
        # Get vertical profile in center region
        center_profile = np.mean(region[:, center_x-margin:center_x+margin], axis=1)
        
        # Normalize
        if center_profile.max() > center_profile.min():
            center_profile = (center_profile - center_profile.min()) / (center_profile.max() - center_profile.min())
        
        # Look for a dip (U-shape has lower values in middle)
        middle = len(center_profile) // 2
        margin_vert = len(center_profile) // 4
        
        # Check if center is darker (lower) than sides
        center_val = np.mean(center_profile[middle-margin_vert:middle+margin_vert])
        side_val = (np.mean(center_profile[:margin_vert]) + np.mean(center_profile[-margin_vert:])) / 2
        
        dip_strength = side_val - center_val
        
        # U-shape detected if there's a clear dip
        has_u = dip_strength > 0.1
        score = min(1.0, max(0.0, dip_strength * 5))  # Scale to 0-1
        
        return has_u, score
    
    def _check_symmetry(self, region):
        """
        Check left-right symmetry.
        Returns: 0-1 where 1 = perfect symmetry
        """
        # Split in half
        mid = region.shape[1] // 2
        left = region[:, :mid]
        right = np.fliplr(region[:, mid:])
        
        # Make same size
        min_width = min(left.shape[1], right.shape[1])
        left = left[:, :min_width]
        right = right[:, :min_width]
        
        # Calculate difference
        diff = np.abs(left.astype(float) - right.astype(float))
        symmetry = 1.0 - (np.mean(diff) / 255.0)
        
        return max(0.0, min(1.0, symmetry))
    
    def _measure_noise(self, region):
        """
        Measure scatter/noise in the data.
        Returns: 0-1 where 0 = no noise, 1 = very noisy
        """
        # Use standard deviation as noise metric
        # High std = lots of scatter = noisy
        std = np.std(region)
        
        # Normalize (typical std range 0-50 for these images)
        noise = min(1.0, std / 50.0)
        
        return noise
    
    def _measure_dip_clarity(self, region):
        """
        Measure how clear the transit dip is.
        Returns: 0-1 where 1 = very clear dip
        """
        # Get horizontal profile (average across vertical)
        h_profile = np.mean(region, axis=0)
        
        # Normalize
        if h_profile.max() > h_profile.min():
            h_profile = (h_profile - h_profile.min()) / (h_profile.max() - h_profile.min())
        
        # Find minimum (should be at center for good transit)
        min_idx = np.argmin(h_profile)
        center_idx = len(h_profile) // 2
        
        # Check if minimum is near center
        offset = abs(min_idx - center_idx) / len(h_profile)
        
        # Depth of dip
        min_val = h_profile[min_idx]
        avg_sides = (np.mean(h_profile[:len(h_profile)//4]) + np.mean(h_profile[-len(h_profile)//4:])) / 2
        depth = avg_sides - min_val
        
        # Good dip = centered + deep
        clarity = depth * (1.0 - offset)
        
        return max(0.0, min(1.0, clarity))
    
    def _calculate_score(self, u_score, symmetry, noise, clarity):
        """
        Calculate overall quality score 0-100.
        """
        # Weighted combination
        score = (
            u_score * 40 +           # U-shape most important
            clarity * 30 +           # Clear dip second
            symmetry * 20 +          # Symmetry
            (1 - noise) * 10         # Low noise
        )
        
        return int(score)
    
    def _get_quality_label(self, score):
        """Get quality label from score."""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "FAIR"
        elif score >= 20:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def _get_recommendation(self, score, has_u, symmetry, noise):
        """Get recommendation text."""
        if score >= 70 and has_u:
            return "⭐⭐⭐ HIGHLY PROMISING - Clear U-shape detected"
        elif score >= 50 and has_u:
            return "⭐⭐ PROMISING - Good signal but verify manually"
        elif score >= 30:
            return "⭐ UNCERTAIN - Weak signal, likely false positive"
        else:
            return "❌ NOT RECOMMENDED - No clear transit pattern"
    
    def scan_all_reports(self, output_dir="output"):
        """
        Scan all PNG files in output directory.
        
        Returns:
            List of dicts with analysis results
        """
        results = []
        
        if not os.path.exists(output_dir):
            return results
        
        # Find all PNG files
        for filename in os.listdir(output_dir):
            if filename.endswith('_report.png'):
                tic_id = filename.replace('_report.png', '').replace('_', ' ')
                filepath = os.path.join(output_dir, filename)
                
                analysis = self.analyze_report(filepath)
                analysis['tic_id'] = tic_id
                analysis['filename'] = filename
                
                results.append(analysis)
        
        # Sort by score (best first)
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results
