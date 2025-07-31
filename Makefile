.PHONY: help install deploy destroy clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install          - Install dependencies"
	@echo "  validate         - Validate CloudFormation template"
	@echo "  deploy           - Deploy complete infrastructure (IaC)"
	@echo "  update-lambda    - Update Lambda function code only"
	@echo "  update-sagemaker-proxy - Update SageMaker proxy Lambda"
	@echo "  test-api         - Test Customer Insights API"
	@echo "  test-sagemaker   - Test SageMaker K-means endpoint"
	@echo "  get-api-url      - Get GenAI API endpoint"
	@echo "  get-sagemaker-api-url - Get SageMaker API endpoint"
	@echo "  get-endpoints    - List SageMaker model endpoints"
	@echo "  get-model-artifacts - Show model artifacts in S3"
	@echo "  status           - Check deployment status"
	@echo "  start-notebook   - Start SageMaker notebook instance"
	@echo "  stop-notebook    - Stop SageMaker notebook instance"
	@echo "  destroy          - Tear down all resources"
	@echo "  force-destroy    - Force delete stack (empty S3 buckets first)"
	@echo "  clean            - Clean up temporary files"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Validate CloudFormation template
validate:
	@echo "Validating CloudFormation template..."
	aws cloudformation validate-template \
		--template-body file://infrastructure/cloudformation-complete.yaml
	@echo "✅ Template validation successful!"

# Deploy complete infrastructure (IaC)
deploy: validate
	@echo "Deploying complete infrastructure with CloudFormation..."
	aws cloudformation deploy \
		--template-file infrastructure/cloudformation-complete.yaml \
		--stack-name ml-pipeline-stack \
		--capabilities CAPABILITY_NAMED_IAM
	@echo "Updating Lambda function with latest code..."
	@$(MAKE) update-lambda
	@echo "Getting stack outputs..."
	aws cloudformation describe-stacks \
		--stack-name ml-pipeline-stack \
		--query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
		--output table

# Clean up existing Lambda function (for CloudFormation deployment)
cleanup-lambda:
	@echo "🧹 Cleaning up existing Lambda function..."
	-aws lambda delete-function --function-name ml-pipeline-genai-insights-dev 2>/dev/null || true

# Package Lambda for deployment
package-lambda:
	@echo "📦 Packaging Lambda function..."
	python scripts/deploy_lambda.py --keep-zip --package-only
	@echo "📤 Uploading package to S3..."
	@if aws cloudformation describe-stacks --stack-name ml-pipeline-stack >/dev/null 2>&1; then \
		MODEL_BUCKET=$$(aws cloudformation describe-stacks --stack-name ml-pipeline-stack --query 'Stacks[0].Outputs[?OutputKey==`ModelBucketName`].OutputValue' --output text); \
		aws s3 cp lambda_packages/genai-insights.zip s3://$$MODEL_BUCKET/lambda/genai-insights.zip; \
	else \
		echo "Stack doesn't exist yet - CloudFormation will handle S3 upload"; \
	fi

# Destroy infrastructure
destroy:
	@echo "Destroying infrastructure..."
	aws cloudformation delete-stack --stack-name ml-pipeline-stack
	@echo "Waiting for stack deletion..."
	-aws cloudformation wait stack-delete-complete --stack-name ml-pipeline-stack

# Force destroy - comprehensive cleanup
force-destroy: clean-buckets
	@echo "Force destroying infrastructure..."
	@echo "Deleting CloudFormation stack..."
	-aws cloudformation delete-stack --stack-name ml-pipeline-stack
	@echo "Waiting for stack deletion..."
	-aws cloudformation wait stack-delete-complete --stack-name ml-pipeline-stack
	@echo "Final cleanup of any remaining buckets..."
	@$(MAKE) clean-buckets

# Clean up orphaned S3 buckets
clean-buckets:
	@echo "Cleaning up orphaned S3 buckets..."
	@echo "Finding ml-pipeline buckets..."
	@aws s3api list-buckets --query "Buckets[?contains(Name, 'ml-pipeline-') && contains(Name, '790768631355')].Name" --output text | while read bucket; do \
		if [ ! -z "$$bucket" ]; then \
			echo "Processing bucket: $$bucket"; \
			echo "Removing all objects and versions..."; \
			aws s3api delete-objects --bucket $$bucket --delete "$$(aws s3api list-object-versions --bucket $$bucket --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json)" 2>/dev/null || true; \
			aws s3api delete-objects --bucket $$bucket --delete "$$(aws s3api list-object-versions --bucket $$bucket --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' --output json)" 2>/dev/null || true; \
			echo "Deleting bucket: $$bucket"; \
			aws s3 rb s3://$$bucket --force; \
		fi; \
	done
	@echo "S3 cleanup complete!"



