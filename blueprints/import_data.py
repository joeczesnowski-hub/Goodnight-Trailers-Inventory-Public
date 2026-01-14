from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
import sqlite3
import pandas as pd
import re
import logging
from datetime import datetime

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
import_bp = Blueprint('import_data', __name__)

def edit_required(f):
    """Decorator to check edit permissions - imported from main app"""
    from functools import wraps
    from flask_login import current_user

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.has_edit_permission():
            flash('You do not have permission to edit inventory')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def cleanup_data(data):
    """
    Automated cleanup function for imported data.
    Handles:
    1. Spelling corrections (ALUIM, ALUMN, ALIUM -> ALUM, BIEGE -> BEIGE, WEILDING/WIELDING -> WELDING)
    2. Space removal with FT (8 FT -> 8FT, 8.FT -> 8FT)
    3. Remove FT from description if length is populated
    4. Remove hitch type keywords from description once hitch_type is filled
    5. Replace H D with HD
    6. Fix number+K spacing (10 K -> 10K)
    7. Uppercase normalization for capacity and dimensions
    8. Consistent terminology standardization
    9. Trailing space removal
    """

    # Fields to clean
    text_fields = ['make', 'type', 'description', 'dimensions', 'capacity', 'color']

    for field in text_fields:
        if field in data and data[field]:
            text = str(data[field])

            # Remove trailing/leading spaces first
            text = text.strip()

            # 1. Fix Aluminum spelling variations to ALUM
            text = re.sub(r'\b(ALUIM|ALUMN|ALIUM)\b', 'ALUM', text, flags=re.IGNORECASE)

            # Fix BEIGE misspelling
            text = re.sub(r'\bBIEGE\b', 'BEIGE', text, flags=re.IGNORECASE)

            # Fix CARGO misspelling
            text = re.sub(r'\bDARGO\b', 'CARGO', text, flags=re.IGNORECASE)

            # Fix WITH misspelling
            text = re.sub(r'\bWUTH\b', 'WITH', text, flags=re.IGNORECASE)

            # Fix welding misspellings
            text = re.sub(r'\b(WEILDING|WIELDING)\b', 'WELDING', text, flags=re.IGNORECASE)

            # 2. Fix FT spacing: "8 FT" -> "8FT", "8.FT" -> "8FT"
            text = re.sub(r'(\d+)\s+FT\b', r'\1FT', text, flags=re.IGNORECASE)
            text = re.sub(r'(\d+)\.FT\b', r'\1FT', text, flags=re.IGNORECASE)

            # Fix K spacing: "10 K" -> "10K"
            text = re.sub(r'(\d+)\s+K\b', r'\1K', text, flags=re.IGNORECASE)

            # 5. Replace "H D" with "HD"
            text = re.sub(r'\bH\s+D\b', 'HD', text, flags=re.IGNORECASE)

            # 8. Consistent terminology standardization
            text = re.sub(r'\bCARHAULER\b', 'CAR HAULER', text, flags=re.IGNORECASE)
            text = re.sub(r'\bDECKOVER\b', 'DECK OVER', text, flags=re.IGNORECASE)
            text = re.sub(r'\bGOOSE\s+NECK\b', 'GOOSENECK', text, flags=re.IGNORECASE)
            text = re.sub(r'\bEQUIP\b', 'EQUIPMENT', text, flags=re.IGNORECASE)

            # Remove trailing spaces again after replacements
            text = text.strip()

            data[field] = text

    # 7. Uppercase normalization for CAPACITY and DIMENSIONS
    if data.get('capacity'):
        data['capacity'] = str(data['capacity']).upper().strip()

    if data.get('dimensions'):
        data['dimensions'] = str(data['dimensions']).upper().strip()

    # 3. Remove FT measurements from description if length column is populated
    if data.get('length') and data.get('description'):
        desc = data['description']
        # Remove patterns like "20FT", "20 FT", "20.FT" from description
        desc = re.sub(r'\b\d+\.?\s*FT\b', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'\s+', ' ', desc).strip()
        data['description'] = desc

    # Remove leading ". " from description
    if data.get('description'):
        desc = data['description']
        if desc.startswith('. '):
            desc = desc[2:].strip()
        data['description'] = desc

    # Remove "TRAILER" from type field
    if data.get('type'):
        type_text = data['type']
        type_text = re.sub(r'\bTRAILER\b', '', type_text, flags=re.IGNORECASE)
        # Clean up extra spaces
        type_text = re.sub(r'\s+', ' ', type_text).strip()
        data['type'] = type_text

    # 4. Remove hitch type keywords from description and type once hitch_type is filled
    if data.get('hitch_type'):
        # List of hitch-related keywords to remove
        hitch_keywords = [
            r'\bGN\b',
            r'\bG/N\b',
            r'\bGOOSENECK\b',
            r'\bGOOSE\s+NECK\b',
            r'\bBP\b',
            r'\bB/P\b',
            r'\bBUMPER\b',
            r'\bBUMPERPULL\b',
            r'\bBUMPER\s+PULL\b',
            r'\bBUMPER-PULL\b'
        ]

        # Clean description
        if data.get('description'):
            desc = data['description']
            for keyword in hitch_keywords:
                desc = re.sub(keyword, '', desc, flags=re.IGNORECASE)
            # Clean up extra spaces and commas
            desc = re.sub(r'\s+', ' ', desc).strip()
            desc = re.sub(r',\s*,', ',', desc)
            desc = re.sub(r'^\s*,\s*', '', desc)
            desc = re.sub(r'\s*,\s*$', '', desc)
            data['description'] = desc

        # Clean type field
        if data.get('type'):
            type_text = data['type']
            for keyword in hitch_keywords:
                type_text = re.sub(keyword, '', type_text, flags=re.IGNORECASE)
            # Clean up extra spaces
            type_text = re.sub(r'\s+', ' ', type_text).strip()
            data['type'] = type_text

    return data

