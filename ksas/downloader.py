import lightkurve as lk
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataDownloader:
    """
    Handles downloading of LightCurve data from MAST via Lightkurve.
    """
    
    def __init__(self):
        pass

    def download_lightcurve(self, target_id: str, mission: str = "TESS", author: str = "SPOC", exptime: int = 120):
        """
        Downloads the light curve for a given target.
        
        Args:
            target_id (str): The ID of the target (e.g., "TIC 261136679").
            mission (str): Mission name (TESS, Kepler, K2).
            author (str): Data product author (SPOC is standard for TESS).
            exptime (int): Exposure time in seconds (120 for 2-min cadence).
            
        Returns:
            lightkurve.LightCurve: The stitched and processed light curve, or None if failed.
        """
        logger.info(f"Searching data for {target_id} (Mission: {mission})...")
        
        # Rate limiting: sleep briefly to be polite to MAST servers
        import time
        time.sleep(1.0)  # 1 second delay between requests
        
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Search for light curve files
                search_result = lk.search_lightcurve(
                    target_id, 
                    mission=mission, 
                    author=author,
                    exptime=exptime
                )
                
                if len(search_result) == 0:
                    logger.warning(f"No data found for {target_id} with specified parameters.")
                    return None
                
                logger.info(f"Found {len(search_result)} observations. Downloading...")
                
                # Download only the last one (latest sector)
                lc = search_result[-1].download()
                
                if lc is None:
                    logger.error(f"Download failed for {target_id}.")
                    return None
                    
                logger.info(f"Successfully downloaded data for {target_id} (Sector/Quarter {lc.sector if hasattr(lc, 'sector') else '?'}).")
                return lc
                
            except Exception as e:
                if "No route to host" in str(e) or "Connection refused" in str(e):
                    logger.warning(f"Connection error for {target_id} (Attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        sleep_time = retry_delay * (attempt + 1)
                        logger.info(f"Waiting {sleep_time}s before retrying...")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"Max retries exceeded for {target_id}. Skipping.")
                        return None
                else:
                    # Other errors (e.g. data errors) might not be recoverable by waiting
                    logger.error(f"An error occurred while downloading {target_id}: {e}")
                    return None

    def generate_random_targets(self):
        """
        Generator that yields random TIC IDs indefinitely.
        This is for discovering NEW exoplanets, not analyzing known ones.
        
        TIC IDs range from roughly 1 to 500,000,000+ but not all have TESS data.
        We'll generate random IDs and let the download function handle failures.
        
        Yields:
            str: Random TIC ID in the format "TIC XXXXXXXX"
        """
        import random
        
        logger.info("Entering continuous discovery mode - generating random targets...")
        
        # TIC catalog has entries up to ~500 million
        # But most productive range is 1-450 million
        MIN_TIC = 1000000
        MAX_TIC = 450000000
        
        while True:
            # Generate random TIC ID
            tic_number = random.randint(MIN_TIC, MAX_TIC)
            target_id = f"TIC {tic_number}"
            yield target_id
