#!/usr/bin/env python3
"""
Test script for the Customer Insights GenAI API endpoint.
"""

import requests
import json
import argparse
import sys
import time


def test_genai_api(api_url: str, feedback_data: dict) -> None:
    """
    Test the Customer Insights GenAI API endpoint.
    
    Args:
        api_url: The API Gateway URL
        feedback_data: Customer feedback data to send
    """
    # Use the API URL directly (it already includes the full path)
    endpoint_url = api_url.rstrip('/')
    
    print(f"Testing Customer Insights API at: {endpoint_url}")
    print(f"Sending data: {json.dumps(feedback_data, indent=2)}")
    
    start_time = time.time()
    
    try:
        # Send POST request
        response = requests.post(
            endpoint_url,
            json=feedback_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Check response
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {response_time}ms")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success! Customer Insights:")
            print("-" * 50)
            print(f"Sentiment: {result.get('sentiment_label')} ({result.get('sentiment_score')})")
            print(f"Language: {result.get('language_detected')}")
            print(f"Confidence: {result.get('confidence')}")
            print(f"Model: {result.get('model')}")
            print(f"Processing Time: {result.get('processing_time_ms')}ms")
            
            insights = result.get('insights', {})
            print(f"\nUnmet Needs: {insights.get('unmet_needs', [])}")
            print(f"Pain Points: {insights.get('pain_points', [])}")
            print(f"Positive Aspects: {insights.get('positive_aspects', [])}")
            print(f"Recommendations: {result.get('recommendations', [])}")
            
            safety_concerns = result.get('safety_concerns', [])
            if safety_concerns:
                print(f"\n⚠️  Safety Concerns: {len(safety_concerns)} detected")
                for concern in safety_concerns:
                    print(f"  - {concern.get('event')} ({concern.get('severity')})")
            else:
                print("\n✅ No safety concerns detected")
        else:
            print(f"\n❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Test Customer Insights GenAI API')
    parser.add_argument(
        '--api-url',
        required=True,
        help='API Gateway URL (from CloudFormation outputs)'
    )
    parser.add_argument(
        '--test-case',
        default='product_feedback',
        choices=['product_feedback', 'safety_concern', 'spanish_feedback', 'positive_review'],
        help='Test case type'
    )
    
    args = parser.parse_args()
    
    # Sample test cases
    test_cases = {
        'product_feedback': {
            'text': 'The product works well but the setup process was confusing and took hours',
            'source': 'customer_review',
            'category': 'product_feedback'
        },
        'safety_concern': {
            'text': 'The device got very hot and burned my hand during use. This is dangerous!',
            'source': 'customer_complaint',
            'category': 'safety_issue'
        },
        'spanish_feedback': {
            'text': 'El producto es bueno pero el precio es muy alto para lo que ofrece',
            'source': 'survey',
            'category': 'pricing_feedback'
        },
        'positive_review': {
            'text': 'Love this product! Easy to use and great customer service. Highly recommend!',
            'source': 'app_store_review',
            'category': 'general_feedback'
        }
    }
    
    feedback_data = test_cases[args.test_case]
    test_genai_api(args.api_url, feedback_data)


if __name__ == "__main__":
    main()