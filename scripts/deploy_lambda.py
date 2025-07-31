#!/usr/bin/env python3
"""
Deploy Lambda function with updated code from src/genai/
Supports both direct update and S3-based deployment for CloudFormation
"""

import boto3
import zipfile
import os
import sys
import argparse
from pathlib import Path

def create_lambda_package(output_dir="."):
    """Create deployment package for lambda function."""
    print("📦 Creating Lambda deployment package...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create zip file
    zip_path = os.path.join(output_dir, "genai-insights.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main lambda files
        src_files = [
            'src/genai/genai_insights.py',
            'src/genai/adverse_events.py',
            'src/genai/prompts.py',
            'src/genai/utils.py'
        ]
        
        for src_file in src_files:
            if os.path.exists(src_file):
                # Add to zip with just filename (no path)
                zipf.write(src_file, os.path.basename(src_file))
                print(f"  ✅ Added {src_file}")
            else:
                print(f"  ⚠️  Missing {src_file}")
        
        # Create index.py as entry point
        index_content = '''# Lambda entry point
from genai_insights import handler'''
        zipf.writestr('index.py', index_content)
        print("  ✅ Added index.py entry point")
        
        # Fix relative imports in genai_insights.py
        with open('src/genai/genai_insights.py', 'r') as f:
            content = f.read()
        content = content.replace('from .adverse_events import', 'from adverse_events import')
        zipf.writestr('genai_insights.py', content)
        print("  ✅ Fixed relative imports")
    
    print(f"📦 Package created: {zip_path}")
    return zip_path

def deploy_to_s3(zip_path):
    """Deploy lambda package to S3."""
    print("📤 Uploading to S3...")
    
    try:
        # Get S3 bucket from CloudFormation
        cf_client = boto3.client('cloudformation')
        response = cf_client.describe_stacks(StackName='ml-pipeline-stack')
        outputs = response['Stacks'][0]['Outputs']
        
        bucket_name = None
        for output in outputs:
            if output['OutputKey'] == 'ModelBucketName':
                bucket_name = output['OutputValue']
                break
        
        if not bucket_name:
            print("❌ Could not find S3 bucket name")
            return False
        
        # Upload to S3
        s3_client = boto3.client('s3')
        s3_key = 'lambda/genai-insights.zip'
        
        s3_client.upload_file(zip_path, bucket_name, s3_key)
        print(f"✅ Uploaded to s3://{bucket_name}/{s3_key}")
        
        return bucket_name, s3_key
        
    except Exception as e:
        print(f"❌ Error uploading to S3: {str(e)}")
        return False

def create_or_update_lambda_function(zip_path, use_s3=False):
    """Create or update the lambda function."""
    lambda_client = boto3.client('lambda')
    function_name = 'ml-pipeline-genai-insights-dev'
    
    # Check if function exists
    try:
        lambda_client.get_function(FunctionName=function_name)
        function_exists = True
        print("🚀 Updating existing Lambda function...")
    except lambda_client.exceptions.ResourceNotFoundException:
        function_exists = False
        print("🆕 Creating new Lambda function...")
    
    try:
        if use_s3:
            # Deploy via S3
            s3_result = deploy_to_s3(zip_path)
            if not s3_result:
                return False
            
            bucket_name, s3_key = s3_result
            
            if function_exists:
                response = lambda_client.update_function_code(
                    FunctionName=function_name,
                    S3Bucket=bucket_name,
                    S3Key=s3_key
                )
            else:
                # Create function
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role='arn:aws:iam::790768631355:role/ml-pipeline-lambda-role-dev',
                    Handler='index.handler',
                    Code={'S3Bucket': bucket_name, 'S3Key': s3_key},
                    MemorySize=1024,
                    Timeout=30,
                    Environment={
                        'Variables': {
                            'BEDROCK_MODEL_ID': 'anthropic.claude-3-haiku-20240307-v1:0',
                            'BEDROCK_REGION': 'us-east-1',
                            'LOG_LEVEL': 'INFO'
                        }
                    }
                )
        else:
            # Direct zip upload
            with open(zip_path, 'rb') as f:
                zip_content = f.read()
            
            if function_exists:
                response = lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )
            else:
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role='arn:aws:iam::790768631355:role/ml-pipeline-lambda-role-dev',
                    Handler='index.handler',
                    Code={'ZipFile': zip_content},
                    MemorySize=1024,
                    Timeout=30,
                    Environment={
                        'Variables': {
                            'BEDROCK_MODEL_ID': 'anthropic.claude-3-haiku-20240307-v1:0',
                            'BEDROCK_REGION': 'us-east-1',
                            'LOG_LEVEL': 'INFO'
                        }
                    }
                )
        
        print(f"✅ Lambda function updated successfully!")
        print(f"   Function: {response['FunctionName']}")
        print(f"   Runtime: {response['Runtime']}")
        print(f"   Last Modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {str(e)}")
        return False

def test_api_endpoint():
    """Test the API endpoint."""
    print("🧪 Testing API endpoint...")
    
    cf_client = boto3.client('cloudformation')
    
    try:
        # Get API URL from CloudFormation
        response = cf_client.describe_stacks(StackName='ml-pipeline-stack')
        outputs = response['Stacks'][0]['Outputs']
        
        api_url = None
        for output in outputs:
            if output['OutputKey'] == 'GenAIApiUrl':
                api_url = output['OutputValue']
                break
        
        if api_url:
            print(f"🌐 API Endpoint: {api_url}")
            
            # Test with curl command
            test_data = {
                "text": "The product works well but setup was confusing",
                "source": "customer_review", 
                "category": "product_feedback"
            }
            
            import json
            curl_cmd = f'''curl -X POST {api_url} \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(test_data)}' '''
            
            print(f"\n🧪 Test command:")
            print(curl_cmd)
            
        else:
            print("❌ Could not find API URL in CloudFormation outputs")
            
    except Exception as e:
        print(f"❌ Error getting API URL: {str(e)}")

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy Lambda function')
    parser.add_argument('--s3', action='store_true', help='Deploy via S3 (for CloudFormation)')
    parser.add_argument('--keep-zip', action='store_true', help='Keep zip file after deployment')
    parser.add_argument('--package-only', action='store_true', help='Only package and upload to S3, don\'t update function')
    args = parser.parse_args()
    
    print("🚀 Lambda Deployment Script")
    print("=" * 40)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Create package
    output_dir = "lambda_packages" if args.s3 else "."
    zip_path = create_lambda_package(output_dir)
    
    if args.package_only:
        # Just package and upload to S3
        if args.s3:
            deploy_to_s3(zip_path)
            print(f"📦 Package uploaded to S3: {zip_path}")
        print("\n✅ Packaging complete!")
    else:
        # Create or update lambda
        if create_or_update_lambda_function(zip_path, use_s3=args.s3):
            # Clean up unless keeping zip
            if not args.keep_zip and not args.s3:
                os.remove(zip_path)
                print(f"🧹 Cleaned up {zip_path}")
            elif args.s3:
                print(f"📦 Package saved: {zip_path}")
            
            # Test endpoint
            test_api_endpoint()
            
            print("\n✅ Deployment complete!")
        else:
            print("\n❌ Deployment failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()