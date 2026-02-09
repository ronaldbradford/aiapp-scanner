# AI App Scanner - Project Structure

**aiapp-scanner** is the main project: the source code, the `aiapp-scanner` CLI command, and what all the docs refer to. The two other repositories are supporting repos for distribution and configuration.

## Repository Structure

```
aiapp-scanner/                   # Main project (this repo) — code, docs, releases
├── aiapp_scanner.py              # Main scanner application
├── scanner_config.json           # Default configuration file
├── setup.py                      # Python package setup
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
├── DEPLOYMENT.md                 # Deployment and Homebrew tap guide
├── LICENSE                       # MIT License
├── Makefile                      # Development shortcuts
├── .gitignore                    # Git ignore rules
├── test_scanner.py               # Test suite
└── com.yourcompany.aiapp-scanner.plist  # LaunchDaemon example

homebrew-aiapp-scanner/          # Tap repo only — Formula for "brew install aiapp-scanner"
└── Formula/
    └── aiapp-scanner.rb         # Homebrew formula (copied from main repo)

aiapp-scanner-config/            # Config repo only — hosts config.json for --update-config
└── config.json                  # Public configuration file (copied from scanner_config.json)
```

## File Descriptions

### Core Files

**aiapp_scanner.py**
- Main Python application
- Contains all scanning logic
- Classes:
  - `ScannerConfig`: Manages configuration loading and updates
  - `ApplicationScanner`: Scans for GUI applications
  - `CLIToolScanner`: Scans for command-line tools
  - `ConfigurationScanner`: Scans for configuration directories
  - `AIAppScanner`: Main orchestrator
- Entry point: `main()` function

**scanner_config.json**
- Default configuration file
- JSON format with three main sections:
  - `applications`: GUI apps to scan for
  - `cli_tools`: CLI tools to detect
  - `config_locations`: Standalone config directories
- Contains `update_url` for remote updates
- Versioned for compatibility tracking

### Documentation

**README.md**
- Primary documentation
- Installation instructions
- Usage examples
- Configuration format
- Output format
- Privacy considerations

**QUICKSTART.md**
- Abbreviated guide for new users
- Common scenarios
- Troubleshooting
- Examples

**DEPLOYMENT.md**
- Complete Homebrew tap setup guide
- Release process
- Configuration hosting options
- MDM deployment
- Best practices

### Setup Files

**setup.py**
- Python package configuration
- Defines entry points
- Package metadata
- Dependencies (none currently!)
- Data files installation

**Makefile**
- Development shortcuts
- Common commands:
  - `make install`: Local installation
  - `make test`: Run tests
  - `make run`: Quick scan
  - `make clean`: Remove build artifacts

### Testing

**test_scanner.py**
- Automated test suite
- Tests various command-line options
- Validates JSON output
- Checks configuration creation

### Packaging

**aiapp-scanner.rb**
- Homebrew formula
- Defines installation process
- Sets up configuration locations
- Includes post-install instructions
- Test commands

**com.yourcompany.aiapp-scanner.plist**
- LaunchDaemon configuration
- Scheduled execution
- Logging setup
- Example for users to customize

## Configuration File Format

```json
{
  "version": "1.1",
  "update_url": "https://example.com/config.json",
  "applications": [
    {
      "name": "AppName.app",
      "vendor": "VendorName",
      "type": "gui",
      "bundle_id": "com.vendor.app"
    }
  ],
  "cli_tools": [
    {
      "name": "toolname",
      "vendor": "VendorName",
      "version_cmd": ["toolname", "--version"],
      "config_paths": ["~/.config/toolname"]
    }
  ],
  "config_locations": [
    {
      "name": "ServiceName",
      "paths": ["~/.service", "~/.config/service"]
    }
  ]
}
```

## Output Format

