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

def sort_by_date(tasks, order):
    if not tasks:
        return []
    def get_date(task):
        try:
            return datetime.strptime(task['created_at'],'%H:%M %d.%m.%Y')
        except:
            return datetime.min
    return sorted(tasks, key=get_date, reverse=(order == 'desc'))

def sort_by_alphabet(tasks, order):
    if not tasks:
        return []
    return sorted(tasks, key=lambda x: x['title'].lower(), reverse=(order=='desc'))

def sort_tasks_priority(tasks, order):
    if not tasks:
        return []
    high=[]
    medium=[]
    low=[]

    for task in tasks:
        priority=task.get('priority','medium')

        if priority=='high':
            high.append(task)
        elif priority=='medium':
            medium.append(task)
        else:
            low.append(task)
    if order=='desc':
        return high+medium+low
    else:
        return low + medium + high

def sorted_tasks(tasks, sort_type, sort_order):
    if not tasks:
        return []
    if sort_type == 'priority':
        tasks = sort_tasks_priority(tasks, sort_order)
    elif sort_type == 'date':
        tasks = sort_by_date(tasks, sort_order)
    elif sort_type == 'alphabet':
        tasks = sort_by_alphabet(tasks, sort_order)

    return tasks

@app.route('/')
def index():
    tasks = load_tasks()
    filter_type = request.args.get('filter','all')
    sort_type = request.args.get('sort', 'priority')
    sort_order = request.args.get('order', 'desc')

    tasks = sorted_tasks(tasks, sort_type, sort_order)

    filtered_tasks = tasks

    if filter_type == 'active':
        filtered_tasks = [task for task in tasks if task['completed']==False]
    elif filter_type == 'completed':
        filtered_tasks = [task for task in tasks if task['completed']==True]

    return render_template('index.html', tasks=filtered_tasks, all_tasks=tasks, filter=filter_type, sort=sort_type, order=sort_order)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    filter_type = request.form.get('filter','all')
    priority = request.form.get('priority','medium')

    if not title:
        return redirect(url_for('index',filter=filter_type))

    tasks = load_tasks()

    new_task = {
        'id': len(tasks) + 1 if tasks else 1,
        'title': title,
        'completed': False,
        'created_at': datetime.now().strftime('%H:%M %d.%m.%Y'),
        'priority': priority
    }

    tasks.append(new_task)
    sort_type = request.form.get('sort', 'priority')
    sort_order = request.form.get('order', 'desc')

    tasks = sorted_tasks(tasks, sort_type, sort_order)
    save_tasks(tasks)

    return redirect(url_for('index', filter=filter_type, sort=sort_type, order=sort_order))

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

    filter_type = request.args.get('filter', 'all')

    sort_type = request.args.get('sort', 'priority')
    sort_order = request.args.get('order', 'desc')

    tasks = sorted_tasks(tasks, sort_type, sort_order)
    save_tasks(tasks)
    return redirect(url_for('index', filter=filter_type, sort=sort_type, order=sort_order))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):

    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]

    filter_type = request.args.get('filter', 'all')

    sort_type = request.args.get('sort', 'priority')
    sort_order = request.args.get('order', 'desc')

    tasks = sorted_tasks(tasks, sort_type, sort_order)
    save_tasks(tasks)
    return redirect(url_for('index', filter=filter_type, sort=sort_type, order=sort_order))

@app.route ('/api/tasks')
def api_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port = 5000)