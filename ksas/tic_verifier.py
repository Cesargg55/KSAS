import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TICVerifier:
    """
    Verifies if a TIC ID is already discovered/cataloged.
    Checks multiple databases: ExoFOP, NASA Exoplanet Archive, SIMBAD.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KSAS-Exoplanet-Verifier/4.2'
        })
    
    def verify_tic(self, tic_id):
        """
        Verify a TIC ID across multiple databases.
        
        Args:
            tic_id: TIC ID (e.g., "TIC 24909452" or "24909452")
            
        Returns:
            dict with verification results
        """
        # Clean TIC ID
        tic_num = tic_id.replace("TIC", "").strip()
        
        result = {
            'tic_id': f"TIC {tic_num}",
            'tic_number': tic_num,
            'timestamp': datetime.now().isoformat(),
            'exofop': self._check_exofop(tic_num),
            'nasa_archive': self._check_nasa_archive(tic_num),
            'simbad': self._check_simbad(tic_num),
            'is_discovered': False,
            'summary': '',
            'details': []
        }
        
        # Determine if discovered
        if result['exofop']['found'] or result['nasa_archive']['found']:
            result['is_discovered'] = True
            result['summary'] = "⚠️ YA DESCUBIERTO"
        else:
            result['is_discovered'] = False
            result['summary'] = "✅ NO ENCONTRADO (potencialmente nuevo)"
        
        # Build details
        if result['exofop']['found']:
            result['details'].append(f"ExoFOP: {result['exofop']['status']}")
        if result['nasa_archive']['found']:
            result['details'].append(f"NASA Archive: {result['nasa_archive']['planet_name']}")
        if result['simbad']['found']:
            result['details'].append(f"SIMBAD: {result['simbad']['object_type']}")
        
        return result
    
    def _check_exofop(self, tic_num):
        """Check ExoFOP-TESS database."""
        try:
            # ExoFOP-TESS API
            url = f"https://exofop.ipac.caltech.edu/tess/download_toi.php?toi=&tid={tic_num}&output=pipe"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200 and len(response.text.strip()) > 100:
                # Has data
                lines = response.text.strip().split('\n')
                if len(lines) > 1:  # Header + data
                    return {
                        'found': True,
                        'status': 'Listed in ExoFOP (TOI)',
                        'raw_data': response.text[:500]  # First 500 chars
                    }
            
            return {'found': False, 'status': 'Not in ExoFOP'}
            
        except Exception as e:
            logger.error(f"ExoFOP check failed: {e}")
            return {'found': False, 'status': f'Error: {str(e)}'}
    
    def _check_nasa_archive(self, tic_num):
        """Check NASA Exoplanet Archive."""
        try:
            # TAP query for TIC ID
            query = f"""
            SELECT pl_name, hostname, discoverymethod, disc_year
            FROM ps
            WHERE tic_id = '{tic_num}'
            """
            
            url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
            params = {
                'query': query,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    planet = data[0]
                    return {
                        'found': True,
                        'planet_name': planet.get('pl_name', 'Unknown'),
                        'host_star': planet.get('hostname', 'Unknown'),
                        'discovery_method': planet.get('discoverymethod', 'Unknown'),
                        'discovery_year': planet.get('disc_year', 'Unknown')
                    }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"NASA Archive check failed: {e}")
            return {'found': False, 'error': str(e)}
    
    def _check_simbad(self, tic_num):
        """Check SIMBAD database."""
        try:
            # SIMBAD TAP query
            url = "http://simbad.u-strasbg.fr/simbad/sim-id"
            params = {
                'Ident': f"TIC {tic_num}",
                'output.format': 'votable'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200 and 'No known catalog' not in response.text:
                # Found in SIMBAD
                return {
                    'found': True,
                    'object_type': 'Star cataloged in SIMBAD'
                }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"SIMBAD check failed: {e}")
            return {'found': False}
    
    def format_result(self, result):
        """Format result for display."""
        lines = []
        lines.append("="*60)
        lines.append(f"TIC VERIFICATION: {result['tic_id']}")
        lines.append("="*60)
        lines.append("")
        lines.append(f"Status: {result['summary']}")
        lines.append("")
        
        if result['details']:
            lines.append("Details:")
            for detail in result['details']:
                lines.append(f"  - {detail}")
            lines.append("")
        
        lines.append("Database Checks:")
        lines.append(f"  ExoFOP-TESS: {'✓ FOUND' if result['exofop']['found'] else '✗ Not found'}")
        lines.append(f"  NASA Archive: {'✓ FOUND' if result['nasa_archive']['found'] else '✗ Not found'}")
        lines.append(f"  SIMBAD: {'✓ FOUND' if result['simbad']['found'] else '✗ Not found'}")
        lines.append("")
        
        if result['nasa_archive']['found']:
            lines.append("NASA Archive Info:")
            lines.append(f"  Planet: {result['nasa_archive'].get('planet_name', 'N/A')}")
            lines.append(f"  Host Star: {result['nasa_archive'].get('host_star', 'N/A')}")
            lines.append(f"  Method: {result['nasa_archive'].get('discovery_method', 'N/A')}")
            lines.append(f"  Year: {result['nasa_archive'].get('discovery_year', 'N/A')}")
            lines.append("")
        
        lines.append("="*60)
        
        return "\n".join(lines)


# Standalone script functionality
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tic_verifier.py <TIC_ID>")
        print("Example: python tic_verifier.py 24909452")
        print("         python tic_verifier.py 'TIC 24909452'")
        sys.exit(1)
    
    tic_id = " ".join(sys.argv[1:])
    
    verifier = TICVerifier()
    print(f"\nVerifying {tic_id}...\n")
    
    result = verifier.verify_tic(tic_id)
    print(verifier.format_result(result))
