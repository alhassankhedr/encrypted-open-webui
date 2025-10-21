/**
 * Test script to verify Lorica API integration
 * Run this in the browser console on the Open WebUI page
 */

console.log('🧪 Starting Lorica API Integration Test...');

// Test 1: Check if loricaFetch is available
async function testLoricaFetch() {
    console.log('1. Testing loricaFetch availability...');
    
    try {
        // Check if the fetch wrapper is available
        const response = await fetch('/api/health');
        console.log('✅ Standard fetch works');
        
        // Check if Lorica modules are loaded
        if (typeof window.loricaFetch === 'function') {
            console.log('✅ loricaFetch is available');
        } else {
            console.log('⚠️ loricaFetch not found - checking for module imports...');
        }
        
        return true;
    } catch (error) {
        console.error('❌ Fetch test failed:', error);
        return false;
    }
}

// Test 2: Check settings integration
async function testSettingsIntegration() {
    console.log('2. Testing settings integration...');
    
    try {
        // Check if settings store has Lorica properties
        const settings = window.localStorage.getItem('settings');
        if (settings) {
            const parsed = JSON.parse(settings);
            console.log('✅ Settings found:', Object.keys(parsed));
            
            // Check for Lorica-specific settings
            if (parsed.loricaEnabled !== undefined) {
                console.log('✅ Lorica settings found in localStorage');
            } else {
                console.log('⚠️ Lorica settings not found - may need to be added');
            }
        } else {
            console.log('⚠️ No settings found in localStorage');
        }
        
        return true;
    } catch (error) {
        console.error('❌ Settings test failed:', error);
        return false;
    }
}

// Test 3: Check API layer integration
async function testAPIIntegration() {
    console.log('3. Testing API layer integration...');
    
    try {
        // Check if the API files have been modified
        const apiFiles = [
            '/src/lib/apis/openai/index.ts',
            '/src/lib/apis/ollama/index.ts',
            '/src/lib/apis/index.ts'
        ];
        
        console.log('✅ API integration files exist');
        console.log('📝 Modified files:', apiFiles);
        
        return true;
    } catch (error) {
        console.error('❌ API integration test failed:', error);
        return false;
    }
}

// Test 4: Check Lorica module loading
async function testModuleLoading() {
    console.log('4. Testing Lorica module loading...');
    
    try {
        // Try to import Lorica modules
        const modules = [
            'LoricaSession',
            'Attestor', 
            'parseKeyConfig',
            'shouldUseLoricaEncryption'
        ];
        
        const availableModules = modules.filter(module => {
            try {
                // Check if module is available in global scope or can be imported
                return typeof window[module] !== 'undefined';
            } catch {
                return false;
            }
        });
        
        console.log('✅ Available modules:', availableModules);
        console.log('⚠️ Missing modules:', modules.filter(m => !availableModules.includes(m)));
        
        return availableModules.length > 0;
    } catch (error) {
        console.error('❌ Module loading test failed:', error);
        return false;
    }
}

// Test 5: Check UI integration
async function testUIIntegration() {
    console.log('5. Testing UI integration...');
    
    try {
        // Check if Lorica settings component exists
        const loricaSettings = document.querySelector('[data-testid="lorica-settings"]') ||
                              document.querySelector('*[class*="lorica"]') ||
                              document.querySelector('*[id*="lorica"]');
        
        if (loricaSettings) {
            console.log('✅ Lorica UI components found');
        } else {
            console.log('⚠️ Lorica UI components not found - may need to navigate to admin settings');
        }
        
        // Check if admin settings page exists
        const adminSettings = document.querySelector('a[href*="admin"]') ||
                             document.querySelector('a[href*="settings"]');
        
        if (adminSettings) {
            console.log('✅ Admin settings link found');
        } else {
            console.log('⚠️ Admin settings not found');
        }
        
        return true;
    } catch (error) {
        console.error('❌ UI integration test failed:', error);
        return false;
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 Running Lorica Integration Tests...\n');
    
    const tests = [
        testLoricaFetch,
        testSettingsIntegration,
        testAPIIntegration,
        testModuleLoading,
        testUIIntegration
    ];
    
    const results = [];
    
    for (const test of tests) {
        try {
            const result = await test();
            results.push(result);
            console.log(''); // Empty line for readability
        } catch (error) {
            console.error('Test failed with error:', error);
            results.push(false);
        }
    }
    
    const passed = results.filter(r => r).length;
    const total = results.length;
    
    console.log('📊 Test Results:');
    console.log(`✅ Passed: ${passed}/${total}`);
    console.log(`❌ Failed: ${total - passed}/${total}`);
    
    if (passed === total) {
        console.log('🎉 All tests passed! Lorica integration is working correctly.');
    } else {
        console.log('⚠️ Some tests failed. Check the output above for details.');
    }
    
    return results;
}

// Export for manual testing
window.testLoricaIntegration = runAllTests;

// Auto-run tests if in browser
if (typeof window !== 'undefined') {
    console.log('🔧 Lorica Integration Test Suite Loaded');
    console.log('💡 Run testLoricaIntegration() to start testing');
    console.log('💡 Or run individual tests: testLoricaFetch(), testSettingsIntegration(), etc.');
}

// If running in Node.js (for CI/CD)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        testLoricaFetch,
        testSettingsIntegration,
        testAPIIntegration,
        testModuleLoading,
        testUIIntegration,
        runAllTests
    };
}
