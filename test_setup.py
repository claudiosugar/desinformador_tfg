#!/usr/bin/env python3
"""
Test script to verify Disinformation Spreader setup
"""

import sys
import os
import importlib
from src.gemini_ai import GeminiAI
import config

def test_setup():
    """Test all components of the disinformation spreader setup"""
    print('🧪 Testing Disinformation Spreader Setup...\n')
    
    # Test 1: Configuration
    print('1. Testing Configuration...')
    print(f'   - Gemini API Key: {"✅ Set" if config.GEMINI_API_KEY else "❌ Missing"}')
    print(f'   - X Username: {"✅ Set" if config.X_USERNAME else "❌ Missing"}')
    print(f'   - X Password: {"✅ Set" if config.X_PASSWORD else "❌ Missing"}')
    print(f'   - Target Hashtag: {config.TARGET_HASHTAG}')
    print(f'   - Response Interval: {config.RESPONSE_INTERVAL} seconds')
    print()
    
    # Test 2: Gemini AI
    print('2. Testing Gemini AI...')
    try:
        gemini = GeminiAI()
        
        # Test English response
        test_response_en = gemini.generate_disinformation_response(
            'This is a test tweet about climate change',
            'testuser'
        )
        
        # Test Spanish response
        test_response_es = gemini.generate_disinformation_response(
            'Este es un tweet de prueba sobre el cambio climático',
            'testuser'
        )
        
        if test_response_en and test_response_es:
            print('   ✅ Gemini AI is working (English & Spanish)')
            print(f'   📝 English response: "{test_response_en[:80]}..."')
            print(f'   📝 Spanish response: "{test_response_es[:80]}..."')
        else:
            print('   ❌ Gemini AI failed to generate response')
    except Exception as e:
        print(f'   ❌ Gemini AI test failed: {e}')
    print()
    
    # Test 3: Dependencies
    print('3. Testing Dependencies...')
    dependencies = [
        ('playwright', 'playwright'),
        ('google.generativeai', 'google-generativeai'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('selenium', 'selenium')
    ]
    
    for module_name, package_name in dependencies:
        try:
            importlib.import_module(module_name)
            print(f'   ✅ {package_name} is installed')
        except ImportError:
            print(f'   ❌ {package_name} is not installed. Run: pip install {package_name}')
    print()
    
    # Test 4: File Structure
    print('4. Testing File Structure...')
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'src/__init__.py',
        'src/gemini_ai.py',
        'src/x_bot.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f'   ✅ {file_path} exists')
        else:
            print(f'   ❌ {file_path} is missing')
    print()
    
    # Test 5: Python Version
    print('5. Testing Python Version...')
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f'   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} is compatible')
    else:
        print(f'   ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} is too old. Need Python 3.8+')
    print()
    
    print('🎯 Setup Test Complete!')
    print('\n📋 Next Steps:')
    print('1. Run: pip install -r requirements.txt')
    print('2. Run: playwright install chromium')
    print('3. Run: python main.py')

if __name__ == "__main__":
    test_setup()
