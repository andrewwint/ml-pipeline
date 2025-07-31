# SageMaker Notebook Environment

This directory contains the SageMaker notebook for K-means customer segmentation model development.

## Notebook Overview

### `CustomerSegmentation.ipynb`
- **Purpose**: Complete K-means clustering pipeline from EDA to deployment
- **Algorithm**: K-means with 5 optimal clusters (silhouette score: 0.62)
- **Deployment**: Creates live SageMaker endpoint for real-time inference
- **Performance**: ~150ms inference latency

## SageMaker Infrastructure

### Instance Types
- **Notebook Instance**: `ml.t3.medium` - Cost-effective for development
- **Endpoint Instance**: `ml.m5.large` - Optimized for real-time inference

### Automated Lifecycle Configuration

The `NotebookInstanceLifecycleConfig` in CloudFormation handles:

1. **Environment Setup**
   - Configures S3 bucket environment variables
   - Sets up system-wide access to data and model buckets

2. **Git Integration**
   - Retrieves GitHub credentials from AWS Secrets Manager
   - Clones/updates the ml-pipeline repository automatically
   - Configures authenticated Git remote for seamless push/pull
   - Sets up user identity and credential helper

3. **Jupyter Configuration**
   - Opens directly in `/ml-pipeline/notebooks/` directory
   - Installs project dependencies from requirements.txt
   - Configures notebook server settings

4. **Auto-Shutdown**
   - Monitors notebook activity every 5 minutes
   - Automatically stops instance after 30 minutes of inactivity
   - Prevents unnecessary costs from idle instances

### Two-Way Git Integration

**From SageMaker to GitHub:**
```bash
# In SageMaker terminal
cd /home/ec2-user/SageMaker/ml-pipeline
git add notebooks/
git commit -m "Update model from SageMaker"
git push
```

**From Local to SageMaker:**
```bash
# Locally
git push

# SageMaker automatically pulls latest changes on startup
```

## Management Commands

### Notebook Operations
```bash
make start-notebook      # Start notebook instance (ml.t3.medium)
make stop-notebook       # Stop notebook to save costs
```

### Model Management
```bash
make get-endpoints       # List SageMaker model endpoints
make get-model-artifacts # Show model artifacts in S3
make test-sagemaker      # Test deployed K-means endpoint
make update-sagemaker-proxy # Update SageMaker API proxy
```

## Model Deployment Results

- **Endpoint**: `kmeans-2025-07-31-19-58-36-067` (InService)
- **Clusters**: 5 customer segments with 0.62 silhouette score
- **Public API**: Available at `/segment` endpoint via `SageMakerProxyLambdaFunction`
- **Proxy Function**: Lambda function that proxies requests to private K-means endpoint
- **Inference**: ~150ms latency with auto-scaling (1-4 instances)

## Cost Optimization

- **Auto-shutdown**: 30-minute idle timeout
- **Manual control**: Use `make stop-notebook` when not in use
- **Endpoint costs**: ~$0.10/hour when running
- **Notebook costs**: ~$0.05/hour when running
