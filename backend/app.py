import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CHEMICALS_DB_PATH = os.path.join(DATA_DIR, 'chemicals.db')
USER_DB_PATH = os.path.join(DATA_DIR, 'user.db')

def get_chemicals_db_connection():
    conn = sqlite3.connect(CHEMICALS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_db_connection():
    # Initialize user.db if it doesn't exist
    if not os.path.exists(USER_DB_PATH):
        init_user_db()
    
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_user_db():
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_id INTEGER NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Ensure user db is initialized on startup
if not os.path.exists(USER_DB_PATH):
    init_user_db()

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'items': [], 'total': 0})

    try:
        conn = get_chemicals_db_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT id, name, synonyms 
            FROM chemicals 
            WHERE name LIKE ? OR synonyms LIKE ?
            LIMIT 500
        """
        search_term = f'%{query}%'
        cursor.execute(sql, (search_term, search_term))
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            items.append({
                'id': row['id'],
                'name': row['name'],
                'synonyms': row['synonyms']
            })
            
        conn.close()
        return jsonify({'items': items, 'total': len(items)})
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'items': [], 'total': 0, 'error': str(e)}), 500

@app.route('/api/chemical/<int:chemical_id>', methods=['GET'])
def get_chemical(chemical_id):
    try:
        conn = get_chemicals_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chemicals WHERE id = ?', (chemical_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Convert Row object to dict
            return jsonify(dict(row))
        else:
            return jsonify(None)
    except Exception as e:
        print(f"Get chemical error: {e}")
        return jsonify(None), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    try:
        conn = get_user_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM favorites ORDER BY added_at DESC')
        rows = cursor.fetchall()
        
        favorites = []
        for row in rows:
            favorites.append({
                'id': row['id'],
                'chemical_id': row['chemical_id'],
                'added_at': row['added_at'],
                'note': row['note']
            })
            
        conn.close()
        return jsonify(favorites)
    except Exception as e:
        print(f"Get favorites error: {e}")
        return jsonify([]), 500

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    try:
        data = request.json
        # Support both snake_case and camelCase
        chemical_id = data.get('chemical_id') or data.get('chemicalId')
        note = data.get('note')
        
        conn = get_user_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO favorites (chemical_id, note) VALUES (?, ?)', (chemical_id, note))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Add favorite error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/favorites/<int:chemical_id>', methods=['DELETE'])
def remove_favorite(chemical_id):
    try:
        conn = get_user_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM favorites WHERE chemical_id = ?', (chemical_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Remove favorite error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
