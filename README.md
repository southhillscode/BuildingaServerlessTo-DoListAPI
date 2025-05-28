# BuildingaServerlessTo-DoListAPI

These are the directions for the Building a Serverless To-Do List API Tutorial.  The Link to the tuturial is as follows:

[Building a Serverless To-Do List API Tutorial](https://docs.google.com/document/d/1gVxsdHtDNNi4dg1WBgLljN4wJqXt3yIehSLfoQZMUZc/edit?usp=sharing)

Though the updated code is here within these files the code on the tutorial might be dated, so use the tutorial, but paste the code from Github.


SHHS CS Final Project 

Building a Serverless To-Do List API Tutorial
This tutorial guides students to create a simple Lambda function, expose it via API Gateway, and store data in S3, all within a Vocareum AWS Academy Learner Lab. It’s designed to minimize IAM issues and can be completed in a short time.


Step 1: Set Up the Vocareum Lab

1.  Log in to Vocareum via the link in your gmail sent to you earlier.
   - Upload the sample code (below) and HTML file to Vocareum or an S3 bucket    accessible to students.
   - Provide instructions via Vocareum lab description.
Step 2: Create the Lambda Function


1.  Access AWS Console :
   - In Vocareum, start the lab and click “AWS Console.”
2.  Create Lambda Function :
   - Navigate to “Lambda” > “Create function.”
   - Choose “Author from scratch,” name it `TodoFunction`, select Python 3.9 runtime,   and use for Execution role - “Use an existing role” and choose “LabRole” in the pull down menu (pre-configured in AWS Academy).
   - Paste this code into `lambda_function.py`:


import json
import boto3

s3 = boto3.client('s3')
BUCKET_NAME = 'YOUR S3 BUCKET NAME HERE'
KEY = 'YOUR .JSON FILE HERE' i.e. (todos.json)

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


3.  Configure S3 Bucket :
   - In the AWS Console, go to “S3” > “Create bucket.”
   - Name it uniquely (e.g., `studentName-todo-123`), disable “Block all public access” for static hosting (see Step 4), and create.
   - Note the bucket name and replace `your-bucket-name` in the code.
   - Instructor: Ensure the bucket’s IAM policy allows `s3:GetObject` and `s3:PutObject` for the Lambda role (Vocareum may pre-configure this).
  

Step 3: Set Up API Gateway



1.  Create API :
   - Go to “API Gateway” > “Create API” > “REST API” > “Build.”
   - Name it `TodoAPI` and create.
2.  Configure Resources :
   - Create a resource named `/todos`.
   - Add methods: `GET` and `POST`, each linked to the `TodoFunction` Lambda function.
   - Enable “Lambda Proxy Integration” for both methods. (Click the button!)
3.  Deploy API :
   - Click “Actions” > “Deploy API,” create a stage (e.g., `prod`), and note the invoke URL (e.g., `https://api-id.execute-api.us-east-1.amazonaws.com/prod/todos`).


Step 4: Host Frontend on S3


1.  Create HTML File :
   - Save this as `index.html`:

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>To-Do List App</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; }
        input { width: 70%; padding: 8px; }
        button { padding: 8px 16px; }
        ul { list-style: none; padding: 0; }
        li { padding: 8px; border-bottom: 1px solid #ddd; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>To-Do List</h1>
    <div>
        <input id="task" type="text" placeholder="Enter task">
        <button onclick="addTask()">Add Task</button>
    </div>
    <p id="error" class="error"></p>
    <ul id="todo-list"></ul>

    <script>
        // Replace with your API Gateway invoke URL
        const apiUrl = 'https://2ns4xpmxcc.execute-api.us-east-1.amazonaws.com/prod/todos'; // e.g., https://api-id.execute-api.us-east-1.amazonaws.com/prod/todos

        // Fetch and display tasks
        async function fetchTodos() {
            try {
                const response = await fetch(apiUrl, { method: 'GET' });
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                const todos = await response.json();
                // Ensure todos is an array
                if (!Array.isArray(todos)) throw new Error('Invalid data: not an array');
                const list = document.getElementById('todo-list');
                if (!list) throw new Error('Element todo-list not found');
                list.innerHTML = todos.map(todo => `<li>${todo.task}</li>`).join('');
                document.getElementById('error').textContent = '';
            } catch (error) {
                console.error('Error fetching todos:', error);
                document.getElementById('error').textContent = 'Failed to load tasks: ' + error.message;
            }
        }

        // Add a new task
        async function addTask() {
            try {
                const task = document.getElementById('task').value.trim();
                if (!task) throw new Error('Task cannot be empty');
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task })
                });
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                document.getElementById('task').value = '';
                await fetchTodos(); // Refresh the list
            } catch (error) {
                console.error('Error adding task:', error);
                document.getElementById('error').textContent = 'Failed to add task: ' + error.message;
            }
        }

        // Run fetchTodos when the page loads
        document.addEventListener('DOMContentLoaded', fetchTodos);
    </script>
</body>
</html>


2.  Upload to S3 :
   - In S3, go to the bucket, enable “Static website hosting,” and set `index.html` as the index document.
   - Upload `index.html`, set permissions to public read. ( Click the box next to index.html and go to → Actions → Make public using ACL.)
   - Get the website URL (e.g., `http://student-todo-123.s3-website-us-east-1.amazonaws.com`).
   - Create/Download the todos.json file from Github or use a text editor with a single   ‘[ ]’ in it (no quotes).  You can also go to the following Github Repository:
Build a Serverless Todo API - Github

Step 5: Test and Submit



1.  Test the App :
   - Open the S3 website URL in a browser.
   - Add tasks and verify they appear in the list.
   - Check S3 to confirm `todos.json` updates.
2.  Deliverables :
   - Submit the API Gateway invoke URL, S3 website URL, and a screenshot of the working app.
   - Cleanup: Delete the Lambda function, API, and S3 bucket to avoid costs.
  Project Timeline (1–2 Weeks)
-  Week 1 :
  - Day 1–2: Watch a short Lambda tutorial (e.g., [AWS Lambda Tutorial For Beginners](https://www.youtube.com/watch?v=3RdzK7M6I2o), ~10 min).
  - Day 3–4: Complete the tutorial above in Vocareum.
  - Day 5: Customize the frontend (e.g., add CSS, delete tasks).
-  Week 2 :
  - Day 1–3: Enhance features (e.g., add error handling, DynamoDB if permitted).
  - Day 4–5: Test, document, and submit the project.  (See Rubric)
