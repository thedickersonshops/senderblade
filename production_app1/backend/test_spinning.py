#!/usr/bin/env python3
"""
Test spinning functionality
"""
from message_spinner import get_message_spinner

def test_basic_spinning():
    spinner = get_message_spinner()
    
    # Test basic spinning
    test_content = "Hello {John|Jane|Bob}, today is a {good|great|wonderful} day!"
    
    print("Original:", test_content)
    
    for i in range(5):
        spun = spinner.spin_text(test_content)
        print(f"Variation {i+1}:", spun)

if __name__ == '__main__':
    test_basic_spinning()