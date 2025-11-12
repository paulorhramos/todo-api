from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'tododb'),
    'user': os.getenv('DB_USER', 'todouser'),
    'password': os.getenv('DB_PASSWORD', 'todopass123')
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialize database table"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, title, description, completed, created_at, updated_at FROM todos ORDER BY created_at DESC')
        todos = []
        for row in cur.fetchall():
            todos.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'completed': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None
            })
        cur.close()
        conn.close()
        return jsonify(todos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create new todo"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO todos (title, description) VALUES (%s, %s) RETURNING id',
            (title, description)
        )
        todo_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': todo_id, 'message': 'Todo created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update todo"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        completed = data.get('completed')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = %s')
            params.append(title)
        if description is not None:
            updates.append('description = %s')
            params.append(description)
        if completed is not None:
            updates.append('completed = %s')
            params.append(completed)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(todo_id)
        
        query = f"UPDATE todos SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, params)
        
        if cur.rowcount == 0:
            return jsonify({'error': 'Todo not found'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Todo updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete todo"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
        
        if cur.rowcount == 0:
            return jsonify({'error': 'Todo not found'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Todo deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """API info"""
    return jsonify({
        'name': 'Todo API',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /api/todos': 'Get all todos',
            'POST /api/todos': 'Create todo',
            'PUT /api/todos/:id': 'Update todo',
            'DELETE /api/todos/:id': 'Delete todo'
        }
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
