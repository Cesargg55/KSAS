"""
Observatory Logic Engine
Provides intelligent analysis and physical parameter estimation for candidates.
"""

import numpy as np

class ObservatoryLogic:
    """
    The brain of the Observatory.
    Calculates physics and generates insights.
    """
    
    # Constants
    R_SUN_KM = 696340
    R_EARTH_KM = 6371
    R_JUPITER_KM = 69911
    AU_KM = 149597870.7
    
    @staticmethod
    def calculate_planet_radius(depth_percent, star_radius_solar=1.0):
        """
        Calculate planet radius in Earth radii.
        Rp = R* * sqrt(depth)
        """
        # depth is in percent (e.g. 1.0 = 1%)
        depth_fraction = depth_percent / 100.0
        r_planet_solar = star_radius_solar * np.sqrt(depth_fraction)
        
        # Convert to Earth radii
        r_planet_earth = (r_planet_solar * ObservatoryLogic.R_SUN_KM) / ObservatoryLogic.R_EARTH_KM
        return r_planet_earth

    @staticmethod
    def estimate_equilibrium_temp(star_temp, period, star_mass_solar=1.0, albedo=0.3):
        """
        Estimate equilibrium temperature (assuming circular orbit).
        Teq = T* * (1-A)^0.25 * sqrt(R* / 2a)
        """
        # Kepler's 3rd Law to get semi-major axis (a) in AU
        # a^3 = P^2 * M (approx)
        # P in years, M in solar masses
        period_years = period / 365.25
        a_au = (period_years**2 * star_mass_solar)**(1/3)
        
        # Convert a to km and R* to km
        a_km = a_au * ObservatoryLogic.AU_KM
        r_star_km = 1.0 * ObservatoryLogic.R_SUN_KM # Assuming Sun-like for now if unknown
        
        # Simplified calculation
        # Teq = T* * sqrt(R* / 2a) * (1-A)^0.25
        teq = star_temp * np.sqrt(r_star_km / (2 * a_km)) * ((1 - albedo)**0.25)
        return teq, a_au

    @staticmethod
    def classify_planet(radius_earth):
        """Classify planet type based on radius."""
        if radius_earth < 1.25:
            return "Earth-sized (Rocky)"
        elif radius_earth < 2.0:
            return "Super-Earth"
        elif radius_earth < 6.0:
            return "Neptune-like (Gas/Ice)"
        elif radius_earth < 15.0:
            return "Jupiter-sized (Gas Giant)"
        else:
            return "Brown Dwarf / Low-mass Star"

    @staticmethod
    def generate_analysis_text(data):
        """
        Generate a natural language analysis of the candidate.
        """
        snr = data.get('snr', 0)
        depth = data.get('depth_percent', 0)
        period = data.get('period', 0)
        score = data.get('score', 0)
        
        # Fallback: Calculate score if missing
        if score == 0:
            from ksas.candidate_quality_analyzer import CandidateQualityAnalyzer
            try:
                analyzer = CandidateQualityAnalyzer()
                # Reconstruct result dict
                temp_result = {
                    'tic_id': data.get('tic_id', 'Unknown'),
                    'period': period,
                    'depth': data.get('depth', 0),
                    'snr': snr,
                    'vetting_passed': data.get('vetting_passed', False)
                }
                score_data = analyzer.analyze_candidate(data.get('tic_id', 'Unknown'), temp_result)
                score = score_data['score']
                # Update data dict so GUI can use it too if needed
                data['score'] = score
            except Exception:
                pass # Keep as 0 if calculation fails
        
        lines = []
        
        # 1. Signal Strength
        if snr > 50:
            lines.append(f"• 📡 **Signal Strength:** EXTREME (SNR {snr:.1f}). This is a very clear signal.")
        elif snr > 20:
            lines.append(f"• 📡 **Signal Strength:** STRONG (SNR {snr:.1f}). Reliable detection.")
        elif snr > 10:
            lines.append(f"• 📡 **Signal Strength:** MODERATE (SNR {snr:.1f}). Borderline, check visually.")
        else:
            lines.append(f"• 📡 **Signal Strength:** WEAK (SNR {snr:.1f}). High risk of noise.")
            
        # 2. Transit Depth & Type
        r_p = ObservatoryLogic.calculate_planet_radius(depth)
        p_type = ObservatoryLogic.classify_planet(r_p)
        
        lines.append(f"• 🌑 **Transit Depth:** {depth:.3f}%.")
        lines.append(f"• 🪐 **Estimated Size:** {r_p:.2f} x Earth ({p_type}).")
        
        if depth > 5.0:
            lines.append("• ⚠️ **Warning:** Depth > 5% suggests an Eclipsing Binary, not a planet.")
        
        # 3. Period
        if period < 1.0:
            lines.append(f"• ⏱️ **Period:** Ultra-short ({period:.3f} days). Tidally locked, very hot.")
        elif period > 10.0:
            lines.append(f"• ⏱️ **Period:** Long ({period:.1f} days). Less likely to be false positive.")
            
        # 4. Overall Verdict
        if score >= 90:
            lines.append("\n**🤖 AI VERDICT:** This is a top-tier candidate. Prioritize for publication.")
        elif score >= 60:
            lines.append("\n**🤖 AI VERDICT:** Good candidate. Check for secondary eclipses manually.")
        else:
            lines.append("\n**🤖 AI VERDICT:** Likely a false positive or binary. Treat with skepticism.")
            
        return "\n".join(lines)

    @staticmethod
    def generate_graph_explanation(data):
        """
        Generate a beginner-friendly explanation of what the graphs show.
        """
        snr = data.get('snr', 0)
        depth = data.get('depth_percent', 0)
        period = data.get('period', 0)
        score = data.get('score', 0)
        
        explanation = []
        
        # 1. Phase Folded Graph Explanation
        explanation.append("📊 **What are we seeing in the Phase Folded Graph?**")
        explanation.append("This graph stacks all the transits on top of each other. It shows the 'shape' of the shadow.")
        
        if snr > 50:
            explanation.append("\n✅ **Crystal Clear Signal:** The dip is extremely distinct against the background noise. This is exactly what we look for in a high-quality candidate.")
        elif snr > 20:
            explanation.append("\n✅ **Clear Signal:** The dip is visible and distinct. It stands out well from the noise.")
        else:
            explanation.append("\n⚠️ **Noisy Signal:** The dip is hard to see clearly. The points are scattered, which means the camera noise is almost as strong as the signal itself.")
            
        if depth > 1.0:
            explanation.append("\n📉 **Deep Dip (Giant Planet):** The curve goes down significantly (>1%). This means a very large object is blocking the star. The 'U' shape is deep and wide.")
        elif depth > 0.1:
            explanation.append("\n📉 **Moderate Dip (Gas Giant/Neptune):** The curve is clearly visible but not huge. This is typical for Neptune-sized or Jupiter-sized planets.")
        else:
            explanation.append("\n📉 **Shallow Dip (Rocky Planet):** The dip is tiny (<0.1%). This suggests a small, Earth-sized planet. These are the hardest to find!")
            
        # 2. Full Lightcurve Explanation
        explanation.append("\n\n📈 **What about the Full Lightcurve?**")
        explanation.append("This shows the star's brightness over time (usually ~27 days).")
        
        if period < 1.0:
            explanation.append(f"\n⏱️ **Rapid Transits:** The dips happen very frequently (every {period:.2f} days). You should see many vertical lines in the graph.")
        elif period > 10.0:
            explanation.append(f"\n⏱️ **Sparse Transits:** The dips are far apart (every {period:.1f} days). You might only see 2 or 3 dips in the whole graph.")
            
        # 3. Shape Analysis (Heuristic)
        explanation.append("\n\n🔍 **Shape Analysis:**")
        if depth > 5.0:
             explanation.append("⚠️ **V-Shape Warning:** The dip is very deep. If it looks like a sharp 'V', it's likely an Eclipsing Binary (two stars) rather than a planet.")
        else:
             explanation.append("✅ **U-Shape:** We are looking for a flat-bottomed 'U' shape. This indicates a planet passing fully in front of the star.")

        return "\n".join(explanation)
