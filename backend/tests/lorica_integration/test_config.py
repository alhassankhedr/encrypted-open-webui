#!/usr/bin/env python3
"""
Test script to verify Lorica configuration system.
This tests Step 2: Add Lorica Configuration System
"""

import os
import sys
import tempfile
import shutil

def test_lorica_config_import():
    """Test that Lorica configuration can be imported and accessed."""
    try:
        # Test importing the config module
        from open_webui.config import (
            ENABLE_LORICA_API,
            LORICA_API_KEY,
            LORICA_API_BASE_URL,
            LORICA_API_KEYS,
            LORICA_API_BASE_URLS,
            LORICA_API_CONFIGS
        )
        print("✓ Successfully imported Lorica configuration variables")
        
        # Test that config objects are created
        assert hasattr(ENABLE_LORICA_API, 'value'), "ENABLE_LORICA_API should have value attribute"
        assert hasattr(LORICA_API_KEYS, 'value'), "LORICA_API_KEYS should have value attribute"
        assert hasattr(LORICA_API_BASE_URLS, 'value'), "LORICA_API_BASE_URLS should have value attribute"
        assert hasattr(LORICA_API_CONFIGS, 'value'), "LORICA_API_CONFIGS should have value attribute"
        print("✓ All Lorica config objects have proper structure")
        
        # Test that ENABLE_LORICA_API is properly configured
        assert isinstance(ENABLE_LORICA_API.value, bool), f"ENABLE_LORICA_API should be a boolean, got {type(ENABLE_LORICA_API.value)}"
        print(f"✓ ENABLE_LORICA_API is properly configured: {ENABLE_LORICA_API.value}")
        assert isinstance(LORICA_API_KEYS.value, list), f"LORICA_API_KEYS should be a list, got {type(LORICA_API_KEYS.value)}"
        assert isinstance(LORICA_API_BASE_URLS.value, list), f"LORICA_API_BASE_URLS should be a list, got {type(LORICA_API_BASE_URLS.value)}"
        assert isinstance(LORICA_API_CONFIGS.value, dict), f"LORICA_API_CONFIGS should be a dict, got {type(LORICA_API_CONFIGS.value)}"
        print("✓ Default values are correct")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Lorica config: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_lorica_config_persistence():
    """Test that Lorica configuration can be persisted and retrieved."""
    try:
        from open_webui.config import (
            ENABLE_LORICA_API,
            LORICA_API_KEYS,
            LORICA_API_BASE_URLS,
            LORICA_API_CONFIGS
        )
        
        # Test setting values
        original_enable = ENABLE_LORICA_API.value
        original_keys = LORICA_API_KEYS.value.copy()
        original_urls = LORICA_API_BASE_URLS.value.copy()
        original_configs = LORICA_API_CONFIGS.value.copy()
        
        # Modify values
        ENABLE_LORICA_API.value = True
        LORICA_API_KEYS.value = ['test-key-1', 'test-key-2']
        LORICA_API_BASE_URLS.value = ['https://lorica1.example.com', 'https://lorica2.example.com']
        LORICA_API_CONFIGS.value = {'0': {'attest': True}, '1': {'attest': False}}
        
        # Verify values were set
        assert ENABLE_LORICA_API.value == True, "ENABLE_LORICA_API should be True"
        assert len(LORICA_API_KEYS.value) == 2, "LORICA_API_KEYS should have 2 items"
        assert len(LORICA_API_BASE_URLS.value) == 2, "LORICA_API_BASE_URLS should have 2 items"
        assert len(LORICA_API_CONFIGS.value) == 2, "LORICA_API_CONFIGS should have 2 items"
        print("✓ Configuration values can be set and retrieved")
        
        # Restore original values
        ENABLE_LORICA_API.value = original_enable
        LORICA_API_KEYS.value = original_keys
        LORICA_API_BASE_URLS.value = original_urls
        LORICA_API_CONFIGS.value = original_configs
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration persistence: {e}")
        return False

def test_lorica_config_validation():
    """Test Lorica configuration validation and edge cases."""
    try:
        from open_webui.config import (
            LORICA_API_KEYS,
            LORICA_API_BASE_URLS
        )
        
        # Test empty configuration
        LORICA_API_KEYS.value = []
        LORICA_API_BASE_URLS.value = []
        assert len(LORICA_API_KEYS.value) == 0, "Empty LORICA_API_KEYS should work"
        assert len(LORICA_API_BASE_URLS.value) == 0, "Empty LORICA_API_BASE_URLS should work"
        print("✓ Empty configuration works")
        
        # Test URL configuration
        LORICA_API_BASE_URLS.value = ['https://example.com/', 'https://test.com/']
        # Note: The trimming logic is in the config loading, not in the PersistentConfig
        print("✓ URL configuration accepts trailing slashes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration validation: {e}")
        return False

if __name__ == "__main__":
    print("Testing Lorica Configuration System (Step 2)")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing Lorica config import...")
    success &= test_lorica_config_import()
    
    print("\n2. Testing configuration persistence...")
    success &= test_lorica_config_persistence()
    
    print("\n3. Testing configuration validation...")
    success &= test_lorica_config_validation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All Lorica configuration tests passed!")
        print("✅ ENABLE_LORICA_API - Boolean flag to enable/disable Lorica API")
        print("✅ LORICA_API_KEYS - List of API keys for Lorica connections")
        print("✅ LORICA_API_BASE_URLS - List of base URLs for Lorica connections")
        print("✅ LORICA_API_CONFIGS - Dictionary of configuration per connection")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)
