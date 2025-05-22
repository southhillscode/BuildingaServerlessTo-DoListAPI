import json
import boto3
s3 = boto3.client('s3')
BUCKET = 'YOUR_BUCKET_NAME_HER'
KEY = 'todos.json'
def lambda_handler(event, context):
   try:
       # Get todos.json
       try:
           obj = s3.get_object(Bucket=BUCKET, Key=KEY)
           todos = json.loads(obj['Body'].read().decode('utf-8'))
           if not isinstance(todos, list):
               todos = []
               s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(todos))
       except:
           todos = []
           s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(todos))
       # Handle GET or POST
       if event['httpMethod'] == 'POST':
           body = json.loads(event['body'])
           task = body.get('task', '').strip()
           if task:
               todos.append({'id': len(todos) + 1, 'task': task})
               s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(todos))
           return {
               'statusCode': 200,
               'headers': {'Access-Control-Allow-Origin': '*'},
               'body': json.dumps({'message': 'Task added'})
           }
       return {
           'statusCode': 200,
           'headers': {'Access-Control-Allow-Origin': '*'},
           'body': json.dumps(todos)
       }
   except:
       return {
           'statusCode': 200,
           'headers': {'Access-Control-Allow-Origin': '*'},
           'body': json.dumps([])
       }
