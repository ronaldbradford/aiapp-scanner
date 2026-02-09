# AI App Scanner - Complete Package

## What You Have

A complete, production-ready macOS scanner for detecting AI applications, CLI tools, and configurations. The scanner is:

✅ **Fully functional** - Works standalone with no external dependencies  
✅ **Configurable** - External JSON config can be updated remotely  
✅ **Homebrew-ready** - Includes formula for easy distribution  
✅ **Well-documented** - Multiple guides for different audiences  
✅ **Privacy-conscious** - Only checks presence/versions, not contents  

## Files Included

### Core Application
- **aiapp_scanner.py** (17KB) - Main scanner application
- **scanner_config.json** (3.7KB) - Default configuration with common AI apps
- **setup.py** (1.3KB) - Python package setup
- **test_scanner.py** (2.4KB) - Test suite

### Distribution
- **aiapp-scanner.rb** (1.7KB) - Homebrew formula
- **com.yourcompany.aiapp-scanner.plist** (1.5KB) - LaunchDaemon for scheduled runs

### Documentation
- **README.md** (6.4KB) - Main documentation
- **QUICKSTART.md** (6.0KB) - Quick start guide
- **DEPLOYMENT.md** (6.2KB) - Homebrew tap setup
- **PROJECT_STRUCTURE.md** (8.3KB) - Project architecture

### Development
- **Makefile** (1.9KB) - Development shortcuts
- **.gitignore** - Git ignore rules
- **LICENSE** (1.1KB) - MIT License

## Quick Test

```bash
# Test the scanner (config file required)
python3 aiapp_scanner.py --config scanner_config.json --pretty

# Run full test suite
python3 test_scanner.py
```

## Next Steps to Deploy

### Step 1: Set Up Main Repository

```bash
# Create GitHub repository
gh repo create aiapp-scanner --public --description "macOS AI application scanner"

# Initialize and push
cd /path/to/aiapp-scanner
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/aiapp-scanner.git
git push -u origin main
```

### Step 2: Create Configuration Repository

```bash
# Create separate repo for configuration
gh repo create aiapp-scanner-config --public

cd /path/to/aiapp-scanner-config
cp /path/to/scanner_config.json config.json

# Update the update_url in config.json
vim config.json
# Change: "update_url": "https://raw.githubusercontent.com/yourusername/aiapp-scanner-config/main/config.json"

git init
git add config.json
git commit -m "Initial configuration"
git branch -M main
git remote add origin https://github.com/yourusername/aiapp-scanner-config.git
git push -u origin main
```

### Step 3: Create Homebrew Tap

```bash
# Create tap repository
gh repo create homebrew-aiapp-scanner --public

cd /path/to/homebrew-aiapp-scanner
mkdir Formula
cp /path/to/aiapp-scanner.rb Formula/

# First, create a release in main repo
cd /path/to/aiapp-scanner
git tag v0.1.0
git push origin v0.1.0

# Create tarball
git archive --format=tar.gz --prefix=aiapp-scanner-0.1.0/ \
  --output=aiapp-scanner-0.1.0.tar.gz v0.1.0

# Get SHA256
SHA256=$(shasum -a 256 aiapp-scanner-0.1.0.tar.gz | awk '{print $1}')
echo "SHA256: $SHA256"

# Update formula
cd /path/to/homebrew-aiapp-scanner
sed -i '' "s/REPLACE_WITH_ACTUAL_SHA256/$SHA256/" Formula/aiapp-scanner.rb
sed -i '' "s/yourusername/YOUR_GITHUB_USERNAME/g" Formula/aiapp-scanner.rb

git init
git add Formula/
git commit -m "Add aiapp-scanner formula v0.1.0"
git branch -M main
git remote add origin https://github.com/yourusername/homebrew-aiapp-scanner.git
git push -u origin main
```

### Step 4: Test Installation

```bash
# Add your tap
brew tap yourusername/aiapp-scanner

# Install
brew install aiapp-scanner

# Test
aiapp-scanner --pretty
```

### Step 5: Update Default Configuration

In your main repository, update `scanner_config.json` to point to your hosted config:

```json
{
  "version": "1.0",
  "update_url": "https://raw.githubusercontent.com/yourusername/aiapp-scanner-config/main/config.json",
  ...
}
```

Commit and push this change.

## Customization Checklist

Before deploying, customize these items:

- [ ] Replace `yourusername` with your GitHub username in all files
- [ ] Update `Your Name` and `your.email@example.com` in setup.py and LICENSE
- [ ] Update company name in `com.yourcompany.aiapp-scanner.plist`
- [ ] Add any additional apps/tools specific to your organization in scanner_config.json
- [ ] Set up your configuration hosting URL
- [ ] Update README with your repository URLs
- [ ] Test on a clean Mac to verify installation

## Adding New AI Tools to Detect

### For a GUI Application

1. Find the bundle ID:
```bash
mdls -name kMDItemCFBundleIdentifier /Applications/YourApp.app
```

2. Add to config.json:
```json
{
  "name": "YourApp.app",
  "vendor": "VendorName",
  "type": "gui",
  "bundle_id": "com.vendor.yourapp"
}
```

