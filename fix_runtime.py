#!/usr/bin/env python3
"""
Fix runtime field handling in movie endpoints.
"""
import re

def fix_runtime_handling():
    """Add runtime processing to both analysis and details endpoints"""
    
    with open('backend/app/api/routes/movies.py', 'r') as f:
        content = f.read()
    
    # Pattern to find where year processing happens but runtime processing is missing
    # Look for year processing followed immediately by Movie creation
    year_pattern = r'(year_int = 2023\n\s+# Create Movie object from enhanced details)'
    runtime_code = '''year_int = 2023
                
                # Handle runtime field - extract numeric value
                runtime_data = enhanced_details.get('runtime') or enhanced_details.get('Runtime')
                runtime_int = None
                if runtime_data:
                    try:
                        # Extract numbers from runtime string (e.g., "169 min" -> 169)
                        import re
                        runtime_match = re.search(r'\\d+', str(runtime_data))
                        if runtime_match:
                            runtime_int = int(runtime_match.group())
                    except (ValueError, TypeError):
                        runtime_int = None
                
                # Create Movie object from enhanced details'''
    
    # Replace the pattern
    new_content = re.sub(year_pattern, runtime_code, content)
    
    if new_content != content:
        with open('backend/app/api/routes/movies.py', 'w') as f:
            f.write(new_content)
        print("✅ Runtime processing added to movie endpoints")
        return True
    else:
        print("❌ No pattern matches found")
        return False

if __name__ == "__main__":
    fix_runtime_handling()
