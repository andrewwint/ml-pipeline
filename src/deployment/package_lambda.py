"""
Lambda packaging script for GenAI insights function.
"""

import zipfile
import os
import shutil
from pathlib import Path


def package_lambda():
    """Create deployment package for Lambda function."""
    
    # Define paths
    src_dir = Path(__file__).parent.parent
    lambda_dir = src_dir / 'genai'
    package_name = 'genai-lambda.zip'
    
    print(f"📦 Creating Lambda deployment package: {package_name}")
    
    # Create zip file
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Add Lambda source files
        lambda_files = [
            'genai_insights.py',
            'prompts.py', 
            'adverse_events.py',
            'utils.py'
        ]
        
        for file_name in lambda_files:
            file_path = lambda_dir / file_name
            if file_path.exists():
                zipf.write(file_path, file_name)
                print(f"  ✅ Added: {file_name}")
            else:
                print(f"  ⚠️  Missing: {file_name}")
    
    # Get package size
    package_size = os.path.getsize(package_name)
    size_mb = package_size / (1024 * 1024)
    
    print(f"📊 Package created successfully!")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Location: {os.path.abspath(package_name)}")
    
    return package_name


def update_cloudformation_code():
    """Update CloudFormation template to use packaged code."""
    
    print("\n🔄 To deploy the packaged Lambda:")
    print("1. Upload genai-lambda.zip to S3:")
    print("   aws s3 cp genai-lambda.zip s3://your-deployment-bucket/")
    print("\n2. Update CloudFormation template:")
    print("   Replace 'ZipFile' with 'S3Bucket' and 'S3Key' properties")
    print("\n3. Deploy updated stack:")
    print("   make deploy")


def clean_package():
    """Clean up deployment package."""
    package_name = 'genai-lambda.zip'
    if os.path.exists(package_name):
        os.remove(package_name)
        print(f"🗑️  Cleaned up: {package_name}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        clean_package()
    else:
        package_name = package_lambda()
        update_cloudformation_code()