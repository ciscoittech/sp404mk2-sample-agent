# Turso MCP Server Setup Guide

## Getting Your Turso API Credentials

The MCP server requires platform-level API credentials, not database-specific tokens.

### 1. Get your Turso API Token
1. Go to [Turso Dashboard](https://turso.tech/app)
2. Click on your profile (top right)
3. Go to "Settings" → "API Tokens"
4. Create a new API token with a descriptive name like "mcp-server"
5. Copy the token (it starts with `ts_`)

### 2. Get your Organization Name
1. In the Turso dashboard, look at the URL
2. It should be: `https://turso.tech/app/[YOUR-ORG-NAME]`
3. Copy your organization name

### 3. Update your .env file
Add these to your .env:
```
TURSO_API_TOKEN=ts_your_actual_api_token_here
TURSO_ORGANIZATION=your-org-name
```

### 4. Update the MCP configuration
Since MCP servers can't directly read .env files, you'll need to either:
- Manually copy the values to the MCP config
- Use a script to inject the values

## Current Database Credentials (for reference)
Your .env already has database-specific credentials:
- `TURSO_URL`: libsql://fafo-notoriouscsv.aws-us-east-1.turso.io
- `TURSO_TOKEN`: Database auth token

These are different from the platform API credentials needed for the MCP server.

## Next Steps
1. Get your platform API token from Turso dashboard
2. Add the credentials to your .env
3. Update the MCP configuration in Claude Desktop
4. Restart Claude Desktop