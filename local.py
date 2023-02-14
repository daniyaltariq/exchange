from lambda_handler import lambda_handler


if __name__ == '__main__':
	print("Lambda function started locally...")
	lambda_handler({}, None)
	print("Lambda function executed successfully!")