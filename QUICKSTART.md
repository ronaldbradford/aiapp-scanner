# Quick Start Guide

## Installation

### For End Users (Homebrew)

```bash
# Add the tap
brew tap ronaldbradford/aiapp-scanner

# Install
brew install aiapp-scanner

# Verify installation
aiapp-scanner --pretty
```

### For Developers

```bash
# Clone the repository
git clone https://github.com/yourusername/aiapp-scanner.git
cd aiapp-scanner

# Install in development mode
pip install -e .

# Or run directly
python aiapp_scanner.py --pretty
```

## Basic Usage

### Run a Quick Scan

```bash
aiapp-scanner --pretty
```

This will output JSON showing all detected AI apps, CLI tools, and configurations.

### Save Results to a File

```bash
aiapp-scanner --output ~/Desktop/my-scan.json --pretty
```

### Update Configuration Before Scanning

```bash
# Update from default URL in config
aiapp-scanner --update-config --pretty

# Or specify a custom URL
aiapp-scanner --update-config --update-url https://your-url.com/config.json
```

## Common Scenarios

### First Time Setup

1. Install via Homebrew (see above)

2. Use a config file (required). Either use the included one or copy it:
```bash
mkdir -p ~/.config/aiapp-scanner
cp scanner_config.json ~/.config/aiapp-scanner/config.json
```

3. Edit the config if needed:
```bash
vim ~/.config/aiapp-scanner/config.json
```

4. Run your first scan:
```bash
aiapp-scanner --pretty
```

### Setting Up Automated Scanning

1. Copy the launchd plist:
```bash
sudo cp com.yourcompany.aiapp-scanner.plist \
  /Library/LaunchDaemons/
```

2. Edit it with your settings:
```bash
sudo vim /Library/LaunchDaemons/com.yourcompany.aiapp-scanner.plist
```

3. Load it:
```bash
sudo launchctl load /Library/LaunchDaemons/com.yourcompany.aiapp-scanner.plist
```

4. Check it's running:
```bash
sudo launchctl list | grep aiapp-scanner
```

### Integrating with Your Reporting System

```bash
# Scan and POST to your API
RESULTS=$(aiapp-scanner)
curl -X POST https://api.yourcompany.com/ai-scans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d "$RESULTS"
```

Or create a wrapper script:

```bash
#!/bin/bash
# scan-and-report.sh

# Run scan with config update
RESULTS=$(aiapp-scanner --update-config 2>/dev/null)

# Check if scan succeeded
if [ $? -eq 0 ]; then
    # Send to your API
    curl -s -X POST https://api.yourcompany.com/ai-scans \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${API_TOKEN}" \
      -d "$RESULTS"

    echo "Scan completed and reported"
else
    echo "Scan failed" >&2
    exit 1
fi
```

## Understanding the Output

The scanner produces JSON with these main sections:

### scan_metadata
Information about the scan itself:
- timestamp: When the scan ran
- hostname: Name of the Mac
- os_version: macOS version
- user: Current user

### applications
GUI apps found in /Applications:
```json
{
  "name": "Claude.app",
  "vendor": "Anthropic",
  "version": "1.2.3",
  "path": "/Applications/Claude.app"
}
```

### cli_tools
Command-line tools found in PATH:
```json
{
  "name": "claude",
  "vendor": "Anthropic",
  "path": "/usr/local/bin/claude",
  "version": "claude 1.0.0",
  "configurations": [...]
}
```

### configurations
Standalone config directories:
```json
{
  "name": "OpenAI",
  "path": "/Users/you/.openai",
  "file_count": 2,
  "files": ["config", "credentials"]
}
```

## Customizing the Configuration

### Add a New Application

Edit your config file (`~/.config/aiapp-scanner/config.json`):

```json
{
  "applications": [
    {
      "name": "NewAI.app",
      "vendor": "NewCompany",
      "type": "gui",
      "bundle_id": "com.newcompany.newai"
    }
  ]
}
```

### Add a New CLI Tool

```json
{
  "cli_tools": [
    {
      "name": "newai-cli",
      "vendor": "NewCompany",
      "version_cmd": ["newai-cli", "--version"],
      "config_paths": ["~/.config/newai"]
    }
  ]
}
```

### Finding Bundle IDs

To find an app's bundle ID:

```bash
# Method 1: Using osascript
osascript -e 'id of app "Claude"'

# Method 2: Using mdls
mdls -name kMDItemCFBundleIdentifier /Applications/Claude.app

# Method 3: Reading Info.plist
/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" \
  /Applications/Claude.app/Contents/Info.plist
```

## Troubleshooting

### Scanner doesn't find an app

1. Check the app is actually installed:
```bash
ls -la /Applications/*.app | grep -i appname
```

2. Verify bundle ID:
```bash
mdls -name kMDItemCFBundleIdentifier /Applications/YourApp.app
```

3. Add to config with correct bundle ID

### Configuration update fails

1. Test URL is accessible:
```bash
curl -L https://your-config-url.json
```

2. Validate JSON:
```bash
curl -L https://your-config-url.json | jq .
```

3. Check permissions on config directory:
```bash
ls -la ~/.config/aiapp-scanner/
```

### Permission denied errors

Some directories require elevated permissions:

```bash
# Run with sudo if needed (be careful!)
sudo aiapp-scanner --pretty
```

### CLI tool not detected

1. Check it's in PATH:
```bash
which tool-name
```

2. Verify version command works:
```bash
tool-name --version
```

3. Update config with correct version command

## Advanced Usage

### Custom Configuration Location

```bash
aiapp-scanner --config /path/to/custom/config.json --pretty
```

### Multiple Scans in Parallel

```bash
# Scan all users (requires sudo)
for user in $(ls /Users); do
    sudo -u $user aiapp-scanner --output /tmp/scan-$user.json &
done
wait
```

### Compare Scans Over Time

```bash
#!/bin/bash
# compare-scans.sh

# Run new scan
aiapp-scanner --output /tmp/scan-new.json

# Compare with previous
if [ -f /tmp/scan-prev.json ]; then
    echo "New apps:"
    jq -r '.applications[].name' /tmp/scan-new.json | \
      grep -v -f <(jq -r '.applications[].name' /tmp/scan-prev.json)
fi

# Save for next comparison
cp /tmp/scan-new.json /tmp/scan-prev.json
```

## Getting Help

- Check README: `cat /usr/local/share/aiapp-scanner/README.md`
- View all options: `aiapp-scanner --help`
- Open issues: https://github.com/yourusername/aiapp-scanner/issues

## Next Steps

1. Set up automated daily scans
2. Integrate with your reporting system
3. Customize configuration for your environment
4. Deploy to all organizational Macs
