import boto3
import json

def lambda_handler(event, context):
    # Extract the ModelName from the event object
    model_name = event.get('ModelName')
    if not model_name:
        return {
            'statusCode': 400,
            'body': json.dumps('ModelName parameter is required')
        }

    # Initialize the SageMaker client
    sagemaker_client = boto3.client('sagemaker')

    try:
        # Delete the SageMaker model
        response = sagemaker_client.delete_model(ModelName=model_name)

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps(f'Model {model_name} deleted successfully.')
        }
    except Exception as e:
        # Handle any errors that occur
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
