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
                logger.error(f"CORRUPTION DETECTED: Could not load star database: {e}")
                # Backup corrupt file
                try:
                    import shutil
                    backup_name = self.db_file + ".corrupt"
                    shutil.copy(self.db_file, backup_name)
                    logger.warning(f"Backed up corrupt database to {backup_name}")
                except:
                    pass
                # Do NOT reset if it's just a read error, but here we assume corruption.
                # If we reset, we lose data. But if we don't, we can't run.
                # We start fresh but keep the backup.
                self.analyzed = set()
        else:
            logger.info("No previous star database found. Starting fresh.")
            self.analyzed = set()
    
    def save(self):
        """Save analyzed stars to file (Atomic Write)."""
        try:
            # Write to temp file first
            temp_file = self.db_file + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump({'analyzed': list(self.analyzed)}, f)
                f.flush()
                os.fsync(f.fileno()) # Ensure write to disk
            
            # Atomic replace
            os.replace(temp_file, self.db_file)
            
        except Exception as e:
            logger.error(f"Could not save star database: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
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
