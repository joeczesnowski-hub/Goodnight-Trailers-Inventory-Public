#!/usr/bin/env python3
"""
Script to link existing Google Drive folders (organized by VIN) to inventory items.
"""

import sqlite3
from google_drive_service import get_drive_service

def get_all_vin_folders(service):
    """Get all folders from Google Drive root"""
    
    query = "mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false"
    
    all_folders = {}
    page_token = None
    
    while True:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageSize=1000,
            pageToken=page_token
        ).execute()
        
        folders = results.get('files', [])
        for folder in folders:
            all_folders[folder['name']] = folder['id']
        
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return all_folders

def link_folders_to_inventory():
    """Match VIN folders to inventory items and update database"""
    
    print("Getting Google Drive service...")
    service = get_drive_service()
    if not service:
        print("ERROR: Could not authenticate with Google Drive")
        return
    
    print("Fetching folders from Google Drive root...")
    folders = get_all_vin_folders(service)
    print(f"Found {len(folders)} folders in Google Drive")
    
    # Connect to database
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    updated_count = 0
    
    # Check each table
    for table in ['inventory', 'trucks', 'classic_cars']:
        print(f"\nProcessing {table}...")
        
        # Get all items with VINs
        cursor.execute(f'SELECT id, vin, google_drive_folder_id FROM {table} WHERE vin IS NOT NULL AND vin != ""')
        items = cursor.fetchall()
        
        for item_id, vin, existing_folder_id in items:
            # Skip if already has a folder linked
            if existing_folder_id:
                continue
                
            # Check if there's a folder matching this VIN (exact match)
            if vin in folders:
                folder_id = folders[vin]
                cursor.execute(f'UPDATE {table} SET google_drive_folder_id = ? WHERE id = ?', (folder_id, item_id))
                print(f"  ✓ Linked VIN {vin} to folder ID {folder_id}")
                updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Done! Updated {updated_count} items with folder links.")

if __name__ == "__main__":
    link_folders_to_inventory()