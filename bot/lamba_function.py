import boto3
import json

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
table = dynamodb.Table("chat_history")

def lambda_handler(event, context):
    user_id = event["user_id"]
    message = event["message"]
    response = event["response"]

    # Save to DynamoDB
    table.put_item(
        Item={
            "user_id": user_id,
            "message": message,
            "response": response
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Data saved successfully")
    }
