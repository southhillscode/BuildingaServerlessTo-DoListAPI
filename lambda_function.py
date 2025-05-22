
import json
import boto3

s3 = boto3.client('s3')
BUCKET = 'your-bucket-name'  # Get this from your S3 bucket
KEY = 'todos.json'

def lambda_handler(event, context):
    http_method = event['httpMethod']
    try:
        # Get existing todos
        try:
            obj = s3.get_object(Bucket=BUCKET, Key=KEY)
            todos = json.loads(obj['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            todos = []

        if http_method == 'POST':
            body = json.loads(event['body'])
            todos.append({'id': len(todos) + 1, 'task': body['task']})
            s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(todos))
            return {'statusCode': 200, 'body': json.dumps({'message': 'Task added'})}
        elif http_method == 'GET':
            return {'statusCode': 200, 'body': json.dumps(todos)}
        else:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid method'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
