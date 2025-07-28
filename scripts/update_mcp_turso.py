#!/usr/bin/env python3
"""
Update Claude Desktop MCP configuration with Turso credentials from .env file
"""
import json
import os
from pathlib import Path

def load_env_file():
    """Simple .env file loader"""
    env_path = Path('.env')
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

def update_mcp_config():
    # Load environment variables
    env_vars = load_env_file()
    
    # Get Turso credentials from environment
    turso_api_token = env_vars.get('TURSO_API_TOKEN', '')
    turso_org = env_vars.get('TURSO_ORGANIZATION', '')
    turso_default_db = env_vars.get('TURSO_DEFAULT_DATABASE', '')
    
    # Path to Claude Desktop config
    config_path = Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'
    
    if not config_path.exists():
        print("Error: Claude Desktop configuration not found!")
        return False
    
    # Read current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update Turso configuration
    if 'turso' in config['mcpServers']:
        config['mcpServers']['turso']['env']['TURSO_API_TOKEN'] = turso_api_token
        config['mcpServers']['turso']['env']['TURSO_ORGANIZATION'] = turso_org
        if turso_default_db:
            config['mcpServers']['turso']['env']['TURSO_DEFAULT_DATABASE'] = turso_default_db
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ MCP configuration updated successfully!")
        print(f"   Organization: {turso_org}")
        print(f"   API Token: {turso_api_token[:10]}..." if turso_api_token else "   API Token: Not set")
        print(f"   Default DB: {turso_default_db}" if turso_default_db else "   Default DB: Not set")
        print("\n⚠️  Please restart Claude Desktop for changes to take effect.")
        return True
    else:
        print("Error: Turso MCP server not found in configuration!")
        print("Please add it first using Claude Desktop.")
        return False

if __name__ == "__main__":
    # Check if required credentials exist
    env_vars = load_env_file()
    
    if not env_vars.get('TURSO_API_TOKEN'):
        print("⚠️  TURSO_API_TOKEN not found in .env file")
        print("Please add: TURSO_API_TOKEN=ts_your_token_here")
    
    if not env_vars.get('TURSO_ORGANIZATION'):
        print("⚠️  TURSO_ORGANIZATION not found in .env file")
        print("Please add: TURSO_ORGANIZATION=your-org-name")
    
    if env_vars.get('TURSO_API_TOKEN') and env_vars.get('TURSO_ORGANIZATION'):
        update_mcp_config()