# Clean temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	rm -rf .coverage htmlcov/
	rm -rf models/*.pkl



# Get stack status
status:
	@echo "Checking stack status..."
	aws cloudformation describe-stacks \
		--stack-name ml-pipeline-stack \
		--query 'Stacks[0].{Status:StackStatus,Created:CreationTime}' \
		--output table

# Get API URL for testing
get-api-url:
	@aws cloudformation describe-stacks \
		--stack-name ml-pipeline-stack \
		--query 'Stacks[0].Outputs[?OutputKey==`GenAIApiUrl`].OutputValue' \
		--output text

# Get SageMaker API URL
get-sagemaker-api-url:
	@aws cloudformation describe-stacks \
		--stack-name ml-pipeline-stack \
		--query 'Stacks[0].Outputs[?OutputKey==`SageMakerApiUrl`].OutputValue' \
		--output text

# Get SageMaker model endpoints
get-endpoints:
	@echo "SageMaker Endpoints:"
	@aws sagemaker list-endpoints \
		--query 'Endpoints[?contains(EndpointName, `kmeans`)].{Name:EndpointName,Status:EndpointStatus,Created:CreationTime}' \
		--output table

# Get model artifacts location
get-model-artifacts:
	@echo "Model Artifacts in S3:"
	@aws s3 ls s3://sagemaker-us-east-1-790768631355/sagemaker/customer-segmentation-kmeans/ --recursive \
		| grep model.tar.gz | tail -5



# Update Lambda function with latest code
update-lambda: package-lambda
	@echo "📦 Updating Lambda function..."
	python scripts/deploy_lambda.py --s3 --keep-zip

# Update SageMaker proxy Lambda
update-sagemaker-proxy:
	@echo "📦 Updating SageMaker proxy Lambda..."
	zip -j sagemaker-proxy.zip src/genai/sagemaker_proxy.py
	aws lambda update-function-code --function-name ml-pipeline-sagemaker-proxy-dev --zip-file fileb://sagemaker-proxy.zip
	rm -f sagemaker-proxy.zip
	@echo "✅ SageMaker proxy Lambda updated!"

# Deploy Lambda via S3 (for CloudFormation)
deploy-lambda-s3:
	@echo "📦 Deploying Lambda function via S3..."
	python scripts/deploy_lambda.py --s3 --keep-zip

# Test Customer Insights API
test-api:
	@echo "Testing Customer Insights API..."
	@API_URL=$$(aws cloudformation describe-stacks --stack-name ml-pipeline-stack --query 'Stacks[0].Outputs[?OutputKey==`GenAIApiUrl`].OutputValue' --output text); \
	echo "API Endpoint: $$API_URL"; \
	echo "Testing with customer feedback..."; \
	curl -X POST $$API_URL \
		-H "Content-Type: application/json" \
		-d '{ \
			"text": "The product works well but setup was confusing", \
			"source": "customer_review", \
			"category": "product_feedback" \
		}' | jq .

# Test SageMaker endpoint
test-sagemaker:
	@echo "Testing SageMaker K-means endpoint..."
	@ENDPOINT=$$(aws sagemaker list-endpoints --query 'Endpoints[?contains(EndpointName, `kmeans`)].EndpointName' --output text | head -1); \
	if [ -z "$$ENDPOINT" ]; then \
		echo "No K-means endpoints found. Deploy model first."; \
	else \
		echo "Testing endpoint: $$ENDPOINT"; \
		python scripts/test_sagemaker_endpoint.py --endpoint-name $$ENDPOINT; \
	fi

# Start SageMaker notebook instance
start-notebook:
	@echo "Starting SageMaker notebook instance..."
	aws sagemaker start-notebook-instance --notebook-instance-name ml-pipeline-notebook-dev
	@echo "Waiting for notebook to be in service..."
	aws sagemaker wait notebook-instance-in-service --notebook-instance-name ml-pipeline-notebook-dev
	@echo "Notebook is ready!"

# Stop SageMaker notebook instance
stop-notebook:
	@echo "Stopping SageMaker notebook instance..."
	aws sagemaker stop-notebook-instance --notebook-instance-name ml-pipeline-notebook-dev
	@echo "Waiting for notebook to stop..."
	aws sagemaker wait notebook-instance-stopped --notebook-instance-name ml-pipeline-notebook-dev
	@echo "Notebook stopped!"
