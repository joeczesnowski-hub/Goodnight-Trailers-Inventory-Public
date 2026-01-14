from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import logging
from functools import wraps

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to check admin permissions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    return render_template('react_admin.html')

@admin_bp.route('/api/users', methods=['GET'])
@login_required
@admin_required
def api_get_users():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.role, u.is_active, u.created_at,
                   u.last_login, u.email, u.group_id, g.name as group_name
            FROM users u
            LEFT JOIN groups g ON u.group_id = g.id
            ORDER BY u.id
        ''')
        users = cursor.fetchall()
        conn.close()

        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'is_active': user[3],
                'created_at': user[4],
                'last_login': user[5],
                'email': user[6],
                'group_id': user[7],
                'group_name': user[8]
            })

        return jsonify(users_list)
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': str(e)}), 500

# ============== GROUP API ROUTES ==============

@admin_bp.route('/api/groups', methods=['GET'])
@login_required
@admin_required
def api_get_groups():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, g.can_view, g.can_edit, g.can_delete, 
                   g.can_view_financial, g.can_view_summary, g.can_view_sold,
                   g.receive_new_item_emails, g.receive_sold_item_emails,
                   (SELECT COUNT(*) FROM users WHERE group_id = g.id) as user_count
            FROM groups g
            ORDER BY g.id
        ''')
        groups = cursor.fetchall()
        conn.close()

        groups_list = []
        for group in groups:
            groups_list.append({
                'id': group[0],
                'name': group[1],
                'can_view': group[2],
                'can_edit': group[3],
                'can_delete': group[4],
                'can_view_financial': group[5],
                'can_view_summary': group[6],
                'can_view_sold': group[7],
                'receive_new_item_emails': group[8],
                'receive_sold_item_emails': group[9],
                'user_count': group[10]
            })

        return jsonify(groups_list)
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/groups', methods=['POST'])
@login_required
@admin_required
def api_add_group():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Group name is required'}), 400

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO groups (name, can_view, can_edit, can_delete, 
                               can_view_financial, can_view_summary, can_view_sold,
                               receive_new_item_emails, receive_sold_item_emails)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            data.get('can_view', 1),
            data.get('can_edit', 0),
            data.get('can_delete', 0),
            data.get('can_view_financial', 0),
            data.get('can_view_summary', 0),
            data.get('can_view_sold', 0),
            data.get('receive_new_item_emails', 0),
            data.get('receive_sold_item_emails', 0)
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({'success': True, 'id': new_id})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Group name already exists'}), 400
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/groups/<int:group_id>', methods=['PUT'])
@login_required
@admin_required
def api_edit_group(group_id):
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE groups SET
                name = ?,
                can_view = ?,
                can_edit = ?,
                can_delete = ?,
                can_view_financial = ?,
                can_view_summary = ?,
                can_view_sold = ?,
                receive_new_item_emails = ?,
                receive_sold_item_emails = ?
            WHERE id = ?
        ''', (
            data.get('name'),
            data.get('can_view', 0),
            data.get('can_edit', 0),
            data.get('can_delete', 0),
            data.get('can_view_financial', 0),
            data.get('can_view_summary', 0),
            data.get('can_view_sold', 0),
            data.get('receive_new_item_emails', 0),
            data.get('receive_sold_item_emails', 0),
            group_id
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating group: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/groups/<int:group_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_group(group_id):
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE group_id = ?', (group_id,))
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            conn.close()
            return jsonify({'error': f'Cannot delete group with {user_count} user(s) assigned'}), 400
        
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/account/settings', methods=['GET'])
@login_required
def api_get_account_settings():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT email, receive_new_item_emails, receive_sold_item_emails 
                          FROM users WHERE id = ?''', (current_user.id,))
        user_data = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'email': user_data[0] if user_data else None,
            'receive_new_item_emails': user_data[1] if user_data else 0,
            'receive_sold_item_emails': user_data[2] if user_data else 0
        })
    except Exception as e:
        logger.error(f"Error fetching account settings: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def admin_add_user():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '').strip()
        group_id = request.form.get('group_id')

        if not username or not password:
            flash('Username and password required')
            return redirect(url_for('admin.admin_users'))

        if not group_id:
            flash('Please select a group')
            return redirect(url_for('admin.admin_users'))

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Get the group name to set the role
        cursor.execute('SELECT name FROM groups WHERE id = ?', (group_id,))
        group = cursor.fetchone()
        role = group[0].lower() if group else 'user'
        
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, group_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, role, email if email else None, group_id))
        conn.commit()
        conn.close()

        flash(f'User {username} created successfully')
    except sqlite3.IntegrityError:
        flash('Username already exists')
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        flash('Error creating user')

    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    try:
        email = request.form.get('email', '').strip()
        group_id = request.form.get('group_id')
        is_active = int(request.form.get('is_active', 1))
        new_password = request.form.get('new_password', '').strip()

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Get the group name to update the role
        cursor.execute('SELECT name FROM groups WHERE id = ?', (group_id,))
        group = cursor.fetchone()
        role = group[0].lower() if group else 'user'
        
        cursor.execute('''
            UPDATE users SET email = ?, group_id = ?, role = ?, is_active = ?
            WHERE id = ?
        ''', (email if email else None, group_id, role, is_active, user_id))
        
        if new_password:
            password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        
        conn.commit()
        conn.close()

        flash('User updated successfully')
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        flash('Error updating user')

    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    try:
        if user_id == current_user.id:
            flash('Cannot delete your own account')
            return redirect(url_for('admin.admin_users'))

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        flash('User deleted successfully')
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        flash('Error deleting user')

    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/smtp-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def smtp_settings():
    if request.method == 'POST':
        try:
            data = request.json
            
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            
            # Save SMTP settings
            for key, value in data.items():
                if key == 'mail_password' and not value:
                    continue  # Skip if password is blank (keep existing)
                
                cursor.execute('''
                    INSERT INTO smtp_settings (setting_key, setting_value, updated_at)
                    VALUES (?, ?, datetime('now'))
                    ON CONFLICT(setting_key) DO UPDATE SET 
                        setting_value = excluded.setting_value,
                        updated_at = datetime('now')
                ''', (key, str(value)))
            
            conn.commit()
            conn.close()
            
            # Reinitialize mail with new settings
            from email_service import init_mail
            from flask import current_app
            init_mail(current_app)
            
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error saving SMTP settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    return render_template('smtp_settings.html')

