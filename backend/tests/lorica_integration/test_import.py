#!/usr/bin/env python3
"""
Test script to verify lorica package import and basic functionality.
This tests Step 1: Add Lorica Dependency
"""

import sys
import os

def test_lorica_import():
    """Test that lorica package can be imported and basic classes are available."""
    try:
        # Test basic lorica import
        import lorica
        print("✓ Successfully imported lorica package")
        
        # Test lorica.ohttp import
        from lorica import ohttp
        print("✓ Successfully imported lorica.ohttp")
        
        # Test lorica.ohttp.Session class
        from lorica.ohttp import Session
        print("✓ Successfully imported lorica.ohttp.Session")
        
        # Test lorica.ohttp.Transport class
        from lorica.ohttp import Transport
        print("✓ Successfully imported lorica.ohttp.Transport")
        
        # Test lorica.Session (main session class)
        from lorica import Session as LoricaSession
        print("✓ Successfully imported lorica.Session")
        
        # Test lorica.Transport (main transport class)
        from lorica import Transport as LoricaTransport
        print("✓ Successfully imported lorica.Transport")
        
        # Test that we can instantiate Session (without making actual requests)
        try:
            session = LoricaSession()
            print("✓ Successfully created lorica.Session instance")
        except Exception as e:
            print(f"⚠ Could not create Session instance (expected if no network): {e}")
        
        # Test that we can instantiate Transport (without making actual requests)
        try:
            transport = LoricaTransport()
            print("✓ Successfully created lorica.Transport instance")
        except Exception as e:
            print(f"⚠ Could not create Transport instance (expected if no network): {e}")
        
        print("\n🎉 All lorica import tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import lorica: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_lorica_version():
    """Test lorica package version and dependencies."""
    try:
        import lorica
        print(f"✓ Lorica package location: {lorica.__file__}")
        
        # Check if we can access version info
        if hasattr(lorica, '__version__'):
            print(f"✓ Lorica version: {lorica.__version__}")
        else:
            print("⚠ No version info available")
            
        return True
    except Exception as e:
        print(f"❌ Error checking lorica version: {e}")
        return False

def test_lorica_dependencies():
    """Test that lorica dependencies are available."""
    try:
        # Test ohttpy dependency
        import ohttpy
        print("✓ ohttpy dependency available")
        
        # Test cachetools dependency
        import cachetools
        print("✓ cachetools dependency available")
        
        # Test PyJWT dependency
        import jwt
        print("✓ PyJWT dependency available")
        
        return True
    except ImportError as e:
        print(f"❌ Missing lorica dependency: {e}")
        return False

if __name__ == "__main__":
    print("Testing Lorica Package Import (Step 1)")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing lorica import...")
    success &= test_lorica_import()
    
    print("\n2. Testing lorica version...")
    success &= test_lorica_version()
    
    print("\n3. Testing lorica dependencies...")
    success &= test_lorica_dependencies()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Lorica package is ready for integration.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)
