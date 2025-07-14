#!/usr/bin/env python3
"""
Script to fix Python 2 to Python 3 compatibility issues in MedFact project.
"""

import os
import re
import glob

def fix_urllib_imports(file_path):
    """Fix urllib import statements for Python 3."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix urllib.urlopen import
    content = re.sub(
        r'from urllib import urlopen',
        'from urllib.request import urlopen',
        content
    )
    
    return content

def fix_print_statements(file_path):
    """Fix print(statements for Python 3.""")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix print(statements without parentheses)
    # This regex looks for print(followed by space and captures the rest)
    content = re.sub(
        r"print\s+([^(].*?)(?=\n|$)",
        r"print(\1)",
        content,
        flags=re.MULTILINE
    )
    
    return content

def backup_file(file_path):
    """Create a backup of the original file."""
    backup_path = file_path + '.backup'
    with open(file_path, 'r') as original:
        with open(backup_path, 'w') as backup:
            backup.write(original.read())
    print(f"Created backup: {backup_path}")

def fix_file(file_path):
    """Fix a single Python file."""
    print(f"Processing: {file_path}")
    
    # Create backup
    backup_file(file_path)
    
    # Read and fix content
    content = None
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Apply fixes
    content = fix_urllib_imports(file_path)
    content = fix_print_statements(file_path)
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed {file_path}")
    else:
        print(f"  - No changes needed for {file_path}")

def main():
    """Main function to fix all Python files."""
    print("Fixing Python 2 to Python 3 compatibility issues...")
    
    # Get all Python files
    python_files = glob.glob("*.py")
    
    for file_path in python_files:
        if file_path.endswith('.backup'):
            continue
        fix_file(file_path)
    
    print("\nDone! Original files have been backed up with .backup extension.")
    print("\nNext steps:")
    print("1. Test the application with: python medfact.py")
    print("2. Install spaCy language model: python -m spacy download en_core_web_sm")
    print("3. Check for any remaining API compatibility issues")

if __name__ == "__main__":
    main()