@admin_bp.route('/api/smtp-settings', methods=['GET'])
@login_required
@admin_required
def api_get_smtp_settings():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT setting_key, setting_value FROM smtp_settings')
        rows = cursor.fetchall()
        conn.close()
        
        settings = {row[0]: row[1] for row in rows}
        
        # Convert string 'True'/'False' to boolean for mail_use_tls
        if 'mail_use_tls' in settings:
            settings['mail_use_tls'] = settings['mail_use_tls'].lower() == 'true'
        
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error getting SMTP settings: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-email', methods=['POST'])
@login_required
@admin_required
def test_email():
    try:
        from email_service import mail
        from flask_mail import Message
        
        if not current_user.email:
            return jsonify({'error': 'No email address set for your account. Please add one in Account Settings.'}), 400
        
        msg = Message(
            subject="✅ Test Email from Goodnight Trailers",
            recipients=[current_user.email],
            html="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 30px; border-radius: 10px; text-align: center; }
                    .content { padding: 20px; background: #f8f9fa; border-radius: 10px; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">✅ Success!</h1>
                        <p style="margin: 10px 0 0 0; font-size: 18px;">Your SMTP settings are working correctly</p>
                    </div>
                    <div class="content">
                        <p>This is a test email from your Goodnight Trailers Inventory Management System.</p>
                        <p>If you received this message, your email notifications are configured properly and ready to use.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
        
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

@admin_bp.route('/api/activity-report', methods=['GET'])
@login_required
@admin_required
def api_activity_report():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Get new items from last 7 days
        new_items = []
        
        # Trailers (inventory table)
        cursor.execute('''
            SELECT id, year, make, type, vin, created_at, 'trailers' as category
            FROM inventory
            WHERE created_at >= datetime('now', '-7 days')
            AND deleted_at IS NULL
            ORDER BY created_at DESC
        ''')
        new_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],
            'vin': row[4],
            'created_at': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Bucket Trucks (use model instead of type)
        cursor.execute('''
            SELECT id, year, make, model, vin, created_at, 'trucks' as category
            FROM trucks
            WHERE created_at >= datetime('now', '-7 days')
            AND deleted_at IS NULL
            ORDER BY created_at DESC
        ''')
        new_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],  # Using model as type
            'vin': row[4],
            'created_at': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Classic Cars (use model instead of type)
        cursor.execute('''
            SELECT id, year, make, model, vin, created_at, 'classic_cars' as category
            FROM classic_cars
            WHERE created_at >= datetime('now', '-7 days')
            AND deleted_at IS NULL
            ORDER BY created_at DESC
        ''')
        new_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],  # Using model as type
            'vin': row[4],
            'created_at': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Get deleted items from last 7 days
        deleted_items = []
        
        # Trailers
        cursor.execute('''
            SELECT id, year, make, type, vin, deleted_at, 'trailers' as category
            FROM inventory
            WHERE deleted_at >= datetime('now', '-7 days')
            ORDER BY deleted_at DESC
        ''')
        deleted_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],
            'vin': row[4],
            'deleted_at': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Bucket Trucks
        cursor.execute('''
            SELECT id, year, make, model, vin, deleted_at, 'trucks' as category
            FROM trucks
            WHERE deleted_at >= datetime('now', '-7 days')
            ORDER BY deleted_at DESC
        ''')
        deleted_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],  # Using model as type
            'vin': row[4],
            'deleted_at': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Classic Cars
        cursor.execute('''
            SELECT id, year, make, model, vin, deleted_at, 'classic_cars' as category
            FROM classic_cars
            WHERE deleted_at >= datetime('now', '-7 days')
            ORDER BY deleted_at DESC
        ''')
        deleted_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],  # Using model as type
            'vin': row[4],
            'deleted_at': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        # Get sold items from last 7 days
        sold_items = []
        
        # Trailers
        cursor.execute('''
            SELECT id, year, make, type, vin, sold_date, 'trailers' as category
            FROM inventory
            WHERE sold_date >= date('now', '-7 days')
            AND (sold = "YES" OR sold = "yes")
            ORDER BY sold_date DESC
        ''')
        sold_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],
            'vin': row[4],
            'sold_date': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Bucket Trucks
        cursor.execute('''
            SELECT id, year, make, model, vin, sold_date, 'trucks' as category
            FROM trucks
            WHERE sold_date >= date('now', '-7 days')
            AND (sold = "YES" OR sold = "yes")
            ORDER BY sold_date DESC
        ''')
        sold_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],
            'vin': row[4],
            'sold_date': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        # Classic Cars
        cursor.execute('''
            SELECT id, year, make, model, vin, sold_date, 'classic_cars' as category
            FROM classic_cars
            WHERE sold_date >= date('now', '-7 days')
            AND (sold = "YES" OR sold = "yes")
            ORDER BY sold_date DESC
        ''')
        sold_items.extend([{
            'id': row[0],
            'year': row[1],
            'make': row[2],
            'type': row[3],
            'vin': row[4],
            'sold_date': row[5],
            'category': row[6]
        } for row in cursor.fetchall()])
        
        conn.close()
        
        return jsonify({
            'new_items': new_items,
            'deleted_items': deleted_items,
            'sold_items': sold_items  # ADD THIS
        })
    
        conn.close()
        
        return jsonify({
            'new_items': new_items,
            'deleted_items': deleted_items
        })
    except Exception as e:
        logger.error(f"Error fetching activity report: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/activity-report')
@login_required
@admin_required
def activity_report():
    return render_template('activity_report.html')

@admin_bp.route('/account-settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            # Handle password change
            if action == 'change_password':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')

                if not current_password or not new_password or not confirm_password:
                    flash('All password fields are required')
                    return redirect(url_for('admin.account_settings'))

                if new_password != confirm_password:
                    flash('New passwords do not match')
                    return redirect(url_for('admin.account_settings'))

                # Verify current password
                conn = sqlite3.connect('inventory.db')
                cursor = conn.cursor()
                cursor.execute('SELECT password_hash FROM users WHERE id = ?', (current_user.id,))
                result = cursor.fetchone()

                if not result or not check_password_hash(result[0], current_password):
                    flash('Current password is incorrect')
                    conn.close()
                    return redirect(url_for('admin.account_settings'))

                # Update password
                new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, current_user.id))
                conn.commit()
                conn.close()

                flash('Password changed successfully!')
                return redirect(url_for('index'))
            
            # Handle notification preferences
            elif action == 'update_notifications':
                receive_new_item_emails = 1 if 'receive_new_item_emails' in request.form else 0
                receive_sold_item_emails = 1 if 'receive_sold_item_emails' in request.form else 0
                
                conn = sqlite3.connect('inventory.db')
                cursor = conn.cursor()
                cursor.execute('''UPDATE users 
                                  SET receive_new_item_emails = ?, receive_sold_item_emails = ? 
                                  WHERE id = ?''',
                               (receive_new_item_emails, receive_sold_item_emails, current_user.id))
                conn.commit()
                conn.close()
                
                flash('Notification preferences updated successfully!')
                return redirect(url_for('admin.account_settings'))

        except Exception as e:
            logger.error(f"Error updating account settings: {e}")
            flash('Error updating settings')
            return redirect(url_for('admin.account_settings'))

    # GET request - load current settings
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT email, receive_new_item_emails, receive_sold_item_emails 
                      FROM users WHERE id = ?''', (current_user.id,))
    user_data = cursor.fetchone()
    conn.close()
    
    # GET request - render React page
    return render_template('react_account_settings.html')