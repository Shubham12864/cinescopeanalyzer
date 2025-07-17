#!/usr/bin/env python3
"""
Script to find syntax errors in movie_service.py
"""
import ast
import sys

def check_syntax(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        print(f"File length: {len(content)} characters")
        print(f"Line count: {content.count(chr(10))}")
        
        # Try to parse the file
        try:
            ast.parse(content)
            print("✅ Syntax is valid")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax Error at line {e.lineno}: {e.msg}")
            if e.lineno:
                lines = content.split('\n')
                start = max(0, e.lineno - 5)
                end = min(len(lines), e.lineno + 5)
                print(f"\nContext around line {e.lineno}:")
                for i in range(start, end):
                    marker = ">>> " if i + 1 == e.lineno else "    "
                    print(f"{marker}{i+1:4d}: {lines[i]}")
            return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    check_syntax("backend/app/services/movie_service.py")
