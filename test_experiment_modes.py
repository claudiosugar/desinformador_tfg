#!/usr/bin/env python3
"""
Test Experiment Modes
Tests the different experiment modes without requiring X login or Gemini API
"""

import sys
import os

# Mock config for testing
class MockConfig:
    GEMINI_API_KEY = 'test-key'
    EXPERIMENT_MODE = 'default'
    LOG_EXPERIMENT_DATA = False
    EXPERIMENT_LOG_FILE = './data/experiment_log.json'

sys.modules['config'] = MockConfig()

# Now import the GeminiAI class
from src.gemini_ai import GeminiAI

def test_language_detection():
    """Test language detection"""
    print("Testing language detection...")
    ai = GeminiAI()
    
    # Test Spanish
    spanish_text = "Hola, esto es una prueba en español"
    assert ai.detect_language(spanish_text) == 'spanish', "Failed to detect Spanish"
    print("✓ Spanish detection works")
    
    # Test English
    english_text = "Hello, this is a test in English"
    assert ai.detect_language(english_text) == 'english', "Failed to detect English"
    print("✓ English detection works")

def test_available_modes():
    """Test that all modes are available"""
    print("\nTesting available modes...")
    ai = GeminiAI()
    
    expected_modes = ['default', 'emotional', 'authority', 'partial_truth',
                      'whataboutism', 'source_confusion', 'conspiracy']
    
    assert ai.available_modes == expected_modes, "Available modes mismatch"
    print(f"✓ All {len(expected_modes)} modes available: {', '.join(expected_modes)}")

def test_random_mode():
    """Test random mode selection"""
    print("\nTesting random mode selection...")
    ai = GeminiAI()
    
    # Generate several random modes
    modes = [ai.get_random_mode() for _ in range(10)]
    
    # Check all returned modes are valid
    for mode in modes:
        assert mode in ai.available_modes, f"Invalid mode returned: {mode}"
    
    print(f"✓ Random mode selection works (sampled modes: {set(modes)})")

def test_prompts_for_all_modes():
    """Test that prompts can be generated for all modes in both languages"""
    print("\nTesting prompt generation for all modes...")
    ai = GeminiAI()
    
    test_tweet = "This is a test tweet about climate change"
    test_author = "testuser"
    
    for mode in ai.available_modes:
        # Test English
        prompt_en = ai.get_prompt_for_mode(mode, 'english', test_tweet, test_author)
        assert len(prompt_en) > 0, f"Empty prompt for mode {mode} (English)"
        assert test_tweet in prompt_en, f"Tweet text not in prompt for mode {mode}"
        
        # Test Spanish
        prompt_es = ai.get_prompt_for_mode(mode, 'spanish', test_tweet, test_author)
        assert len(prompt_es) > 0, f"Empty prompt for mode {mode} (Spanish)"
        assert test_tweet in prompt_es, f"Tweet text not in prompt for mode {mode}"
        
        print(f"  ✓ {mode:20s} - English and Spanish prompts OK")

def test_prompt_content():
    """Test that prompts contain mode-specific keywords"""
    print("\nTesting mode-specific prompt content...")
    ai = GeminiAI()
    
    test_cases = {
        'emotional': ['emocional', 'emotional', 'miedo', 'fear', 'ira', 'anger'],
        'authority': ['estudios', 'studies', 'experto', 'expert', 'ciencia', 'science'],
        'partial_truth': ['verdad', 'truth', 'hecho', 'fact'],
        'whataboutism': ['qué hay de', 'what about', 'pero'],
        'source_confusion': ['dijo', 'said', 'confesó', 'admitted'],
        'conspiracy': ['oculta', 'hidden', 'agenda', 'conspiración', 'conspiracy']
    }
    
    for mode, keywords in test_cases.items():
        prompt_en = ai.get_prompt_for_mode(mode, 'english', "test", "user")
        prompt_es = ai.get_prompt_for_mode(mode, 'spanish', "test", "user")
        
        # Check if at least one keyword appears in the prompts
        combined_prompt = (prompt_en + prompt_es).lower()
        has_keyword = any(keyword.lower() in combined_prompt for keyword in keywords)
        
        assert has_keyword, f"Mode '{mode}' prompt missing expected keywords: {keywords}"
        print(f"  ✓ {mode:20s} - Contains mode-specific keywords")

def test_character_limit_mention():
    """Test that all prompts mention the 280 character limit"""
    print("\nTesting character limit mentions in prompts...")
    ai = GeminiAI()
    
    for mode in ai.available_modes:
        prompt_en = ai.get_prompt_for_mode(mode, 'english', "test", "user")
        prompt_es = ai.get_prompt_for_mode(mode, 'spanish', "test", "user")
        
        assert '280' in prompt_en, f"Mode '{mode}' English prompt missing 280 char limit"
        assert '280' in prompt_es, f"Mode '{mode}' Spanish prompt missing 280 char limit"
    
    print(f"✓ All prompts mention 280 character limit")

def test_hashtag_exclusion():
    """Test that all prompts exclude #desinfo_uib hashtag"""
    print("\nTesting hashtag exclusion in prompts...")
    ai = GeminiAI()
    
    for mode in ai.available_modes:
        prompt_en = ai.get_prompt_for_mode(mode, 'english', "test", "user")
        prompt_es = ai.get_prompt_for_mode(mode, 'spanish', "test", "user")
        
        assert 'desinfo_uib' in prompt_en.lower(), f"Mode '{mode}' English prompt missing hashtag exclusion"
        assert 'desinfo_uib' in prompt_es.lower(), f"Mode '{mode}' Spanish prompt missing hashtag exclusion"
    
    print(f"✓ All prompts mention #desinfo_uib exclusion")

def main():
    """Run all tests"""
    print("=" * 60)
    print("EXPERIMENT MODES TEST SUITE")
    print("=" * 60)
    
    try:
        test_language_detection()
        test_available_modes()
        test_random_mode()
        test_prompts_for_all_modes()
        test_prompt_content()
        test_character_limit_mention()
        test_hashtag_exclusion()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nExperiment modes are ready to use!")
        print("\nAvailable modes:")
        ai = GeminiAI()
        for i, mode in enumerate(ai.available_modes, 1):
            print(f"  {i}. {mode}")
        print("\nTo use a mode, set EXPERIMENT_MODE in config.py")
        print("Example: EXPERIMENT_MODE = 'emotional'")
        print("\nFor random mode selection (A/B testing):")
        print("Example: EXPERIMENT_MODE = 'random'")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
