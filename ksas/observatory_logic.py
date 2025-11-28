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

    @staticmethod
    def calculate_derived_parameters(data):
        """
        Calculate comprehensive derived physical parameters.
        Updates the data dictionary in place with new fields.
        """
        import math
        
        # 1. Extract Inputs (with defaults for Sun-like star if missing)
        period = data.get('period', 0)
        depth = data.get('depth', 0)
        
        # Stellar Parameters (Defaults: Sun)
        r_star = data.get('r_star', 1.0)
        m_star = data.get('m_star', 1.0)
        teff = data.get('teff', 5778)
        
        if period <= 0: return data
        
        # 2. Standardize Depth (to ratio)
        # If depth > 1, assume it's ppm? Or percent? 
        # KSAS usually stores depth as ratio (e.g. 0.01 for 1%).
        # But if it's > 1, it might be ppm (e.g. 3000).
        # Let's assume if < 1 it's ratio.
        depth_ratio = depth
        if depth > 1:
             # If > 1, could be ppm or percent?
             # If > 100, definitely ppm.
             if depth > 100: depth_ratio = depth / 1e6
             else: depth_ratio = depth / 100.0 # Percent
        
        # 3. Calculations
        
        # Rp/R*
        rp_rs = math.sqrt(depth_ratio)
        data['rp_rs'] = rp_rs
        
        # Planet Radius (Earth Radii)
        # R_p (Earth) = Rp/R* * R_star (Sun) * 109
        r_planet_earth = rp_rs * r_star * 109.0
        data['r_planet_earth'] = r_planet_earth
        
        # Semi-major Axis (AU)
        # a (AU) = [ M_s * P_yr^2 ]^(1/3)
        p_years = period / 365.25
        a_au = (m_star * (p_years ** 2)) ** (1/3)
        data['a_au'] = a_au
        
        # a / R*
        # 1 AU = 215.032 R_sun
        if r_star > 0:
            a_rs = (a_au * 215.032) / r_star
            data['a_rs'] = a_rs
        else:
            data['a_rs'] = 0
            
        # Equilibrium Temperature (K)
        # Teq = Teff * sqrt(R_s / 2a)
        # R_s / a = 1 / a_rs
        if data.get('a_rs', 0) > 0:
            teq = teff * math.sqrt(1 / (2 * data['a_rs']))
            data['teq'] = teq
        else:
            data['teq'] = 0
            
        # Insolation Flux (Earth Flux)
        # S = (R_s/a)^2 * (Teff/Tsun)^4
        if a_au > 0:
            l_star_sun = (r_star**2) * ((teff/5778)**4)
            insolation = l_star_sun / (a_au**2)
            data['insolation'] = insolation
        else:
            data['insolation'] = 0
            
        # Estimations for Inclination and Impact Parameter
        # Without a full fit, these are rough estimates for transiting planets
        # Impact parameter b = a/R* * cos(i)
        # For a transit to occur, b < 1 + Rp/R*
        # We'll estimate b ~ 0.3 (typical average) and derive i
        
        b_est = 0.3
        data['impact_parameter'] = b_est
        
        # i = arccos(b / (a/R*))
        if data.get('a_rs', 0) > 0:
            # Ensure argument is within domain [-1, 1]
            arg = b_est / data['a_rs']
            if arg > 1: arg = 1
            
            inclination_rad = math.acos(arg)
            inclination_deg = math.degrees(inclination_rad)
            data['inclination'] = inclination_deg
        else:
            data['inclination'] = 90.0 # Default edge-on
            
        return data