@import_bp.route('/import', methods=['POST'])
@login_required
@edit_required
def import_file():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        flash('Please upload a CSV or XLSX file')
        return redirect(url_for('index'))

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, engine='openpyxl', sheet_name='TRAILERS')

        header_map = {
            'LENGTH': 'length', 'YEAR': 'year', 'MAKE': 'make', 'TYPE': 'type',
            'DIMENSIONS': 'dimensions', 'CAPACITY': 'capacity', 'DESCRIPTION': 'description',
            'CONDITION': 'condition', 'VIN': 'vin', 'COLOR': 'color', 'HITCH_TYPE': 'hitch_type',
            'SELL': 'sell_price', 'SOLD': 'sold', 'PURCHASE': 'purchase_price', 'SOLD_DATE': 'sold_date'
        }
        df = df.rename(columns=header_map)

        df = df[
            (df['make'].notna() & (df['make'].astype(str).str.strip() != '') & (~df['make'].str.lower().str.contains('total', na=False))) &
            (df['vin'].notna() & (df['vin'].astype(str).str.strip() != ''))
        ]

        if df.empty:
            flash('No valid data found in file')
            return redirect(url_for('index'))

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        imported_count = 0
        skipped_count = 0

        for index, row in df.iterrows():
            try:
                length_str = str(row.get('length', '')).strip()
                if not length_str or pd.isna(length_str):
                    skipped_count += 1
                    continue
                length_clean = re.sub(r'[^\d.]', '', length_str)
                if not length_clean or not re.match(r'^\d*\.?\d+$', length_clean):
                    skipped_count += 1
                    continue
                length_float = float(length_clean)

                year_str = str(row.get('year', '')).strip()
                year = None
                if year_str and not pd.isna(year_str):
                    try:
                        year = int(float(year_str))
                    except (ValueError, TypeError):
                        pass

                sell_str = str(row.get('sell_price', '')).strip()
                sell_price = None
                if sell_str and not pd.isna(sell_str):
                    try:
                        sell_price = float(sell_str)
                    except (ValueError, TypeError):
                        pass

                purchase_str = str(row.get('purchase_price', '')).strip()
                purchase_price = 0.0
                if purchase_str and not pd.isna(purchase_str):
                    try:
                        purchase_price = float(purchase_str)
                    except (ValueError, TypeError):
                        pass

                sold_str = str(row.get('sold', '')).strip().upper()
                sold = 'No' if not sold_str or sold_str == 'NAN' or sold_str == '' else sold_str

                sold_date = None
                if 'sold_date' in row and not pd.isna(row['sold_date']):
                    sold_date = str(row['sold_date']).strip()
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', sold_date):
                        sold_date = None

                data = {
                    'length': length_float,
                    'year': year,
                    'make': str(row.get('make', '')).strip(),
                    'type': str(row.get('type', '')).strip(),
                    'dimensions': str(row.get('dimensions', '')).strip(),
                    'capacity': str(row.get('capacity', '')).strip(),
                    'description': str(row.get('description', '')).strip(),
                    'condition': str(row.get('condition', '')).strip(),
                    'vin': str(row.get('vin', '')).strip(),
                    'color': str(row.get('color', '')).strip(),
                    'hitch_type': str(row.get('hitch_type', '')).strip(),
                    'sell_price': sell_price,
                    'sold': sold,
                    'purchase_price': purchase_price,
                    'sold_date': sold_date
                }
                data['profit'] = (data['sell_price'] - data['purchase_price']) if data['sell_price'] is not None else 0.0

                # Auto-populate hitch_type if not provided
                hitch_type = data.get('hitch_type', '').strip()
                if not hitch_type:
                    type_field = data.get('type', '').upper()
                    desc_field = data.get('description', '').upper()
                    if any(indicator in type_field for indicator in ['GOOSENECK', 'GOOSE NECK', 'GN', 'G/N']) or \
                       any(indicator in desc_field for indicator in ['GOOSENECK', 'GOOSE NECK', 'GN', 'G/N']):
                        hitch_type = 'Gooseneck'
                    elif any(indicator in type_field for indicator in ['BP', 'BUMPERPULL', 'BUMPER PULL', 'BUMPER-PULL', 'B/P']) or \
                         any(indicator in desc_field for indicator in ['BP', 'BUMPERPULL', 'BUMPER PULL', 'B/P']):
                        hitch_type = 'Bumper-pull'
                    else:
                        hitch_type = 'Bumper-pull'
                    data['hitch_type'] = hitch_type

                # APPLY AUTOMATED CLEANUP
                data = cleanup_data(data)

                cursor.execute('SELECT id FROM inventory WHERE vin = ?', (data['vin'],))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute('''
                        UPDATE inventory SET length=?, year=?, make=?, type=?, dimensions=?, capacity=?, description=?, condition=?, vin=?, color=?, hitch_type=?, sell_price=?, sold=?, purchase_price=?, profit=?, sold_date=?
                        WHERE id=?
                    ''', (data['length'], data['year'], data['make'], data['type'], data['dimensions'], data['capacity'], data['description'], data['condition'], data['vin'], data['color'], data['hitch_type'], data['sell_price'], data['sold'], data['purchase_price'], data['profit'], data['sold_date'], existing[0]))
                else:
                    cursor.execute('''
                        INSERT INTO inventory (length, year, make, type, dimensions, capacity, description, condition, vin, color, hitch_type, sell_price, sold, purchase_price, profit, sold_date, date_added)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (data['length'], data['year'], data['make'], data['type'], data['dimensions'], data['capacity'], data['description'], data['condition'], data['vin'], data['color'], data['hitch_type'], data['sell_price'], data['sold'], data['purchase_price'], data['profit'], data['sold_date'], datetime.now().strftime('%Y-%m-%d')))

                imported_count += 1

            except Exception as e:
                logger.error(f"Error processing row {index}: {e}")
                skipped_count += 1
                continue

        conn.commit()
        conn.close()

        flash(f'Successfully imported {imported_count} items. Skipped {skipped_count} invalid rows.')
    except Exception as e:
        logger.error(f"Error importing file: {e}")
        flash(f'Error importing file: {str(e)}')

    return redirect(url_for('index'))