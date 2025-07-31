#!/usr/bin/env python3
"""
Test script for SageMaker K-means customer segmentation endpoint.
"""

import boto3
import json
import numpy as np
import argparse
import sys
from io import StringIO


def test_sagemaker_endpoint(endpoint_name: str) -> None:
    """
    Test the SageMaker K-means endpoint with sample customer data.
    
    Args:
        endpoint_name: Name of the SageMaker endpoint
    """
    print(f"Testing SageMaker endpoint: {endpoint_name}")
    
    # Initialize SageMaker runtime client
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    
    # Sample test data (normalized customer features: Age, Income, Purchases)
    test_data = np.array([
        [-1.1399157, -1.134114, 0.6786672],      # Young, low income, high purchases
        [-1.6670444, -0.80645496, -0.21812823],  # Very young, low income, medium purchases
        [-0.01976732, -0.01708255, -1.5978135],  # Average age/income, very low purchases
        [1.100381, 0.44526705, -0.2871125],      # Older, high income, low purchases
        [-1.3375889, -1.0499506, 1.6444468]      # Young, low income, very high purchases
    ])
    
    print(f"\nTest data shape: {test_data.shape}")
    print(f"Test data (normalized features):")
    print(test_data)
    
    # Convert to CSV format for SageMaker
    csv_buffer = StringIO()
    np.savetxt(csv_buffer, test_data, delimiter=',', fmt='%.6f')
    csv_data = csv_buffer.getvalue()
    
    try:
        # Make prediction request
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Accept='application/json',
            Body=csv_data
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        print(f"\n✅ Predictions (cluster assignments):")
        print(json.dumps(result, indent=2))
        
        # Extract and display cluster assignments
        if 'predictions' in result:
            cluster_assignments = [pred['closest_cluster'] for pred in result['predictions']]
            distances = [pred['distance_to_cluster'] for pred in result['predictions']]
            
            print(f"\n📊 Summary:")
            print(f"Cluster assignments: {cluster_assignments}")
            print(f"Average distance to cluster: {np.mean(distances):.3f}")
            
            # Interpret clusters
            cluster_names = {
                0: "Budget-conscious customers",
                1: "Medium-value customers", 
                2: "High-value customers",
                3: "Young professionals",
                4: "Price-sensitive segment"
            }
            
            print(f"\n🎯 Customer Segments:")
            for i, (cluster, distance) in enumerate(zip(cluster_assignments, distances)):
                segment = cluster_names.get(int(cluster), f"Cluster {int(cluster)}")
                print(f"  Customer {i+1}: {segment} (distance: {distance:.3f})")
        
        print(f"\n✅ Endpoint test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error calling endpoint: {str(e)}")
        sys.exit(1)


def list_available_endpoints():
    """List available SageMaker endpoints."""
    sagemaker = boto3.client('sagemaker')
    
    try:
        response = sagemaker.list_endpoints()
        endpoints = response['Endpoints']
        
        if not endpoints:
            print("No SageMaker endpoints found.")
            return
        
        print("Available SageMaker endpoints:")
        for endpoint in endpoints:
            print(f"  - {endpoint['EndpointName']} ({endpoint['EndpointStatus']})")
            
    except Exception as e:
        print(f"Error listing endpoints: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Test SageMaker K-means endpoint')
    parser.add_argument(
        '--endpoint-name',
        help='SageMaker endpoint name (e.g., kmeans-2025-07-31-19-58-36-067)'
    )
    parser.add_argument(
        '--list-endpoints',
        action='store_true',
        help='List available SageMaker endpoints'
    )
    
    args = parser.parse_args()
    
    if args.list_endpoints:
        list_available_endpoints()
        return
    
    if not args.endpoint_name:
        print("Error: --endpoint-name is required")
        print("\nUse --list-endpoints to see available endpoints")
        sys.exit(1)
    
    test_sagemaker_endpoint(args.endpoint_name)


if __name__ == "__main__":
    main()