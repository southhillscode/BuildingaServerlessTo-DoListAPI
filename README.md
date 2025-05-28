# Serverless To-Do List API

This project is a serverless To-Do List application developed for an AP Computer Science course using AWS services. It enables users to add and view tasks through a web interface, implementing **CRUD** operations (Create via POST, Read via GET) using AWS Lambda, S3, and API Gateway. Hosted in AWS Academy Learner Lab (Vocareum, `us-east-1`), it aligns with California K–12 Computer Science Standards (9-12.DA.9 for data management, Practice 6 for testing, Practice 7 for communication).

## Project Overview

- **Objective**: Build a serverless API to manage a to-do list, storing tasks in `todos.json` on S3.
- **Components**:
  - **S3 Bucket**: `YOUR BUCKET NAME HERE` hosts `index.html` (UI) and stores `todos.json` (e.g., `[{"id":1,"task":"Study"}]`).
  - **Lambda Function**: `TodoFunction` (Python) handles GET (read tasks) and POST (add tasks).
  - **API Gateway**: Routes requests at `https://YOUR_API_URL.execute-api.us-east-1.amazonaws.com/prod/todos`.
  - **Frontend**: Accessible at `https://fitz-todo-156.s3.us-east-1.amazonaws.com/index.html`.
- **Technologies**: AWS Lambda, S3, API Gateway, Python, JavaScript, HTML/CSS.

## Setup Instructions

1. **S3 Bucket**:
   - Create bucket `fitz-todo-156` in `us-east-1`.
   - Upload `todos.json` with `[]` (empty array).
   - Upload `index.html` for the UI.
   - Enable static website hosting: `http://fitz-todo-156.s3-website-us-east-1.amazonaws.com`.
   - Set bucket policy for public read/write:
     ```json
     {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Effect": "Allow",
                 "Principal": "*",
                 "Action": ["s3:GetObject", "s3:PutObject"],
                 "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME_HERE/*"
             }
         ]
     }
     ```

2. **Lambda Function**:
   - Create `TodoFunction` (Python 3.9).
   - Deploy `lambda_function.py` (see below).
   - Assign IAM role with `s3:GetObject`, `s3:PutObject`, and CloudWatch logs permissions.
   - Set timeout: 15 seconds, memory: 256 MB.

3. **API Gateway**:
   - Create REST API with `/todos` resource.
   - Add GET and POST methods, linked to `TodoFunction`.
   - Enable CORS and deploy to `prod` stage.

4. **Test**:
   - Visit `http://fitz-todo-156.s3-website-us-east-1.amazonaws.com`.
   - Add a task (e.g., “Study”).
   - Verify `todos.json` updates in S3: `[{"id":1,"task":"Study"}]`.

## Usage

- **Add Task**:
  - Enter a task (e.g., “Study”) in the UI input field.
  - Click “Add Task” or press Enter.
  - Task appears in the list and saves to `todos.json`.
- **View Tasks**:
  - Tasks load automatically on page load via GET request.
  - Refresh to confirm persistence.
- **API Endpoints**:
  - **POST**: Add task
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"task":"Study"}' https://YOUR_API_URL.execute-api.us-east-1.amazonaws.com/prod/todos
    ```
    Response: `{"message": "Task added"}`
  - **GET**: List tasks
    ```bash
    curl -X GET https://2ns4xpmxcc.execute-api.us-east-1.amazonaws.com/prod/todos
    ```
    Response: `[{"id":1,"task":"Study"}]`

## Project Files

Below are the core files for the project, including the Lambda function (`lambda_function.py`), frontend (`index.html`), and data store (`todos.json`).

### Lambda Function: `lambda_function.py`

This Python script runs in AWS Lambda, handling GET (read `todos.json`) and POST (append tasks to `todos.json`) requests with error handling and logging.

```python
import json
import boto3

s3 = boto3.client('s3')
BUCKET_NAME = 'YOUR BUCKET NAME HERE'
KEY = 'todos.json'

