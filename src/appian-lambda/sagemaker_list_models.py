import boto3

def list_sagemaker_model_registry(prefix):
    sagemaker = boto3.client('sagemaker')
    response = sagemaker.list_models(MaxResults=100)
    models = response.get('Models', [])

    model_info = []
    for model in models:
        model_name = model.get('ModelName')
        creation_time = model.get('CreationTime')

        if model_name.startswith(prefix):
            model_info.append({
                'ModelName': model_name,
                'CreationTime': creation_time.strftime('%Y-%m-%d %H:%M:%S')
            })

    return model_info

def lambda_handler(event, context):
    prefix = event.get('Prefix', '')
    model_info_list = list_sagemaker_model_registry(prefix)
    return {
        'statusCode': 200,
        'body': model_info_list  # Returning the list directly
    }