```json
{
  "scan_metadata": {
    "timestamp": "ISO 8601 datetime",
    "scanner_version": "0.1.0",
    "hostname": "computer-name",
    "os_version": "14.2.1",
    "config_version": "1.1",
    "user": "username"
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
          "path": "/Users/user/.config/claude",
          "exists": true,
          "type": "directory",
          "file_count": 3,
          "files": ["config.json", "history.db"]
        }
      ]
    }
  ],
  "configurations": [
    {
      "type": "configuration",
      "name": "OpenAI",
      "path": "/Users/user/.openai",
      "exists": true,
      "file_count": 2,
      "files": ["config", "credentials"]
    }
  ],
  "summary": {
    "total_applications": 5,
    "total_cli_tools": 3,
    "total_configurations": 2
  }
}
```

## Development Workflow

### Local Development

1. Clone repository
2. Make changes to `aiapp_scanner.py`
3. Test with `python3 aiapp_scanner.py --pretty`
4. Run test suite: `python test_scanner.py`
5. Commit changes

### Creating a Release

1. Update version numbers:
   - `setup.py`: `version="0.2.0"`
   - `aiapp_scanner.py`: `'scanner_version': '0.2.0'`

2. Update CHANGELOG (if you create one)

3. Commit version bump:
```bash
git commit -am "Bump version to 0.2.0"
```

4. Create and push tag:
```bash
git tag v0.2.0
git push origin main --tags
```

5. Create release tarball:
```bash
git archive --format=tar.gz --prefix=aiapp-scanner-0.2.0/ \
  --output=aiapp-scanner-0.2.0.tar.gz v0.2.0
```

6. Calculate SHA256:
```bash
shasum -a 256 aiapp-scanner-0.2.0.tar.gz
```

7. Update Homebrew formula in tap repository

8. Create GitHub release with tarball

### Updating Configuration

1. Edit configuration in separate repo
2. Validate JSON: `cat config.json | jq .`
3. Commit and push
4. Update version number in config
5. Users update with `aiapp-scanner --update-config`

## Installation Locations

### Homebrew Installation

**Binary:**
```
/usr/local/bin/aiapp-scanner
```

**Configuration:**
```
/usr/local/etc/aiapp-scanner/config.json  # System config
~/.config/aiapp-scanner/config.json       # User config (takes precedence)
```

**Logs (if using LaunchDaemon):**
```
/var/log/aiapp-scanner.log
/var/log/aiapp-scanner.error.log
/var/log/aiapp-scanner-latest.json
```

### Manual Installation

**Binary:**
```
~/.local/bin/aiapp-scanner
```

**Configuration:**
```
./scanner_config.json          # Current directory
~/.config/aiapp-scanner/config.json
```

## Dependencies

**Runtime:**
- Python 3.8+
- Standard library only (no external packages!)

**Development:**
- black (formatting)
- flake8 (linting)

**Distribution:**
- setuptools
- Homebrew (for tap distribution)

## Security Considerations

1. **No credentials stored**: Scanner doesn't read config file contents
2. **Limited file listing**: Max 20 files shown per directory
3. **No network by default**: Only when `--update-config` used
4. **No data transmission**: Local scanning only
5. **Timeout protection**: Version commands timeout after 5 seconds

## Extending the Scanner

### Adding New Detection Methods

1. Create new scanner class in `aiapp_scanner.py`
2. Follow existing patterns (`ApplicationScanner`, etc.)
3. Update `AIAppScanner.scan()` to include new scanner
4. Add results to output JSON
5. Document in README

### Adding New Configuration Fields

1. Add field to config JSON schema (e.g. in scanner_config.json)
2. Use field in relevant scanner class
4. Document field in README
5. Update config version number

### Custom Output Formats

The scanner outputs JSON. To add other formats:

1. Create formatter function:
```python
def format_as_csv(results):
    # Convert to CSV
    pass
```

2. Add argument: `--format csv`
3. Call formatter before output
4. Update documentation

## Monitoring and Logging

### LaunchDaemon Logs

Check logs:
```bash
tail -f /var/log/aiapp-scanner.log
tail -f /var/log/aiapp-scanner.error.log
```

### Manual Logging

Redirect output:
```bash
aiapp-scanner --pretty > ~/scan-$(date +%Y%m%d).json 2>&1
```

### System Logs

Check system logs:
```bash
log show --predicate 'process == "aiapp-scanner"' --last 1h
```

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Submit pull request

## License

MIT License - See LICENSE file
