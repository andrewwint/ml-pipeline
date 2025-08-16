.PHONY: help install deploy destroy clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install          - Install dependencies"
	@echo "  validate         - Validate CloudFormation template"
	@echo "  deploy           - Deploy complete infrastructure with auto-scaling (IaC)"
	@echo "  deploy-dev       - Deploy with minimal scaling (1-2 instances)"
	@echo "  deploy-prod      - Deploy with production scaling (2-8 instances)"
	@echo "  deploy-custom    - Deploy with custom scaling parameters"
	@echo "  update-lambda    - Update Lambda function code only"
	@echo "  update-sagemaker-proxy - Update SageMaker proxy Lambda"
	@echo "  test-api         - Test Customer Insights API"
	@echo "  test-sagemaker   - Test SageMaker K-means endpoint"
	@echo "  get-api-url      - Get GenAI API endpoint"
	@echo "  get-sagemaker-api-url - Get SageMaker API endpoint"
	@echo "  get-endpoints    - List SageMaker model endpoints with scaling info"
	@echo "  get-scaling      - Show auto-scaling configuration and metrics"
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

# Deploy complete infrastructure with auto-scaling (IaC)
deploy: validate
	@echo "Deploying complete infrastructure with auto-scaling..."
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

# Deploy with development scaling (minimal resources)
deploy-dev: validate
	@echo "Deploying with development auto-scaling configuration..."
	aws cloudformation deploy \
		--template-file infrastructure/cloudformation-complete.yaml \
		--stack-name ml-pipeline-stack \
		--parameter-overrides \
			EndpointMinCapacity=1 \
			EndpointMaxCapacity=2 \
			EndpointTargetInvocations=50 \
			SageMakerInstanceType=ml.t3.medium \
		--capabilities CAPABILITY_NAMED_IAM
	@echo "Updating Lambda function with latest code..."
	@$(MAKE) update-lambda
	@echo "✅ Development deployment complete with 1-2 instance auto-scaling!"

# Deploy with production scaling (high availability)
deploy-prod: validate
	@echo "Deploying with production auto-scaling configuration..."
	aws cloudformation deploy \
		--template-file infrastructure/cloudformation-complete.yaml \
		--stack-name ml-pipeline-stack \
		--parameter-overrides \
			EndpointMinCapacity=2 \
			EndpointMaxCapacity=8 \
			EndpointTargetInvocations=150 \
			SageMakerInstanceType=ml.m5.large \
		--capabilities CAPABILITY_NAMED_IAM
	@echo "Updating Lambda function with latest code..."
	@$(MAKE) update-lambda
	@echo "✅ Production deployment complete with 2-8 instance auto-scaling!"

# Deploy with custom scaling parameters (interactive)
deploy-custom: validate
	@echo "Deploy with custom auto-scaling parameters:"
	@read -p "Minimum instances (default 1): " MIN_CAP; \
	read -p "Maximum instances (default 4): " MAX_CAP; \
	read -p "Target invocations per instance (default 100): " TARGET_INV; \
	read -p "Instance type (default ml.m5.large): " INSTANCE_TYPE; \
	MIN_CAP=$${MIN_CAP:-1}; \
	MAX_CAP=$${MAX_CAP:-4}; \
	TARGET_INV=$${TARGET_INV:-100}; \
	INSTANCE_TYPE=$${INSTANCE_TYPE:-ml.m5.large}; \
	echo "Deploying with: Min=$${MIN_CAP}, Max=$${MAX_CAP}, Target=$${TARGET_INV}, Type=$${INSTANCE_TYPE}"; \
	aws cloudformation deploy \
		--template-file infrastructure/cloudformation-complete.yaml \
		--stack-name ml-pipeline-stack \
		--parameter-overrides \
			EndpointMinCapacity=$${MIN_CAP} \
			EndpointMaxCapacity=$${MAX_CAP} \
			EndpointTargetInvocations=$${TARGET_INV} \
			SageMakerInstanceType=$${INSTANCE_TYPE} \
		--capabilities CAPABILITY_NAMED_IAM
	@echo "Updating Lambda function with latest code..."
	@$(MAKE) update-lambda
	@echo "✅ Custom deployment complete!"

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

# Get SageMaker model endpoints with scaling info
get-endpoints:
	@echo "SageMaker Endpoints:"
	@aws sagemaker list-endpoints \
		--query 'Endpoints[?contains(EndpointName, `kmeans`)].{Name:EndpointName,Status:EndpointStatus,Created:CreationTime}' \
		--output table
	@echo ""
	@echo "Endpoint Configuration Details:"
	@ENDPOINT_NAME=$(aws sagemaker list-endpoints --query 'Endpoints[?contains(EndpointName, `kmeans`)].EndpointName' --output text | head -1); \
	if [ ! -z "$ENDPOINT_NAME" ]; then \
		aws sagemaker describe-endpoint --endpoint-name $ENDPOINT_NAME \
			--query 'ProductionVariants[0].{InstanceType:InstanceType,CurrentInstanceCount:CurrentInstanceCount,DesiredInstanceCount:DesiredInstanceCount}' \
			--output table; \
	else \
		echo "No K-means endpoints found"; \
	fi

# Get auto-scaling configuration and metrics
get-scaling:
	@echo "Auto-Scaling Configuration:"
	@ENDPOINT_NAME=$(aws sagemaker list-endpoints --query 'Endpoints[?contains(EndpointName, `kmeans`)].EndpointName' --output text | head -1); \
	if [ ! -z "$ENDPOINT_NAME" ]; then \
		echo "Endpoint: $ENDPOINT_NAME"; \
		echo ""; \
		echo "Scalable Targets:"; \
		aws application-autoscaling describe-scalable-targets \
			--service-namespace sagemaker \
			--resource-ids endpoint/$ENDPOINT_NAME/variant/AllTraffic \
			--query 'ScalableTargets[0].{MinCapacity:MinCapacity,MaxCapacity:MaxCapacity,CurrentCapacity:CurrentCapacity}' \
			--output table 2>/dev/null || echo "No auto-scaling configured"; \
		echo ""; \
		echo "Scaling Policies:"; \
		aws application-autoscaling describe-scaling-policies \
			--service-namespace sagemaker \
			--resource-id endpoint/$ENDPOINT_NAME/variant/AllTraffic \
			--query 'ScalingPolicies[0].TargetTrackingScalingPolicyConfiguration.{TargetValue:TargetValue,MetricType:PredefinedMetricSpecification.PredefinedMetricType}' \
			--output table 2>/dev/null || echo "No scaling policies found"; \
	else \
		echo "No K-means endpoints found"; \
	fi

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
			"text": "El producto funciona bien, pero la configuración fue confusa.", \
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
