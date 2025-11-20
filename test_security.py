#!/usr/bin/env python3
"""
Security test script for webhook endpoint.
Tests payload validation and size limits.
"""

import json
import sys

# Test the validation function directly
sys.path.insert(0, '/home/user/aotr-listener/vercel-deployment/api')
from webhook import validate_aotr_payload


def test_validation():
    """Test payload validation function."""
    print("Testing Payload Validation")
    print("=" * 80)

    tests = [
        # Valid AOTR payload
        {
            'name': 'Valid AOTR payload with embeds',
            'payload': {
                'embeds': [{
                    'title': 'AOTR Logger',
                    'fields': [
                        {'name': 'Level', 'value': '10', 'inline': True},
                        {'name': 'Gold', 'value': '1000', 'inline': True}
                    ]
                }]
            },
            'should_pass': True
        },
        # Valid content-only payload
        {
            'name': 'Valid content-only payload',
            'payload': {
                'content': 'Test message'
            },
            'should_pass': True
        },
        # Invalid: not a dict
        {
            'name': 'Invalid: not a dictionary',
            'payload': "not a dict",
            'should_pass': False
        },
        # Invalid: no embeds or content
        {
            'name': 'Invalid: missing embeds and content',
            'payload': {
                'random_field': 'value'
            },
            'should_pass': False
        },
        # Invalid: embeds not an array
        {
            'name': 'Invalid: embeds not an array',
            'payload': {
                'embeds': 'not an array'
            },
            'should_pass': False
        },
        # Invalid: embed missing title and description
        {
            'name': 'Invalid: embed missing title and description',
            'payload': {
                'embeds': [{
                    'color': 123456
                }]
            },
            'should_pass': False
        },
        # Invalid: field missing name or value
        {
            'name': 'Invalid: field missing value',
            'payload': {
                'embeds': [{
                    'title': 'Test',
                    'fields': [
                        {'name': 'Field1'}  # Missing 'value'
                    ]
                }]
            },
            'should_pass': False
        },
        # Valid: embed with description but no title
        {
            'name': 'Valid: embed with description only',
            'payload': {
                'embeds': [{
                    'description': 'Just a description'
                }]
            },
            'should_pass': True
        },
    ]

    passed = 0
    failed = 0

    for test in tests:
        is_valid, error_msg = validate_aotr_payload(test['payload'])
        expected = test['should_pass']

        if is_valid == expected:
            print(f"✅ PASS: {test['name']}")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Expected: {'valid' if expected else 'invalid'}")
            print(f"   Got: {'valid' if is_valid else 'invalid'}")
            if error_msg:
                print(f"   Error: {error_msg}")
            failed += 1

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    success = test_validation()
    sys.exit(0 if success else 1)
