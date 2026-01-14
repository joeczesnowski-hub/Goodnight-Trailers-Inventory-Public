from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from google_drive_service import get_drive_service, get_or_create_vin_folder, upload_photo, get_folder_link

photo_upload_bp = Blueprint('photo_upload', __name__)

UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'heif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@photo_upload_bp.route('/api/upload-photos', methods=['POST'])
@login_required
def upload_photos():
    """Upload photos to Google Drive"""
    if not current_user.is_admin():
        return jsonify({'error': 'Only admins can upload photos'}), 403
    
    # Get VIN from form data
    vin = request.form.get('vin')
    if not vin:
        return jsonify({'error': 'VIN is required'}), 400
    
    # Get uploaded files
    if 'photos' not in request.files:
        return jsonify({'error': 'No photos uploaded'}), 400
    
    files = request.files.getlist('photos')
    if len(files) == 0:
        return jsonify({'error': 'No photos selected'}), 400
    
    # Get Google Drive service
    service = get_drive_service()
    if not service:
        return jsonify({'error': 'Google Drive not authorized. Please authorize first.'}), 401
    
    try:
        # Create temp upload folder if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Get or create VIN folder in Drive (root level)
        folder_id = get_or_create_vin_folder(service, vin, 'root')
        
        uploaded_files = []
        
        # Upload each file
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save temporarily
                file.save(temp_path)
                
                # Upload to Google Drive
                uploaded_file = upload_photo(service, temp_path, folder_id)
                uploaded_files.append(uploaded_file)
                
                # Delete temp file
                os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'folder_id': folder_id,
            'folder_link': get_folder_link(folder_id),
            'uploaded_count': len(uploaded_files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500