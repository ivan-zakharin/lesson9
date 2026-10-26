# TODO: написати тодо під RestApi

from flask import Flask, request, abort, jsonify
import sqlite3

app = Flask(__name__)
DB="todo.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

with get_db_connection() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT NOT NULL, 
        done BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    conn.commit()

@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(error):
    return jsonify({'error': error.description}), error.code

@app.route('/todos', methods=['GET'])
def get_todos():
    with get_db_connection() as conn:
        todos = conn.execute('SELECT * FROM todos').fetchall()
    return {'todos': [dict(todo) for todo in todos]}

@app.route('/todos', methods=['POST'])
def create_todo():
    data =  request.get_json(silent=True) or {}
    title = str(data.get('title', '')).strip()
    if not title:
        abort(400, description="Title is required")

    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO todos (title) VALUES (?)', (title,))
        row = conn.execute('SELECT * FROM todos WHERE id = ?', (cursor.lastrowid,)).fetchone()
        if row is None:
            abort(404, description="Todo not found after creation")
    
    return jsonify(dict(row))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')