# Notebooks Directory

This directory contains Jupyter notebooks for the ML Pipeline customer segmentation model development and analysis.

## Notebooks Overview

### `01_eda_analysis.ipynb`

**Purpose**: Exploratory Data Analysis of customer segmentation dataset

**Contents**:

- Dataset overview and statistics
- Feature distribution analysis
- Correlation analysis between features
- Data quality assessment
- Visualization of customer patterns

**Key Insights**:

- Customer age distribution and income patterns
- Purchase behavior analysis
- Gender distribution across segments
- Feature relationships and correlations

### `02_model_development.ipynb`

**Purpose**: K-means clustering model development and deployment

**Contents**:

- Data preprocessing and feature engineering
- Optimal cluster number determination (Elbow method)
- K-means model training and validation
- Model evaluation using silhouette scores
- SageMaker endpoint deployment
- Real-time prediction testing

**Model Results**:

- **Algorithm**: K-means clustering
- **Optimal Clusters**: 5 (determined via Elbow method)
- **Silhouette Score**: 0.62
- **Deployment**: SageMaker real-time endpoint
- **Inference Latency**: < 200ms

## SageMaker Integration

### Endpoint Deployment

The notebooks create a managed SageMaker endpoint for real-time predictions:

```python
# Example endpoint creation
kmeans_predictor = kmeans_sagemaker.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name=f'kmeans-{timestamp}'
)
```

### Model Artifacts

Trained models are automatically stored in S3:

```
s3://sagemaker-us-east-1-{account-id}/sagemaker/customer-segmentation-kmeans/
└── output/
    └── kmeans-{timestamp}/
        └── output/
            └── model.tar.gz
```

## Usage Instructions

### 1. Start SageMaker Notebook

```bash
make start-notebook    # Start the notebook instance
```

### 2. Access Jupyter

- Navigate to SageMaker console or use the notebook URL
- Open `ml-pipeline/notebooks/` directory
- Run notebooks in order: `01_eda_analysis.ipynb` → `02_model_development.ipynb`

### 3. Git Integration

The notebooks are automatically connected to git:

```bash
# In SageMaker terminal
cd /home/ec2-user/SageMaker/ml-pipeline
git add notebooks/
git commit -m "Update model development"
git push
```

### 4. Check Deployed Resources

```bash
make get-endpoints        # List SageMaker endpoints
make get-model-artifacts  # Show model artifacts in S3
```

### 5. Test Model Endpoint

```bash
# Test the deployed model endpoint
python scripts/test_sagemaker_endpoint.py --endpoint-name kmeans-2025-07-31-19-58-36-067
```

## Model Performance

### Customer Segmentation Results

- **Cluster 0**: High-value customers (high income, frequent purchases)
- **Cluster 1**: Medium-value customers (moderate income/purchases)
- **Cluster 2**: Low-value customers (lower income, infrequent purchases)
- **Cluster 3**: Young professionals (high income, selective purchases)
- **Cluster 4**: Budget-conscious customers (price-sensitive segment)

### Deployment Metrics

- **Endpoint Status**: InService
- **Instance Type**: ml.m5.large
- **Auto-scaling**: 1-4 instances
- **Inference Latency**: ~150ms average
- **Cost**: ~$0.10/hour when running

### Sample Prediction Results

```python
# Input: Normalized customer features [Age, Income, Purchases]
test_data = [[-1.14, -1.13, 0.68], [-1.67, -0.81, -0.22]]

# Output: Cluster assignments with distances
{
    'predictions': [
        {'closest_cluster': 4.0, 'distance_to_cluster': 0.92},
        {'closest_cluster': 4.0, 'distance_to_cluster': 1.37}
    ]
}
```

## Development Workflow

1. **Data Exploration**: Run `01_eda_analysis.ipynb` to understand the dataset
2. **Model Development**: Use `02_model_development.ipynb` for training and deployment
3. **Testing**: Validate predictions using the deployed endpoint
4. **Iteration**: Modify hyperparameters and retrain as needed
5. **Version Control**: Commit changes to git for tracking

## Cost Management

### Auto-shutdown

- Notebook automatically stops after 30 minutes of inactivity
- Use `make stop-notebook` to manually stop when not in use

### Endpoint Management

- Endpoints continue running until manually deleted
- Monitor costs in AWS console
- Delete unused endpoints to avoid charges

## Troubleshooting

### Common Issues

1. **Kernel not found**: Restart kernel and run cells again
2. **S3 permissions**: Ensure SageMaker role has proper S3 access
3. **Endpoint deployment fails**: Check instance limits and quotas
4. **Git authentication**: Verify GitHub credentials in Secrets Manager

### Support Commands

```bash
make status              # Check CloudFormation stack status
make get-endpoints       # List current endpoints
make start-notebook      # Restart notebook if stopped
```
