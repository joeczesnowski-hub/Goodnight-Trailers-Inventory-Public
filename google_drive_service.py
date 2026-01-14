from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_drive_service():
    """Get authenticated Google Drive service"""
    creds = None
    
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            return None  # Need to authenticate via OAuth flow
    
    # Save credentials for next run
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def create_folder(service, folder_name, parent_folder_id=None):
    """Create a folder in Google Drive"""
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_photo(service, file_path, folder_id):
    """Upload a photo to a Google Drive folder"""
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()
    
    return file

def get_or_create_vin_folder(service, vin, parent_folder_id):
    """Get existing folder by VIN or create new one"""
    # Search for existing folder
    query = f"name='{vin}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        return folders[0]['id']
    else:
        # Create new folder
        return create_folder(service, vin, parent_folder_id)

def get_folder_link(folder_id):
    """Get shareable link to folder"""
    return f"https://drive.google.com/drive/folders/{folder_id}"

def move_folder_to_archive(service, folder_id, archive_parent_id):
    """Move a folder to the archive (to be deleted) parent folder"""
    try:
        # Remove from current parent and add to archive parent
        file = service.files().get(fileId=folder_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        
        # Move the file to the new folder
        file = service.files().update(
            fileId=folder_id,
            addParents=archive_parent_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error moving folder to archive: {e}")
        return False

def get_or_create_archive_folder(service):
    """Get or create the 'Archive - To Delete' folder"""
    folder_name = "Archive - To Delete"
    
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        return folders[0]['id']
    else:
        # Create the archive folder at root level
        return create_folder(service, folder_name, None)

def delete_old_archived_folders(service, archive_parent_id, days=14):
    """Delete folders in archive that are older than specified days"""
    import datetime
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    cutoff_date_str = cutoff_date.isoformat() + 'Z'
    
    # Find all folders in the archive folder older than cutoff date
    query = f"'{archive_parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and modifiedTime < '{cutoff_date_str}' and trashed=false"
    
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, modifiedTime)'
        ).execute()
        
        folders = results.get('files', [])
        deleted_count = 0
        
        for folder in folders:
            try:
                service.files().delete(fileId=folder['id']).execute()
                deleted_count += 1
                print(f"Deleted folder: {folder['name']} (modified: {folder['modifiedTime']})")
            except Exception as e:
                print(f"Error deleting folder {folder['name']}: {e}")
        
        return deleted_count
    except Exception as e:
        print(f"Error finding old folders: {e}")
        return 0