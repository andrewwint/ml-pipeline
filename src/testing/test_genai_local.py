"""
Local testing script for GenAI Lambda function.
"""

import json
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from genai.genai_insights import handler


def test_local():
    """Test the Lambda function locally with sample data."""
    
    # Test cases for marketing insights
    test_cases = [
        {
            "name": "english_product_feedback",
            "input": {
                "text": "The product works well but the setup process was confusing and took hours",
                "source": "customer_review",
                "category": "product_feedback"
            }
        },
        {
            "name": "safety_concern_feedback",
            "input": {
                "text": "The device got very hot and burned my hand during use. This is dangerous!",
                "source": "customer_complaint",
                "category": "safety_issue"
            }
        },
        {
            "name": "spanish_pricing_concern",
            "input": {
                "text": "El producto es bueno pero el precio es muy alto para lo que ofrece",
                "source": "survey",
                "category": "pricing_feedback"
            }
        }
    ]
    
    print("🧪 Testing Customer Insights GenAI Lambda Function Locally")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {case['name']}")
        print("-" * 30)
        
        # Create mock event
        event = {
            'body': json.dumps(case['input']),
            'httpMethod': 'POST'
        }
        
        # Call handler
        try:
            result = handler(event, {})
            
            print(f"Status Code: {result['statusCode']}")
            
            if result['statusCode'] == 200:
                response_data = json.loads(result['body'])
                print(f"Sentiment: {response_data.get('sentiment_label')}")
                print(f"Language: {response_data.get('language_detected')}")
                print(f"Unmet Needs: {response_data.get('insights', {}).get('unmet_needs', [])}")
                print(f"Safety Concerns: {len(response_data.get('safety_concerns', []))} detected")
                print(f"Processing Time: {response_data.get('processing_time_ms')}ms")
            else:
                error_data = json.loads(result['body'])
                print(f"Error: {error_data.get('message')}")
                
        except Exception as e:
            print(f"Test failed: {str(e)}")
    
    print("\n✅ Local testing complete!")


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-haiku-20240307-v1:0'
    os.environ['BEDROCK_REGION'] = 'us-east-1'
    
    test_local()