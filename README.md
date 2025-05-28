Serverless To-Do List API
This project is a serverless To-Do List application built for an AP Computer Science course using AWS services. It allows users to add and view tasks via a web interface, implementing CRUD operations (Create and Read) using AWS Lambda, S3, and API Gateway. The project is hosted in AWS Academy Learner Lab (Vocareum, us-east-1) and meets California K–12 Computer Science Standards (9-12.DA.9, Practice 6).
Project Overview

Objective: Create a serverless API to manage a to-do list, storing tasks in todos.json on S3.
Components:
S3 Bucket: fitz-todo-156 stores todos.json (e.g., [{"id":1,"task":"Study"}]) and hosts index.html.
Lambda Function: TodoFunction (Python) handles GET (read tasks) and POST (add tasks).
API Gateway: https://2ns4xpmxcc.execute-api.us-east-1.amazonaws.com/prod/todos routes requests.
Frontend: http://fitz-todo-156.s3-website-us-east-1.amazonaws.com for user interaction.


Technologies: AWS Lambda, S3, API Gateway, Python, JavaScript, HTML/CSS.

Setup Instructions

S3 Bucket:

Create fitz-todo-156 in us-east-1.
Upload todos.json with [] (empty array).
Upload index.html (UI).
Enable static website hosting: http://fitz-todo-156.s3-website-us-east-1.amazonaws.com.
Set bucket policy for public read/write:{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": "arn:aws:s3:::fitz-todo-156/*"
        }
    ]
}




Lambda Function:

Create TodoFunction (Python 3.9).
Deploy lambda_function.py (below).
Set IAM role with s3:GetObject, s3:PutObject, CloudWatch logs.
Timeout: 15s, Memory: 256MB.


API Gateway:

Create REST API, resource /todos.
Add GET/POST methods, link to TodoFunction.
Enable CORS, deploy to prod stage.


Test:

Open http://fitz-todo-156.s3-website-us-east-1.amazonaws.com.
Add task (e.g., “Study”).
Verify todos.json updates: [{"id":1,"task":"Study"}].



Usage

Add Task:
Enter a task (e.g., “Study”) in the UI.
Click “Add Task” or press Enter.
Task appears in the list and saves to todos.json.


View Tasks:
Tasks load on page refresh via GET request.


API:
POST: curl -X POST -H "Content-Type: application/json" -d '{"task":"Study"}' https://2ns4xpmxcc.../prod/todos
GET: curl -X GET https://2ns4xpmxcc.../prod/todos



Lambda Function Code
Below is the lambda_function.py code that powers the To-Do List API. It handles GET (read todos.json) and POST (append tasks to todos.json) requests, with error handling and logging.
import json
import boto3

s3 = boto3.client('s3')
BUCKET_NAME = 'fitz-todo-156'
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

Debugging

Check Logs: AWS CloudWatch (TodoFunction) for Event received, POST task, Wrote to S3.
Verify S3: Download todos.json to confirm tasks (e.g., [{"id":1,"task":"Study"}]).
Network: Browser Inspect > Network for POST/GET requests to https://2ns4xpmxcc....
Errors: Share Console, Network, or CloudWatch logs if tasks don’t save.

Future Enhancements

Add Update/Delete for full CRUD.
Migrate to DynamoDB for scalability.
Enhance UI with task editing/removal.

Credits
Built for AP Computer Science, AWS Academy Learner Lab, May 2025.
