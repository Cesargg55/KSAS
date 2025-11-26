import json
import os
import logging

logger = logging.getLogger(__name__)

class StarTracker:
    """
    Tracks analyzed stars to avoid duplicates.
    """
    
    def __init__(self, db_file="analyzed_stars.json"):
        self.db_file = db_file
        self.analyzed = set()
        self.load()
    
    def load(self):
        """Load analyzed stars from file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.analyzed = set(data.get('analyzed', []))
                logger.info(f"Loaded {len(self.analyzed)} previously analyzed stars.")
            except Exception as e:
                logger.warning(f"Could not load star database: {e}")
                self.analyzed = set()
        else:
            logger.info("No previous star database found. Starting fresh.")
            self.analyzed = set()
    
    def save(self):
        """Save analyzed stars to file."""
        try:
            with open(self.db_file, 'w') as f:
                json.dump({'analyzed': list(self.analyzed)}, f)
        except Exception as e:
            logger.error(f"Could not save star database: {e}")
    
    def is_analyzed(self, target_id):
        """Check if a star has been analyzed."""
        return target_id in self.analyzed
    
    def mark_analyzed(self, target_id):
        """Mark a star as analyzed."""
        self.analyzed.add(target_id)
        # Save periodically (every 10 stars to reduce I/O)
        if len(self.analyzed) % 10 == 0:
            self.save()
    
    def get_count(self):
        """Get count of analyzed stars."""
        return len(self.analyzed)
