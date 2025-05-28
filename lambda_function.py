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
