from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import sqlite3
import logging

logger = logging.getLogger(__name__)

inventory_api_bp = Blueprint('inventory_api', __name__)

def get_db_connection(category='trailers'):
    """Get database connection for the specified category"""
    table_map = {
        'trailers': 'inventory',
        'trucks': 'trucks',
        'classic_cars': 'classic_cars'
    }
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn, table_map.get(category, 'inventory')

@inventory_api_bp.route('/api/inventory/<category>', methods=['GET'])
def get_inventory(category):
    """Get all inventory items for a category"""
    try:
        conn, table_name = get_db_connection(category)
        cursor = conn.cursor()
        
        # Get sold filter from query params
        sold_filter = request.args.get('sold', 'all')
        
        # UPDATED: Exclude deleted items
        if sold_filter == 'unsold':
            cursor.execute(f'SELECT * FROM {table_name} WHERE (sold = "No" OR sold = "no") AND deleted_at IS NULL')
        elif sold_filter == 'sold':
            cursor.execute(f'SELECT * FROM {table_name} WHERE (sold = "YES" OR sold = "yes") AND deleted_at IS NULL')
        else:
            cursor.execute(f'SELECT * FROM {table_name} WHERE deleted_at IS NULL')
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_api_bp.route('/api/inventory/summary/<category>', methods=['GET'])
@login_required
def get_summary(category):
    """Get summary statistics for a category"""
    if not current_user.has_summary_permission():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        conn, table_name = get_db_connection(category)
        cursor = conn.cursor()
        
        # Unsold summary - EXCLUDE DELETED
        cursor.execute(f'''
            SELECT 
                SUM(sell_price) as sell_total,
                SUM(purchase_price) as purchase_total,
                SUM(profit) as profit_total
            FROM {table_name}
            WHERE sold = 'No'
            AND deleted_at IS NULL
        ''')
        unsold = dict(cursor.fetchone())

        # Sold summary - EXCLUDE DELETED
        cursor.execute(f'''
            SELECT 
                SUM(sell_price) as sell_total,
                SUM(purchase_price) as purchase_total,
                SUM(profit) as profit_total
            FROM {table_name}
            WHERE sold = 'Yes'
            AND deleted_at IS NULL
        ''')
        sold = dict(cursor.fetchone())
        
        conn.close()
        
        return jsonify({
            'unsold': unsold,
            'sold': sold
        })
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_api_bp.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Soft delete a single item"""
    if not current_user.has_delete_permission():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        category = request.args.get('category', 'trailers')
        conn, table_name = get_db_connection(category)
        cursor = conn.cursor()
        # Soft delete - mark as deleted
        cursor.execute(f'UPDATE {table_name} SET deleted_at = datetime("now") WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_api_bp.route('/api/inventory/bulk-delete', methods=['POST'])
@login_required
def bulk_delete():
    """Soft delete multiple items"""
    if not current_user.has_delete_permission():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        item_ids = data.get('ids', [])
        category = data.get('category', 'trailers')
        
        conn, table_name = get_db_connection(category)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(item_ids))
        # Soft delete - mark as deleted
        cursor.execute(f'UPDATE {table_name} SET deleted_at = datetime("now") WHERE id IN ({placeholders})', item_ids)
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'deleted': len(item_ids)})
    except Exception as e:
        logger.error(f"Error bulk deleting: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_api_bp.route('/api/inventory/bulk-mark-sold', methods=['POST'])
@login_required
def bulk_mark_sold():
    """Mark multiple items as sold"""
    try:
        data = request.json
        item_ids = data.get('ids', [])
        category = data.get('category', 'trailers')
        sold_date = data.get('sold_date')
        
        conn, table_name = get_db_connection(category)
        cursor = conn.cursor()
        
        # Get folder IDs before updating (for archive)
        placeholders = ','.join('?' * len(item_ids))
        cursor.execute(f'SELECT id, google_drive_folder_id FROM {table_name} WHERE id IN ({placeholders})', item_ids)
        items_with_folders = cursor.fetchall()
        
        # Update items to sold
        cursor.execute(f'''
            UPDATE {table_name} 
            SET sold = "YES", sold_date = ? 
            WHERE id IN ({placeholders})
        ''', [sold_date] + item_ids)
        
        conn.commit()
        
        # Move folders to archive
        from google_drive_service import get_drive_service, move_folder_to_archive, get_or_create_archive_folder
        try:
            service = get_drive_service()
            if service:
                archive_folder_id = get_or_create_archive_folder(service)
                for row in items_with_folders:
                    folder_id = row['google_drive_folder_id'] if isinstance(row, dict) else row[1]
                    if folder_id:
                        move_folder_to_archive(service, folder_id, archive_folder_id)
                        logger.info(f"Moved folder {folder_id} to archive (bulk sold)")
        except Exception as e:
            logger.error(f"Error moving folders to archive: {e}")
        
        # Send email notifications for each sold item
        for item_id in item_ids:
            cursor.execute(f'SELECT * FROM {table_name} WHERE id = ?', (item_id,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            if row:
                item_data = dict(zip(columns, row))
                from email_service import send_item_sold_alert
                send_item_sold_alert(item_data)
        
        conn.close()
        
        return jsonify({'success': True, 'updated': len(item_ids)})
    except Exception as e:
        logger.error(f"Error marking sold: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_api_bp.route('/api/inventory/bulk-mark-unsold', methods=['POST'])
@login_required
def bulk_mark_unsold():
    """Mark multiple items as unsold"""
    try:
        data = request.json
        item_ids = data.get('ids', [])
        category = data.get('category', 'trailers')
        
        # print(f"=== BULK MARK UNSOLD ===")
        # print(f"Item IDs: {item_ids}")
        # print(f"Category: {category}")
        
        conn, table_name = get_db_connection(category)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(item_ids))
        # query = f'UPDATE {table_name} SET sold = "No", sold_date = NULL WHERE id IN ({placeholders})'
        # print(f"Query: {query}")
        # print(f"Values: {item_ids}")
        
        cursor.execute(f'UPDATE {table_name} SET sold = "No", sold_date = NULL WHERE id IN ({placeholders})', item_ids)
        # rows_affected = cursor.rowcount
        # print(f"Rows affected: {rows_affected}")
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'updated': len(item_ids)})
    except Exception as e:
        logger.error(f"Error marking unsold: {e}")
        return jsonify({'error': str(e)}), 500
    
@inventory_api_bp.route('/api/inventory/bulk-edit', methods=['POST'])
@login_required
def bulk_edit():
    """Update multiple items with specified fields"""
    try:
        data = request.json
        item_ids = data.get('ids', [])
        category = data.get('category', 'trailers')
        updates = data.get('updates', {})
        
        if not item_ids or not updates:
            return jsonify({'error': 'No items or updates provided'}), 400
        
        table_name = 'inventory' if category == 'trailers' else category
        
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query based on provided fields
        set_clauses = []
        values = []
        
        if 'sold' in updates:
            set_clauses.append('sold = ?')
            values.append(updates['sold'])
        
        if 'sold_date' in updates:
            set_clauses.append('sold_date = ?')
            values.append(updates['sold_date'])
        
        if 'pictures_taken' in updates:
            set_clauses.append('pictures_taken = ?')
            values.append(updates['pictures_taken'])
        
        if 'facebook_posted_date' in updates:
            set_clauses.append('facebook_posted_date = ?')
            values.append(updates['facebook_posted_date'])
        
        if not set_clauses:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add IDs to values
        placeholders = ','.join('?' * len(item_ids))
        values.extend(item_ids)
        
        query = f'''
            UPDATE {table_name} 
            SET {', '.join(set_clauses)}
            WHERE id IN ({placeholders})
        '''
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'updated': len(item_ids)})
    except Exception as e:
        logger.error(f"Error in bulk edit: {e}")
        return jsonify({'error': str(e)}), 500