def lambda_handler(event, context):
    print(f"Event received: {json.dumps(event)}")
    try:
        # Load todos.json
        try:
            print(f"Reading s3://{BUCKET_NAME}/{KEY}")
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=KEY)
            content = obj['Body'].read().decode('utf-8')
            print(f"Raw content: {content}")
            tasks = json.loads(content)
            print(f"Parsed tasks: {tasks}")
            if not isinstance(tasks, list):
                print("Invalid tasks (not a list), resetting to []")
                tasks = []
                s3.put_object(Bucket=BUCKET_NAME, Key=KEY, Body=json.dumps(tasks))
        except s3.exceptions.NoSuchKey:
            print("No todos.json, creating []")
            tasks = []
            s3.put_object(Bucket=BUCKET_NAME, Key=KEY, Body=json.dumps(tasks))
        except json.JSONDecodeError as e:
            print(f"Corrupted todos.json: {str(e)}")
            tasks = []
            s3.put_object(Bucket=BUCKET_NAME, Key=KEY, Body=json.dumps(tasks))
        except Exception as e:
            print(f"Error reading todos.json: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'},
                'body': json.dumps({'error': 'Failed to read tasks'})
            }

        # Handle GET or POST
        if event.get('httpMethod') == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
                task = body.get('task', '').strip()
                print(f"POST task: {task}")
                if task:
                    new_todo = {'id': len(tasks) + 1, 'task': task}
                    tasks.append(new_todo)
                    print(f"Writing tasks: {tasks}")
                    s3.put_object(Bucket=BUCKET_NAME, Key=KEY, Body=json.dumps(tasks))
                    print("Wrote to S3")
                    return {
                        'statusCode': 200,
                        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'},
                        'body': json.dumps({'message': 'Task added'})
                    }
                print("Empty task, skipping")
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'},
                    'body': json.dumps({'error': 'Task cannot be empty'})
                }
            except json.JSONDecodeError as e:
                print(f"Invalid POST body: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'},
                    'body': json.dumps({'error': 'Invalid task data'})
                }
        print(f"Returning tasks for GET: {tasks}")
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'},
            'body': json.dumps(tasks)
        }
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'},
            'body': json.dumps({'error': 'Server error'})
        }
```

### Frontend: `index.html`

This HTML file provides the user interface, with JavaScript to fetch tasks (GET) and add tasks (POST) via the API Gateway.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Serverless To-Do List</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 0 20px; background-color: #f4f4f9; }
        h1 { text-align: center; color: #333; }
        .todo-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input { padding: 10px; width: calc(100% - 90px); margin-right: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 15px; border: none; border-radius: 4px; background-color: #28a745; color: white; cursor: pointer; }
        button:hover { background-color: #218838; }
        ul { list-style: none; padding: 0; }
        li { padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; }
        #error { color: red; margin-top: 10px; text-align: center; }
    </style>
</head>
<body>
    <h1>Serverless To-Do List</h1>
    <div class="todo-container">
        <input type="text" id="taskInput" placeholder="Enter a task">
        <button id="addButton">Add Task</button>
        <ul id="todo-list"></ul>
        <div id="error"></div>
    </div>
    <script>
        const apiUrl = 'https://YOUR_API_URL_HERE.execute-api.us-east-1.amazonaws.com/prod/todos';
        async function fetchTodos() {
            try {
                console.log('Fetching todos...');
                const response = await fetch(apiUrl, { method: 'GET' });
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                const todos = await response.json();
                console.log('Todos:', todos);
                if (!Array.isArray(todos)) throw new Error('Invalid data: not an array');
                const list = document.getElementById('todo-list');
                list.innerHTML = todos.map(todo => `<li>${todo.task}</li>`).join('');
                document.getElementById('error').textContent = '';
            } catch (error) {
                console.error('Error fetching todos:', error);
                document.getElementById('error').textContent = 'Failed to load tasks: ' + error.message;
            }
        }
        async function addTask() {
            try {
                const input = document.getElementById('taskInput');
                const task = input.value.trim();
                console.log('Adding task:', task);
                if (!task) {
                    document.getElementById('error').textContent = 'Please enter a task!';
                    return;
                }
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task })
                });
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                const result = await response.json();
                console.log('Add task response:', result);
                document.getElementById('error').textContent = '';
                input.value = '';
                fetchTodos();
            } catch (error) {
                console.error('Error adding task:', error);
                document.getElementById('error').textContent = 'Failed to add task: ' + error.message;
            }
        }
        document.getElementById('addButton').addEventListener('click', addTask);
        document.getElementById('taskInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') addTask();
        });
        document.addEventListener('DOMContentLoaded', fetchTodos);
    </script>
</body>
</html>
```

### Data Store: `todos.json`

This JSON file stores tasks in the S3 bucket. It starts empty (`[]`) and updates with tasks (e.g., `[{"id":1,"task":"Study"}]`).

```json
[]
```

## Debugging

- **CloudWatch Logs**: Check `TodoFunction` logs for `Event received`, `POST task`, `Wrote to S3`.
- **S3 Verification**: Download `todos.json` to confirm tasks.
- **Browser Debugging**:
  - Open `http://fitz-todo-156.s3-website-us-east-1.amazonaws.com`.
  - Use **Inspect** > **Network** for POST/GET requests.
  - Check **Console** for errors (e.g., `Failed to add task`).
- **Errors**: If tasks don’t save, share:
  - **Console** logs.
  - **Network** request details.
  - **CloudWatch** logs.
  - `curl` output:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"task":"Study"}' https://2ns4xpmxcc.execute-api.us-east-1.amazonaws.com/prod/todos
    ```

## Future Enhancements

- Implement **Update/Delete** for full CRUD.
- Migrate to DynamoDB for a database solution.
- Add UI features: task editing, deletion, or completion status.

- Rubric
https://docs.google.com/spreadsheets/d/18Q2R6rLxSuhKwwS74nWeBjRCgr-1wO8g11FcFPzwHXk/edit?usp=sharing

## Credits

Developed for AP Computer Science, AWS Academy Learner Lab, May 2025.
