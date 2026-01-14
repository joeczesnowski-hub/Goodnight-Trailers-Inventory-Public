#!/usr/bin/env python3
"""
Cleanup script to delete Google Drive folders from archive that are older than 14 days.
Run this script periodically (e.g., daily via cron job).
"""

from google_drive_service import get_drive_service, get_or_create_archive_folder, delete_old_archived_folders
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main cleanup function"""
    logger.info("Starting archived folder cleanup...")
    
    try:
        # Get Google Drive service
        service = get_drive_service()
        if not service:
            logger.error("Could not authenticate with Google Drive")
            return
        
        # Get archive folder
        archive_folder_id = get_or_create_archive_folder(service)
        logger.info(f"Archive folder ID: {archive_folder_id}")
        
        # Delete folders older than 14 days
        deleted_count = delete_old_archived_folders(service, archive_folder_id, days=14)
        
        logger.info(f"Cleanup complete. Deleted {deleted_count} folder(s)")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()