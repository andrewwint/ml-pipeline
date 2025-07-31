# Troubleshooting Guide

This guide helps resolve common issues encountered during deployment and operation of the ML Pipeline.

## CloudFormation Deployment Issues

### 1. Stack Deployment Failures

#### Debugging Commands
```bash
# Check failed resources
aws cloudformation describe-stack-events --stack-name ml-pipeline-stack \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' \
  --output table

# Check stack status
aws cloudformation describe-stacks --stack-name ml-pipeline-stack \
  --query 'Stacks[0].StackStatus' --output text

# View all stack events (recent first)
aws cloudformation describe-stack-events --stack-name ml-pipeline-stack \
  --query 'StackEvents[0:10].[Timestamp,ResourceStatus,LogicalResourceId,ResourceStatusReason]' \
  --output table
```

#### Common Failure Scenarios

**S3 Bucket Already Exists**
```
Error: ml-pipeline-data-790768631355-us-east-1 already exists
```
**Cause**: S3 bucket names must be globally unique. Previous deployment left buckets.
**Solution**:
```bash
make force-destroy    # Clean up orphaned buckets
make deploy          # Retry deployment
```

**IAM Role Creation Failed**
```
Error: Role with name ml-pipeline-sagemaker-role-dev already exists
```
**Cause**: Previous deployment left IAM resources.
**Solution**:
```bash
# Delete existing role manually
aws iam delete-role --role-name ml-pipeline-sagemaker-role-dev
make deploy
```

**Lambda Function Already Exists**
```
Error: Function creation failed because the function already exists
```
**Cause**: Lambda function exists outside CloudFormation management.
**Solution**:
```bash
# Delete existing function
aws lambda delete-function --function-name ml-pipeline-genai-insights-dev
make deploy
```

### 2. Stack Deletion Issues

#### S3 Bucket Not Empty
```
Error: The bucket you tried to delete is not empty
```
**Cause**: S3 buckets contain objects or versions that prevent deletion.
**Solution**:
```bash
# Force cleanup with bucket emptying
make force-destroy

# Manual cleanup if needed
make clean-buckets
```

#### Resources in Use
```
Error: Resource is in use and cannot be deleted
```
**Cause**: Resources have dependencies or are actively being used.
**Solution**:
```bash
# Stop all running resources first
make stop-notebook

# Wait for resources to stop, then retry
aws cloudformation delete-stack --stack-name ml-pipeline-stack
```

## S3 Bucket Issues

### 1. Bucket Access Denied
```
Error: Access Denied when accessing S3 bucket
```
**Debugging**:
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket ml-pipeline-data-790768631355-us-east-1

# Check IAM permissions
aws iam get-role-policy --role-name ml-pipeline-sagemaker-role-dev --policy-name S3Access
```

**Solution**:
- Verify IAM role has correct S3 permissions
- Check bucket policy allows the role access
- Ensure bucket exists in correct region

### 2. Versioned Objects Blocking Deletion
```
Error: Bucket cannot be deleted due to versioned objects
```
**Solution**:
```bash
# List all versions
aws s3api list-object-versions --bucket ml-pipeline-data-790768631355-us-east-1

# Use force cleanup
make clean-buckets
```

## Lambda Function Issues

### 1. Import Errors
```
Error: Unable to import module 'index': attempted relative import with no known parent package
```
**Cause**: Relative imports in Lambda package.
**Solution**:
```bash
# Redeploy with fixed imports
make update-lambda
```

### 2. Bedrock Access Denied
```
Error: User is not authorized to perform: bedrock:InvokeModel
```
**Debugging**:
```bash
# Check Lambda execution role
aws iam get-role-policy --role-name ml-pipeline-lambda-role-dev --policy-name BedrockAccess

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/ml-pipeline-genai
```

**Solution**:
- Verify Lambda role has Bedrock permissions
- Check Bedrock model access in correct region
- Ensure model ID is correct

### 3. Timeout Issues
```
Error: Task timed out after 30.00 seconds
```
**Solution**:
```bash
# Increase timeout in CloudFormation template
# Or update directly
aws lambda update-function-configuration \
  --function-name ml-pipeline-genai-insights-dev \
  --timeout 60
```

## SageMaker Issues

### 1. Notebook Instance Failures
```
Error: Notebook instance failed to start
```
**Debugging**:
```bash
# Check notebook status
aws sagemaker describe-notebook-instance --notebook-instance-name ml-pipeline-notebook-dev

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/sagemaker/NotebookInstances
```

**Common Causes**:
- Insufficient IAM permissions
- VPC/subnet configuration issues
- Instance type not available in region

### 2. Endpoint Deployment Failures
```
Error: Endpoint creation failed
```
**Debugging**:
```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name kmeans-2025-07-31-19-58-36-067

