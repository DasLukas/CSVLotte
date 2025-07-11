#!/usr/bin/env python3
"""
Script to embed README.md content as a Python string for use in built executables.
This ensures the README content is always available even if the file can't be found.
"""

import os
import sys

def embed_readme():
    """Convert README.md to a Python string and save it."""
    readme_path = "README.md"
    output_path = "src/csvlotte/utils/embedded_readme.py"
    
    if not os.path.exists(readme_path):
        print(f"Error: {readme_path} not found")
        return False
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Escape the content for Python string
        escaped_content = repr(readme_content)
        
        python_code = f'''"""
Embedded README.md content for CSVLotte application.
This file is automatically generated by embed_readme.py during build.
"""

README_CONTENT = {escaped_content}
'''
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"Successfully embedded README.md content in {output_path}")
        return True
        
    except Exception as e:
        print(f"Error embedding README.md: {e}")
        return False

if __name__ == "__main__":
    success = embed_readme()
    sys.exit(0 if success else 1)
