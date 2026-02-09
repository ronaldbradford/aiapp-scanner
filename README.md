# AI App Scanner for macOS

A flexible scanner that detects installed AI applications, CLI tools, and configurations on macOS systems. Perfect for IT administrators who need to track AI tool usage across their organization.

## Features

- **GUI Application Detection**: Scans for installed AI desktop applications (Claude, ChatGPT, Cursor, VSCode, etc.)
- **VSCode Extension Detection**: Detects AI extensions in VSCode (e.g. Roo Code) from `~/.vscode/extensions` and `~/.vscode-insiders/extensions`
- **CLI Tool Discovery**: Detects command-line AI tools in PATH
- **Configuration Tracking**: Identifies configuration files and directories
- **External Configuration**: Uses JSON configuration file that can be updated from a public URL
- **JSON Output**: Structured output for easy integration with reporting systems

## Installation

This repository (**aiapp-scanner**) is the main project. The `aiapp-scanner` command is installed from here or via the Homebrew tap.

### Via Homebrew (Recommended)

```bash
brew tap yourusername/aiapp-scanner
brew install aiapp-scanner
```

*(The tap uses the separate repo `homebrew-aiapp-scanner`, which contains only the formula.)*

### Manual Installation

```bash
git clone https://github.com/yourusername/aiapp-scanner.git
cd aiapp-scanner
pip install .
```

### Development Setup (venv)

Use a virtual environment to isolate dependencies and install the package in editable mode:

```bash
git clone https://github.com/yourusername/aiapp-scanner.git
cd aiapp-scanner
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -e .
```

The `venv/` directory is in `.gitignore`. After activation, `python` and `pip` use the venv, and the `aiapp-scanner` command is available. Editable install (`-e`) lets you run code changes without reinstalling.

## Usage

### Basic Scan

```bash
aiapp-scanner
```

### Save Results to File

```bash
aiapp-scanner --output scan_results.json --pretty
```

### Update Configuration Before Scanning

```bash
aiapp-scanner --update-config
```

### Use Custom Configuration File

```bash
aiapp-scanner --config /path/to/custom_config.json
```

A configuration file is required. Use the included `scanner_config.json`, or copy it to `~/.config/aiapp-scanner/config.json`, or pass `--config PATH`.

### Update Configuration from Custom URL

```bash
aiapp-scanner --update-config --update-url https://your-domain.com/scanner-config.json
```

## Configuration File Format

The scanner uses a JSON configuration file with four main sections: `applications`, `vscode_extensions`, `cli_tools`, and `config_locations`.

```json
{
  "version": "1.0",
  "update_url": "https://example.com/scanner-config.json",
  "applications": [
    {
      "name": "Claude.app",
      "vendor": "Anthropic",
      "type": "gui",
      "bundle_id": "com.anthropic.claude"
    }
  ],
  "cli_tools": [
    {
      "name": "claude",
      "vendor": "Anthropic",
      "version_cmd": ["claude", "--version"],
      "config_paths": ["~/.config/claude"]
    }
  ],
  "vscode_extensions": [
    {
      "id": "roocode.roocode",
      "name": "Roo Code",
      "vendor": "Roo"
    }
  ],
  "config_locations": [
    {
      "name": "OpenAI",
      "paths": ["~/.openai", "~/.config/openai"]
    }
  ]
}
```

### Configuration Locations

The scanner looks for configuration files in the following order:

1. Path specified with `--config` flag
2. `./scanner_config.json` (current directory)
3. `~/.config/aiapp-scanner/config.json` (user config)
4. `/usr/local/etc/aiapp-scanner/config.json` (system config)

## Output Format

```json
{
  "scan_metadata": {
    "timestamp": "2025-02-05T10:30:00",
    "scanner_version": "0.1.0",
    "hostname": "macb3f2a1b4c",
    "os_version": "14.2.1",
    "config_version": "1.1",
    "user": "user8e7d6c5b"
  },
  "applications": [
    {
      "type": "application",
      "name": "Claude.app",
      "vendor": "Anthropic",
      "version": "1.2.3",
      "bundle_version": "100",
      "bundle_id": "com.anthropic.claude",
      "path": "/Applications/Claude.app",
      "install_location": "/Applications"
    }
  ],
  "cli_tools": [
    {
      "type": "cli_tool",
      "name": "claude",
      "vendor": "Anthropic",
      "path": "/usr/local/bin/claude",
      "version": "claude 1.0.0",
      "configurations": [
        {
          "path": "/Users/username/.config/claude",
          "exists": true,
          "type": "directory",
          "file_count": 3,
          "files": ["config.json", "history.db", "auth.token"]
        }
      ]
    }
  ],
  "configurations": [
    {
      "type": "configuration",
      "name": "OpenAI",
      "path": "/Users/username/.openai",
      "exists": true,
      "file_count": 2,
      "files": ["config", "credentials"]
    }
  ],
  "vscode_extensions": [
    {
      "type": "vscode_extension",
      "extension_id": "roocode.roocode",
      "name": "Roo Code",
      "vendor": "Roo",
      "version": "1.0.0",
      "path": "/Users/username/.vscode/extensions/roocode.roocode-1.0.0",
      "vscode_type": "vscode"
    }
  ],
  "summary": {
    "total_applications": 5,
    "total_cli_tools": 3,
    "total_configurations": 2,
    "total_vscode_extensions": 1
  }
}
```

