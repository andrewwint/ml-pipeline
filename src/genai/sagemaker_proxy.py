import json
import boto3
import csv
import io

def handler(event, context):
    try:
        # Parse request body
        body = json.loads(event['body']) if event.get('body') else {}
        
        # Extract customer features (normalized: Age, Income, Purchases)
        features = body.get('features', [])
        
        if not features or len(features) == 0:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing features array',
                    'example': {'features': [[-1.14, -1.13, 0.68], [-1.67, -0.81, -0.22]]}
                })
            }
        
        # Convert to CSV format for SageMaker
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        for feature_row in features:
            writer.writerow(feature_row)
        csv_data = csv_buffer.getvalue().strip()
        
        # Call SageMaker endpoint
        sagemaker = boto3.client('sagemaker-runtime')
        
        # Find the kmeans endpoint
        sagemaker_client = boto3.client('sagemaker')
        endpoints = sagemaker_client.list_endpoints()['Endpoints']
        kmeans_endpoint = None
        
        for endpoint in endpoints:
            if 'kmeans' in endpoint['EndpointName'].lower():
                kmeans_endpoint = endpoint['EndpointName']
                break
        
        if not kmeans_endpoint:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No K-means endpoint found'})
            }
        
        response = sagemaker.invoke_endpoint(
            EndpointName=kmeans_endpoint,
            ContentType='text/csv',
            Accept='application/json',
            Body=csv_data
        )
        
        result = json.loads(response['Body'].read().decode())
        
        # Add metadata
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'predictions': result.get('predictions', result),
                'endpoint': kmeans_endpoint,
                'model': 'K-means Customer Segmentation',
                'features_processed': len(features)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }