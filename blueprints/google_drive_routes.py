from flask import Blueprint, redirect, url_for, session, request, flash
from flask_login import login_required, current_user
from google_auth_oauthlib.flow import Flow
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for local testing

google_drive_bp = Blueprint('google_drive', __name__)

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'

@google_drive_bp.route('/authorize-drive')
@login_required
def authorize_drive():
    """Initiate OAuth flow for Google Drive"""
    if not current_user.is_admin():
        flash('Only admins can authorize Google Drive access')
        return redirect(url_for('index'))
    
    # Determine redirect URI based on environment
    if 'localhost' in request.host or '127.0.0.1' in request.host:
        redirect_uri = 'http://localhost:7777/oauth2callback'
    else:
        redirect_uri = 'https://czesnowski.pythonanywhere.com/oauth2callback'
    
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@google_drive_bp.route('/oauth2callback')
@login_required
def oauth2callback():
    """Handle OAuth callback"""
    state = session.get('state')
    
    # Determine redirect URI based on environment
    if 'localhost' in request.host or '127.0.0.1' in request.host:
        redirect_uri = 'http://localhost:7777/oauth2callback'
    else:
        redirect_uri = 'https://czesnowski.pythonanywhere.com/oauth2callback'
    
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=redirect_uri
    )
    
    flow.fetch_token(authorization_response=request.url)
    
    # Save credentials
    credentials = flow.credentials
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())
    
    flash('Google Drive authorized successfully!')
    return redirect(url_for('index'))