# Check model status
aws sagemaker describe-model --model-name customer-segmentation-model
```

**Solutions**:
- Verify model artifacts exist in S3
- Check instance type availability
- Ensure IAM role has SageMaker permissions

### 3. Training Job Failures
```
Error: Training job failed
```
**Debugging**:
```bash
# Check training job logs
aws sagemaker describe-training-job --training-job-name customer-segmentation-training

# View CloudWatch logs
aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs \
  --log-stream-name customer-segmentation-training/algo-1-1234567890
```

## API Gateway Issues

### 1. 403 Forbidden Errors
```
Error: {"message":"Missing Authentication Token"}
```
**Cause**: API Gateway integration not properly configured.
**Debugging**:
```bash
# Check API Gateway configuration
aws apigateway get-rest-apis

# Check Lambda permissions
aws lambda get-policy --function-name ml-pipeline-genai-insights-dev
```

**Solution**:
- Verify Lambda permission for API Gateway exists
- Check API Gateway deployment stage
- Ensure CORS is configured correctly

### 2. 500 Internal Server Error
```
Error: Internal server error
```
**Debugging**:
```bash
# Check Lambda logs
aws logs tail /aws/lambda/ml-pipeline-genai-insights-dev --follow

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs
```

## Debugging Workflow

### 1. Identify the Problem
```bash
# Check overall stack status
make status

# List all resources
aws cloudformation list-stack-resources --stack-name ml-pipeline-stack
```

### 2. Check CloudWatch Logs
```bash
# Lambda logs
aws logs tail /aws/lambda/ml-pipeline-genai-insights-dev --follow

# SageMaker logs
aws logs describe-log-groups --log-group-name-prefix /aws/sagemaker

# API Gateway logs (if enabled)
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs
```

### 3. Verify Permissions
```bash
# Check IAM roles
aws iam list-roles --query 'Roles[?contains(RoleName, `ml-pipeline`)].RoleName'

# Check policies
aws iam list-attached-role-policies --role-name ml-pipeline-sagemaker-role-dev
```

### 4. Test Components Individually
```bash
# Test Lambda function directly
aws lambda invoke --function-name ml-pipeline-genai-insights-dev \
  --payload '{"body": "{\"text\": \"test\"}"}' response.json

# Test SageMaker endpoint
make test-sagemaker

# Test API Gateway
make test-api
```

## Recovery Procedures

### 1. Partial Stack Failure
```bash
# Continue update from failed state
aws cloudformation continue-update-rollback --stack-name ml-pipeline-stack

# Or cancel and retry
aws cloudformation cancel-update-stack --stack-name ml-pipeline-stack
make deploy
```

### 2. Complete Stack Corruption
```bash
# Force complete cleanup
make force-destroy

# Wait for complete deletion
aws cloudformation wait stack-delete-complete --stack-name ml-pipeline-stack

# Redeploy from scratch
make deploy
```

### 3. Resource Conflicts
```bash
# Identify conflicting resources
aws cloudformation describe-stack-events --stack-name ml-pipeline-stack \
  --query 'StackEvents[?contains(ResourceStatusReason, `already exists`)]'

# Delete conflicting resources manually
# Then retry deployment
make deploy
```

## Prevention Best Practices

### 1. Clean Deployments
```bash
# Always check for existing resources
aws s3 ls | grep ml-pipeline
aws lambda list-functions --query 'Functions[?contains(FunctionName, `ml-pipeline`)]'

# Use force-destroy for complete cleanup
make force-destroy
```

### 2. Monitoring
```bash
# Set up CloudWatch alarms
# Monitor stack events during deployment
# Check logs regularly
```

### 3. Testing
```bash
# Test in development environment first
# Validate templates before deployment
make validate
```

## Getting Help

### 1. AWS Support Resources
- AWS CloudFormation documentation
- AWS SageMaker troubleshooting guides
- AWS Lambda best practices

### 2. Debugging Commands Summary
```bash
# Stack events
aws cloudformation describe-stack-events --stack-name ml-pipeline-stack

# Resource status
aws cloudformation list-stack-resources --stack-name ml-pipeline-stack

# CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/ml-pipeline

# Service status
make status
make get-endpoints
```

### 3. Emergency Cleanup
```bash
# Nuclear option - removes everything
make force-destroy
make clean-buckets

# Verify cleanup
aws s3 ls | grep ml-pipeline
aws cloudformation describe-stacks --stack-name ml-pipeline-stack
```

This troubleshooting guide covers the most common issues encountered during deployment and operation. Always check CloudWatch logs for detailed error messages and use the debugging commands to identify root causes.