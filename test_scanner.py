#!/usr/bin/env python
"""
Test script for aiapp-scanner
Demonstrates various usage patterns
"""

import subprocess
import json
import sys

def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"COMMAND: {' '.join(cmd)}")
    print('='*60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Success")
            if result.stdout:
                try:
                    # Try to parse and pretty print JSON
                    data = json.loads(result.stdout)
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(result.stdout)
        else:
            print("✗ Failed")
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("✗ Timeout")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    tests = [
        {
            'cmd': ['python3', 'aiapp_scanner.py', '--create-default-config'],
            'description': 'Create default configuration'
        },
        {
            'cmd': ['python3', 'aiapp_scanner.py', '--pretty'],
            'description': 'Basic scan with pretty output'
        },
        {
            'cmd': ['python3', 'aiapp_scanner.py', '--output', '/tmp/scan_results.json'],
            'description': 'Scan with output to file'
        },
        {
            'cmd': ['python3', 'aiapp_scanner.py', '--config', 'scanner_config.json', '--pretty'],
            'description': 'Scan with custom config file'
        }
    ]

    results = []
    for test in tests:
        success = run_command(test['cmd'], test['description'])
        results.append({
            'description': test['description'],
            'success': success
        })

    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['description']}")

    total = len(results)
    passed = sum(1 for r in results if r['success'])
    print(f"\nPassed: {passed}/{total}")

    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
