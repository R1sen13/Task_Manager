import json
import os
from flask import Flask, render_template, request, url_for, jsonify
from werkzeug.utils import redirect
from datetime import datetime

app = Flask(__name__)

TASK_FILE = 'task.json'

def load_tasks():
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error: {e}")
            return []
    return  []

def save_tasks(tasks):
    try:
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error: {e}")
        return False

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()

    if not title:
        return redirect(url_for('index'))

    tasks = load_tasks()

    new_task = {
        'id': len(tasks) + 1 if tasks else 1,
        'title': title,
        'completed': False,
        'created_at': datetime.now().strftime('%d.%m.%Y %H:%M')
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):

    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]

    for i, task in enumerate(tasks,1):
        task['id'] = i

    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route ('/api/tasks')
def api_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port = 5000)