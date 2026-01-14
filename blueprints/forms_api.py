from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
import sqlite3
import logging
from datetime import datetime
from functools import wraps
from google_drive_service import get_drive_service, move_folder_to_archive, get_or_create_archive_folder

logger = logging.getLogger(__name__)

forms_api_bp = Blueprint('forms_api', __name__)

def edit_required(f):
    """Decorator to check edit permissions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_edit_permission():
            return jsonify({'error': 'Edit permission required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@forms_api_bp.route('/api/item/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """Get item data for editing"""
    category = request.args.get('category', session.get('category', 'trailers'))
    table_name = 'inventory' if category == 'trailers' else category
    
    try:
        conn = sqlite3.connect('inventory.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE id = ? AND (deleted_at IS NULL OR deleted_at = "")', (item_id,))
        item = cursor.fetchone()
        conn.close()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify(dict(item))
    except Exception as e:
        logger.error(f"Error getting item: {e}")
        return jsonify({'error': str(e)}), 500

@forms_api_bp.route('/api/form-options/<category>', methods=['GET'])
@login_required
def get_form_options(category):
    """Get dropdown options for form fields"""
    table_name = 'inventory' if category == 'trailers' else category
    
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        options = {}
        
        if category == 'trailers':
            cursor.execute('SELECT DISTINCT length FROM inventory WHERE length IS NOT NULL ORDER BY length ASC')
            options['lengths'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT make FROM inventory WHERE make IS NOT NULL AND make != "" ORDER BY make ASC')
            options['makes'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT type FROM inventory WHERE type IS NOT NULL AND type != "" ORDER BY type ASC')
            options['types'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT dimensions FROM inventory WHERE dimensions IS NOT NULL AND dimensions != "" ORDER BY dimensions ASC')
            options['dimensions'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT capacity FROM inventory WHERE capacity IS NOT NULL AND capacity != "" ORDER BY capacity ASC')
            options['capacities'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT condition FROM inventory WHERE condition IS NOT NULL AND condition != "" ORDER BY condition ASC')
            options['conditions'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT color FROM inventory WHERE color IS NOT NULL AND color != "" ORDER BY color ASC')
            options['colors'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT hitch_type FROM inventory WHERE hitch_type IS NOT NULL AND hitch_type != "" ORDER BY hitch_type ASC')
            options['hitch_types'] = [row[0] for row in cursor.fetchall()]
            
            options['years'] = list(range(2000, 2051))
            
        elif category == 'trucks':
            cursor.execute('SELECT DISTINCT make FROM trucks WHERE make IS NOT NULL AND make != "" ORDER BY make ASC')
            options['makes'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT model FROM trucks WHERE model IS NOT NULL AND model != "" ORDER BY model ASC')
            options['models'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT engine_type FROM trucks WHERE engine_type IS NOT NULL AND engine_type != "" ORDER BY engine_type ASC')
            options['engine_types'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT truck_type FROM trucks WHERE truck_type IS NOT NULL AND truck_type != "" ORDER BY truck_type ASC')
            options['truck_types'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT condition FROM trucks WHERE condition IS NOT NULL AND condition != "" ORDER BY condition ASC')
            options['conditions'] = [row[0] for row in cursor.fetchall()]
            
            options['years'] = list(range(1990, 2051))
            
        elif category == 'classic_cars':
            cursor.execute('SELECT DISTINCT make FROM classic_cars WHERE make IS NOT NULL AND make != "" ORDER BY make ASC')
            options['makes'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT model FROM classic_cars WHERE model IS NOT NULL AND model != "" ORDER BY model ASC')
            options['models'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT transmission FROM classic_cars WHERE transmission IS NOT NULL AND transmission != "" ORDER BY transmission ASC')
            options['transmissions'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT restoration_status FROM classic_cars WHERE restoration_status IS NOT NULL AND restoration_status != "" ORDER BY restoration_status ASC')
            options['restoration_statuses'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT condition FROM classic_cars WHERE condition IS NOT NULL AND condition != "" ORDER BY condition ASC')
            options['conditions'] = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT DISTINCT color FROM classic_cars WHERE color IS NOT NULL AND color != "" ORDER BY color ASC')
            options['colors'] = [row[0] for row in cursor.fetchall()]
            
            options['years'] = list(range(1900, 2051))
        
        conn.close()
        return jsonify(options)
    except Exception as e:
        logger.error(f"Error getting form options: {e}")
        return jsonify({'error': str(e)}), 500

@forms_api_bp.route('/api/item/add', methods=['POST'])
@login_required
@edit_required
def add_item():
    """Add new item via API"""
    category = session.get('category', 'trailers')
    table_name = 'inventory' if category == 'trailers' else category
    
    try:
        data = request.json
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        if category == 'trailers':
            # Calculate profit
            sell_price = float(data.get('sell_price', 0)) if data.get('sell_price') else None
            purchase_price = float(data.get('purchase_price', 0)) if data.get('purchase_price') else 0.0
            profit = (sell_price - purchase_price) if sell_price is not None else 0.0
            
            cursor.execute('''
                INSERT INTO inventory (length, year, make, type, dimensions, capacity, description, 
                    condition, vin, color, hitch_type, sell_price, sold, 
                    purchase_price, profit, sold_date, date_added, created_at, pictures_taken, facebook_url, facebook_posted_date, google_drive_folder_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
            ''', (
                float(data.get('length')) if data.get('length') else None,
                int(data.get('year')) if data.get('year') else None,
                data.get('make', '').strip(),
                data.get('type', '').strip(),
                data.get('dimensions', '').strip(),
                data.get('capacity', '').strip(),
                data.get('description', '').strip(),
                data.get('condition', '').strip(),
                data.get('vin', '').strip(),
                data.get('color', '').strip(),
                data.get('hitch_type', '').strip(),
                sell_price,
                data.get('sold', 'No'),
                purchase_price,
                profit,
                data.get('sold_date'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('pictures_taken', 'No'),
                data.get('facebook_url', '').strip() if data.get('facebook_url') else None,
                data.get('facebook_posted_date') if data.get('facebook_posted_date') else None,
                data.get('google_drive_folder_id')
            ))
            
        elif category == 'trucks':
            sell_price = float(data.get('sell_price', 0)) if data.get('sell_price') else None
            purchase_price = float(data.get('purchase_price', 0)) if data.get('purchase_price') else 0.0
            profit = (sell_price - purchase_price) if sell_price is not None else 0.0
            
            cursor.execute('''
                INSERT INTO trucks (year, make, model, boom_height, weight_capacity, 
                    engine_type, hours, vin, condition, description, 
                    sell_price, sold, purchase_price, profit, sold_date, 
                    date_added, created_at, pictures_taken, facebook_url, facebook_posted_date,
                    truck_type, mileage, google_drive_folder_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?)
            ''', (
                int(data.get('year')) if data.get('year') else None,
                data.get('make', '').strip(),
                data.get('model', '').strip(),
                float(data.get('boom_height')) if data.get('boom_height') else None,
                float(data.get('weight_capacity')) if data.get('weight_capacity') else None,
                data.get('engine_type', '').strip(),
                int(data.get('hours')) if data.get('hours') else None,
                data.get('vin', '').strip(),
                data.get('condition', '').strip(),
                data.get('description', '').strip(),
                sell_price,
                data.get('sold', 'No'),
                purchase_price,
                profit,
                data.get('sold_date'),
                data.get('date_added'),
                data.get('pictures_taken', 'No'),
                data.get('facebook_url', '').strip(),
                data.get('facebook_posted_date'),
                data.get('truck_type', '').strip(),
                int(data.get('mileage')) if data.get('mileage') else None,
                data.get('google_drive_folder_id')
            ))
            
        elif category == 'classic_cars':
            sell_price = float(data.get('sell_price', 0)) if data.get('sell_price') else None
            purchase_price = float(data.get('purchase_price', 0)) if data.get('purchase_price') else 0.0
            profit = (sell_price - purchase_price) if sell_price is not None else 0.0
            
            cursor.execute('''
                INSERT INTO classic_cars (year, make, model, mileage, engine_specs, transmission, 
                        vin, restoration_status, condition, color, description, 
                        sell_price, sold, purchase_price, profit, sold_date, 
                        date_added, created_at, pictures_taken, facebook_url, facebook_posted_date, google_drive_folder_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?)
            ''', (
                int(data.get('year')) if data.get('year') else None,
                data.get('make', '').strip(),
                data.get('model', '').strip(),
                int(data.get('mileage')) if data.get('mileage') else None,
                data.get('engine_specs', '').strip(),
                data.get('transmission', '').strip(),
                data.get('vin', '').strip(),
                data.get('restoration_status', '').strip(),
                data.get('condition', '').strip(),
                data.get('color', '').strip(),
                data.get('description', '').strip(),
                sell_price,
                data.get('sold', 'No'),
                purchase_price,
                profit,
                data.get('sold_date'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('pictures_taken', 'No'),
                data.get('facebook_url', '').strip() if data.get('facebook_url') else None,
                data.get('facebook_posted_date') if data.get('facebook_posted_date') else None,
                data.get('google_drive_folder_id')
            ))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        # Send email alert
        try:
            from email_service import send_new_item_alert
            send_new_item_alert(data)
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
        
        return jsonify({'success': True, 'id': new_id}), 201
        
    except Exception as e:
        logger.error(f"Error adding item: {e}")
        return jsonify({'error': str(e)}), 500

@forms_api_bp.route('/api/item/<int:item_id>', methods=['PUT'])
@login_required
@edit_required
def update_item(item_id):
    """Update item via API"""
    category = session.get('category', 'trailers')
    table_name = 'inventory' if category == 'trailers' else category
    
    try:
        data = request.json
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        # Get current sold status and folder_id before updating
        cursor.execute(f'SELECT sold, google_drive_folder_id FROM {table_name} WHERE id=?', (item_id,))
        old_data = cursor.fetchone()
        old_sold_status = old_data[0] if old_data else None
        old_folder_id = old_data[1] if old_data else None
        
        if category == 'trailers':
            sell_price = float(data.get('sell_price', 0)) if data.get('sell_price') else None
            purchase_price = float(data.get('purchase_price', 0)) if data.get('purchase_price') else 0.0
            profit = (sell_price - purchase_price) if sell_price is not None else 0.0
            
            cursor.execute('''
                UPDATE inventory 
                SET length=?, year=?, make=?, type=?, dimensions=?, capacity=?, description=?, 
                    condition=?, vin=?, color=?, hitch_type=?, sell_price=?, sold=?, 
                    purchase_price=?, profit=?, sold_date=?, pictures_taken=?, facebook_url=?, facebook_posted_date=?, google_drive_folder_id=?
                WHERE id=?
            ''', (
                float(data.get('length')) if data.get('length') else None,
                int(data.get('year')) if data.get('year') else None,
                data.get('make', '').strip(),
                data.get('type', '').strip(),
                data.get('dimensions', '').strip(),
                data.get('capacity', '').strip(),
                data.get('description', '').strip(),
                data.get('condition', '').strip(),
                data.get('vin', '').strip(),
                data.get('color', '').strip(),
                data.get('hitch_type', '').strip(),
                sell_price,
                data.get('sold', 'No'),
                purchase_price,
                profit,
                data.get('sold_date'),
                data.get('pictures_taken', 'No'),
                data.get('facebook_url', '').strip() if data.get('facebook_url') else None,
                data.get('facebook_posted_date') if data.get('facebook_posted_date') else None,
                data.get('google_drive_folder_id'),
                item_id
            ))
            
        elif category == 'trucks':
            sell_price = float(data.get('sell_price', 0)) if data.get('sell_price') else None
            purchase_price = float(data.get('purchase_price', 0)) if data.get('purchase_price') else 0.0
            profit = (sell_price - purchase_price) if sell_price is not None else 0.0
            
            cursor.execute('''
                UPDATE trucks 
                SET year=?, make=?, model=?, boom_height=?, weight_capacity=?, engine_type=?, 
                    hours=?, vin=?, condition=?, description=?, sell_price=?, sold=?, 
                    purchase_price=?, profit=?, sold_date=?, pictures_taken=?, facebook_url=?, facebook_posted_date=?,
                    truck_type=?, mileage=?, google_drive_folder_id=?
                WHERE id=?
            ''', (
                int(data.get('year')) if data.get('year') else None,
                data.get('make', '').strip(),
                data.get('model', '').strip(),
                float(data.get('boom_height')) if data.get('boom_height') else None,
                float(data.get('weight_capacity')) if data.get('weight_capacity') else None,
                data.get('engine_type', '').strip(),
                int(data.get('hours')) if data.get('hours') else None,
                data.get('vin', '').strip(),
                data.get('condition', '').strip(),
                data.get('description', '').strip(),
                sell_price,
                data.get('sold', 'No'),
                purchase_price,
                profit,
                data.get('sold_date'),
                data.get('pictures_taken', 'No'),
                data.get('facebook_url', '').strip() if data.get('facebook_url') else None,
                data.get('facebook_posted_date') if data.get('facebook_posted_date') else None,
                data.get('truck_type', '').strip(),
                int(data.get('mileage')) if data.get('mileage') else None,
                data.get('google_drive_folder_id'),
                item_id
            ))
            
        elif category == 'classic_cars':
            sell_price = float(data.get('sell_price', 0)) if data.get('sell_price') else None
            purchase_price = float(data.get('purchase_price', 0)) if data.get('purchase_price') else 0.0
            profit = (sell_price - purchase_price) if sell_price is not None else 0.0
            
            cursor.execute('''
                UPDATE classic_cars 
                SET year=?, make=?, model=?, mileage=?, engine_specs=?, transmission=?, vin=?, 
                    restoration_status=?, condition=?, color=?, description=?, sell_price=?, 
                    sold=?, purchase_price=?, profit=?, sold_date=?, pictures_taken=?, facebook_url=?, facebook_posted_date=?, google_drive_folder_id=?
                WHERE id=?
            ''', (
                int(data.get('year')) if data.get('year') else None,
                data.get('make', '').strip(),
                data.get('model', '').strip(),
                int(data.get('mileage')) if data.get('mileage') else None,
                data.get('engine_specs', '').strip(),
                data.get('transmission', '').strip(),
                data.get('vin', '').strip(),
                data.get('restoration_status', '').strip(),
                data.get('condition', '').strip(),
                data.get('color', '').strip(),
                data.get('description', '').strip(),
                sell_price,
                data.get('sold', 'No'),
                purchase_price,
                profit,
                data.get('sold_date'),
                data.get('pictures_taken', 'No'),
                data.get('facebook_url', '').strip() if data.get('facebook_url') else None,
                data.get('facebook_posted_date') if data.get('facebook_posted_date') else None,
                data.get('google_drive_folder_id'),
                item_id
            ))
        
        conn.commit()
       
        # If item was marked as sold and has a Drive folder, move it to archive
        new_sold_status = data.get('sold', 'No')
        
        # Debug output
        # print(f"=== ARCHIVE CHECK ===")
        # print(f"Old status: '{old_sold_status}'")
        # print(f"New status: '{new_sold_status}'")
        # print(f"Folder ID: '{old_folder_id}'")
        # print(f"Comparison: old != 'YES': {old_sold_status != 'YES'}, new == 'YES': {new_sold_status == 'YES'}, has folder: {bool(old_folder_id)}")
        
        if (old_sold_status or '').upper() != 'YES' and (new_sold_status or '').upper() == 'YES' and old_folder_id:
            # print(f">>> CONDITIONS MET - Moving to archive...")
            try:
                service = get_drive_service()
                if service:
                    archive_folder_id = get_or_create_archive_folder(service)
                    # print(f"Archive folder ID: {archive_folder_id}")
                    result = move_folder_to_archive(service, old_folder_id, archive_folder_id)
                    if result:
                        logger.info(f"Moved folder {old_folder_id} to archive for sold item {item_id}")
                        # print(f"SUCCESS: Moved folder {old_folder_id} to archive")
                    # else:
                        # print(f"FAILED: Could not move folder")
                # else:
                    # print("ERROR: Could not get Google Drive service")
            except Exception as e:
                logger.error(f"Error moving folder to archive: {e}")
                # print(f"EXCEPTION: {e}")
        # else:
            # print(f">>> Conditions NOT met - skipping archive")

        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        return jsonify({'error': str(e)}), 500