## Maintaining the Configuration

### Hosting Your Configuration

Host your configuration JSON file on:
- GitHub (recommended): Use raw.githubusercontent.com URL
- S3 bucket with public read access
- Your own web server
- CDN

Example GitHub URL:
```
https://raw.githubusercontent.com/yourusername/aiapp-scanner-config/main/config.json
```

### Adding New Applications

Edit your hosted `config.json` file and add entries to the appropriate section:

**For GUI Apps:**
```json
{
  "name": "NewAI.app",
  "vendor": "VendorName",
  "type": "gui",
  "bundle_id": "com.vendor.newai"
}
```

**For CLI Tools:**
```json
{
  "name": "newai",
  "vendor": "VendorName",
  "version_cmd": ["newai", "--version"],
  "config_paths": ["~/.config/newai"]
}
```

Users can update their local configuration by running:
```bash
aiapp-scanner --update-config
```

## Privacy Considerations

The scanner:
- **Anonymizes identifiers**: `user` and `hostname` in scan output are not PII. Each is the first 4 characters plus the last 8 characters of an MD5 hash of the real value (hostname has `.local` stripped first). Same machine and user always produce the same anonymized IDs, so a SaaS can correlate repeat scans without storing usernames or hostnames.
- **Sanitizes paths**: Any path in the output that contains the current user’s home directory (e.g. `/Users/username`) is rewritten to use the same anonymized user ID (e.g. `/Users/user8e7d6c5b`), so path structure is preserved without exposing the real username.
- Only checks for presence and versions of applications
- Lists configuration directory contents (file names only, not contents)
- Does NOT read configuration file contents
- Does NOT transmit any data (local scanning only)
- Limits directory listings to 20 files for privacy

## Compliance Report

A separate program **compliance_report.py** (or `aiapp-compliance-report` when installed) compares scan results against an organization **policy file**: a JSON allowlist of accepted applications, CLI tools, and VSCode extensions, each with supported versions and an optional `supported_until` date. It runs the scanner and produces an **HTML report** with color-coded rows:

- **Green**: Accepted product and version (in allowlist).
- **Yellow**: Accepted product but installed version not in the allowlist.
- **Red**: Product not in the allowlist.

**Policy file format** (see `policy_example.json`):

```json
{
  "applications": [
    {
      "name": "Claude.app",
      "bundle_id": "com.anthropic.claude",
      "supported_versions": [
        { "version": "1.1.1520", "supported_until": "2025-06-01" }
      ]
    }
  ],
  "cli_tools": [
    { "name": "claude", "supported_versions": [{ "version": "2.1.19 (Claude Code)", "supported_until": "2025-06-01" }] }
  ],
  "vscode_extensions": [
    { "id": "roocode.roocode", "supported_versions": [{ "version": "1.0.0", "supported_until": "2025-06-01" }] }
  ]
}
```

**Run the report:**

```bash
python3 compliance_report.py policy_example.json -o compliance_report.html
# Or, if installed:
aiapp-compliance-report policy.json --output report.html
```

Optional: `--scanner-config path/to/scanner_config.json` to use a specific scanner config.

## Integration with Reporting Systems

The JSON output is designed for easy integration. Example with curl:

```bash
# Scan and send results to your API
RESULTS=$(aiapp-scanner)
curl -X POST https://your-api.com/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "$RESULTS"
```

## Scheduled Scanning

### Using launchd (macOS)

Create `/Library/LaunchDaemons/com.yourcompany.aiapp-scanner.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.yourcompany.aiapp-scanner</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/aiapp-scanner</string>
    <string>--update-config</string>
    <string>--output</string>
    <string>/var/log/aiapp-scanner-latest.json</string>
  </array>
  <key>StartInterval</key>
  <integer>86400</integer>
  <key>StandardOutPath</key>
  <string>/var/log/aiapp-scanner.log</string>
  <key>StandardErrorPath</key>
  <string>/var/log/aiapp-scanner.error.log</string>
</dict>
</plist>
```

Load the daemon:
```bash
sudo launchctl load /Library/LaunchDaemons/com.yourcompany.aiapp-scanner.plist
```

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Support

- Issues: https://github.com/yourusername/aiapp-scanner/issues
- Documentation: https://github.com/yourusername/aiapp-scanner/wiki