3. Commit and push to config repository
4. Users update with: `aiapp-scanner --update-config`

### For a CLI Tool

1. Test the version command:
```bash
tool-name --version
```

2. Add to config.json:
```json
{
  "name": "tool-name",
  "vendor": "VendorName",
  "version_cmd": ["tool-name", "--version"],
  "config_paths": ["~/.config/tool-name"]
}
```

3. Commit and push
4. Users update with: `aiapp-scanner --update-config`

## Integration Examples

### Send to API Endpoint

```bash
#!/bin/bash
# scan-and-report.sh

API_ENDPOINT="https://api.yourcompany.com/ai-scans"
API_TOKEN="your-token-here"

# Run scan
RESULTS=$(aiapp-scanner --update-config 2>/dev/null)

# POST to API
curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d "$RESULTS"
```

### Save to Network Share

```bash
#!/bin/bash
# scan-to-share.sh

HOSTNAME=$(hostname)
DATE=$(date +%Y%m%d)
SHARE_PATH="/Volumes/CompanyShare/ai-scans"

aiapp-scanner --output "$SHARE_PATH/${HOSTNAME}-${DATE}.json"
```

### Email Results

```bash
#!/bin/bash
# scan-and-email.sh

RESULTS=$(aiapp-scanner --pretty)

echo "$RESULTS" | mail -s "AI Scan Results from $(hostname)" admin@yourcompany.com
```

## Monitoring and Maintenance

### Weekly Tasks
- Check scanner logs: `tail -f /var/log/aiapp-scanner.log`
- Review scan results from organization
- Update configuration if new AI tools are released

### Monthly Tasks
- Review detected applications for policy compliance
- Update scanner if new macOS version released
- Check for scanner updates: `brew upgrade aiapp-scanner`

### As Needed
- Add new AI applications to configuration
- Update Homebrew formula for new scanner versions
- Respond to user issues/questions

## Support Resources

### For End Users
- Send them: **QUICKSTART.md**
- Installation: `brew tap yourusername/aiapp-scanner && brew install aiapp-scanner`
- Basic usage: `aiapp-scanner --pretty`

### For IT Administrators
- Send them: **DEPLOYMENT.md**
- LaunchDaemon setup for automated scanning
- Integration with reporting systems
- Configuration management

### For Developers
- Send them: **PROJECT_STRUCTURE.md** and **README.md**
- Contributing guidelines
- Architecture overview
- Extension patterns

## What This Scanner Detects (Default Configuration)

**GUI Applications:**
- Claude (Anthropic)
- ChatGPT (OpenAI)
- Cursor (Cursor)
- Cody (Sourcegraph)
- Windsurf (Codeium)
- Copilot (GitHub)
- Pieces
- Warp (Terminal with AI)
- Raycast (Launcher with AI)

**CLI Tools:**
- claude (Anthropic)
- aichat (sigoden)
- mods (Charm)
- fabric (danielmiessler)
- sgpt (TheR1D)
- chatgpt (OpenAI)
- copilot (GitHub)
- llm (Simon Willison)

**Configuration Directories:**
- OpenAI
- Anthropic
- Google AI
- Hugging Face
- Ollama
- LM Studio

You can easily add more by editing the configuration file!

## Privacy and Security Notes

The scanner:
- ✅ Only checks if apps/tools are installed
- ✅ Only records version numbers
- ✅ Lists config directory file names (not contents)
- ✅ Does NOT read configuration file contents
- ✅ Does NOT access credentials or API keys
- ✅ Does NOT transmit data (unless you add reporting)
- ✅ Limits directory listings to 20 files

## Troubleshooting

**Scanner not finding apps:**
- Verify app is in /Applications or ~/Applications
- Check bundle ID is correct
- App might be in /System/Applications

**Configuration update fails:**
- Check URL is accessible: `curl -L https://your-config-url`
- Validate JSON: `cat config.json | jq .`
- Check network connectivity

**Homebrew installation fails:**
- Run: `brew audit --strict aiapp-scanner`
- Check formula URL is accessible
- Verify SHA256 matches tarball

## Success Metrics

Track these to measure deployment success:
- Number of Macs with scanner installed
- Scan completion rate (daily/weekly)
- Number of AI tools detected per machine
- Configuration update success rate
- Time to detect new AI tool rollout

## Future Enhancements

Potential additions:
- [ ] Browser extension detection (Chrome, Firefox)
- [ ] VS Code extension scanning
- [ ] License/subscription status checking
- [ ] Usage statistics (if apps provide APIs)
- [ ] Policy compliance checking
- [ ] Automated remediation
- [ ] Web dashboard for viewing results
- [ ] Alert on new tool detection

## Getting Help

- GitHub Issues: File bug reports and feature requests
- Email: your.email@example.com
- Documentation: All markdown files included
- Community: Create discussions in GitHub

---

## You're Ready to Deploy! 🚀

You now have everything needed to:
1. ✅ Scan Macs for AI applications
2. ✅ Distribute via Homebrew
3. ✅ Manage configuration remotely
4. ✅ Integrate with your systems
5. ✅ Track AI tool usage across your organization

The scanner is production-ready and fully documented. Start with a small pilot group, gather feedback, then roll out organization-wide!
