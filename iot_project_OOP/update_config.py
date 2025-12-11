#!/usr/bin/env python3
# update_config.py
"""
Update config.py file with new settings.
Called from Java UI to save configuration changes.
"""
import sys
import os
import re

def update_config(key, value):
    """
    Update a configuration value in config.py
    
    Args:
        key: Configuration key (e.g., 'EAR_THRESHOLD')
        value: New value (can be str, int, float, bool)
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    
    if not os.path.exists(config_path):
        print(f"ERROR: config.py not found at {config_path}", file=sys.stderr)
        return False
    
    try:
        # Read current config
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Format value for Python
        if isinstance(value, bool):
            value_str = 'True' if value else 'False'
        elif isinstance(value, str):
            value_str = f'"{value}"'
        elif isinstance(value, (int, float)):
            value_str = str(value)
        else:
            value_str = str(value)
        
        # Pattern to match the key assignment
        # Matches: KEY = value or KEY = value  # comment
        pattern = rf'^{re.escape(key)}\s*=\s*.*$'
        
        # Replace the line
        new_line = f'{key} = {value_str}'
        new_content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
        
        if new_content == content:
            # Key not found, append it
            new_content = content.rstrip() + f'\n{new_line}\n'
        
        # Write back
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"SUCCESS: Updated {key} = {value_str}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update config: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 update_config.py <key> <value>", file=sys.stderr)
        sys.exit(1)
    
    key = sys.argv[1]
    value_str = sys.argv[2]
    
    # Parse value type
    if value_str.lower() in ('true', 'false'):
        value = value_str.lower() == 'true'
    elif value_str.replace('.', '').replace('-', '').isdigit():
        if '.' in value_str:
            value = float(value_str)
        else:
            value = int(value_str)
    else:
        value = value_str
    
    success = update_config(key, value)
    sys.exit(0 if success else 1)

