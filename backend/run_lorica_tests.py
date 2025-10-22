#!/usr/bin/env python3
"""
Comprehensive test runner for Lorica integration tests.
Run this from the backend directory: python run_lorica_tests.py
"""

import sys
import os
import subprocess

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test_file(test_file, test_name):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running {test_name}")
    print(f"{'='*60}")
    
    try:
        # Set PYTHONPATH to include the backend directory
        env = os.environ.copy()
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        env['PYTHONPATH'] = backend_dir
        
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              cwd=backend_dir,
                              env=env)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_name}: {e}")
        return False

def main():
    """Run all Lorica tests."""
    print("🧪 Running All Lorica Integration Tests")
    print("=" * 60)
    
    # Define tests in order
    tests = [
        ("tests/lorica_integration/test_import.py", "Step 1: Lorica Package Import"),
        ("tests/lorica_integration/test_config.py", "Step 2: Lorica Configuration System"),
        # Add more tests as we implement them
        # ("tests/lorica_integration/test_client.py", "Step 3: Async Lorica Client"),
        # ("tests/lorica_integration/test_router.py", "Step 4: Lorica Router"),
        # ("tests/lorica_integration/test_integration.py", "Step 5: Full Integration"),
    ]
    
    all_passed = True
    
    for test_file, test_name in tests:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            success = run_test_file(test_path, test_name)
            all_passed &= success
        else:
            print(f"⚠ Skipping {test_name} - {test_file} not found")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All Lorica integration tests passed!")
        print("✅ Step 1: Lorica package dependency - COMPLETE")
        print("✅ Step 2: Lorica configuration system - COMPLETE")
        print("✅ Ready for Step 3: Async Lorica Client Wrapper")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
