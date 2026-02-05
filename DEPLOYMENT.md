# Homebrew Tap Deployment Guide

This guide walks you through creating and maintaining a Homebrew tap for aiapp-scanner.

## Step 1: Create the Homebrew Tap Repository

1. Create a new GitHub repository named `homebrew-aiapp-scanner`
   - Repository name MUST start with `homebrew-` for Homebrew to recognize it
   - Make it public
   - Add a README

2. Clone the repository:
```bash
git clone https://github.com/ronaldbradford/homebrew-aiapp-scanner.git
cd homebrew-aiapp-scanner
```

## Step 2: Prepare the Formula

1. Copy the formula file:
```bash
cp /path/to/aiapp-scanner.rb Formula/aiapp-scanner.rb
```

2. Create a release of your main scanner repository:
```bash
cd /path/to/aiapp-scanner
git tag v0.1.0
git push origin v0.1.0
```

3. Create a release tarball:
```bash
git archive --format=tar.gz --prefix=aiapp-scanner-0.1.0/ \
  --output=aiapp-scanner-0.1.0.tar.gz v0.1.0
```

4. Calculate SHA256:
```bash
shasum -a 256 aiapp-scanner-0.1.0.tar.gz
```

5. Upload the tarball to your GitHub release:
   - Go to your scanner repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag: v0.1.0
   - Upload the tarball
   - Publish release

6. Update the formula with the correct URL and SHA256:
```ruby
url "https://github.com/ronaldbradford/aiapp-scanner/archive/v0.1.0.tar.gz"
sha256 "PASTE_SHA256_HERE"
```

## Step 3: Commit and Push

```bash
cd homebrew-aiapp-scanner
git add Formula/aiapp-scanner.rb
git commit -m "Add aiapp-scanner formula v0.1.0"
git push origin main
```

## Step 4: Test Installation

```bash
# Add your tap
brew tap ronaldbradford/aiapp-scanner

# Install your formula
brew install aiapp-scanner

# Test it works
aiapp-scanner --pretty
```

## Step 5: Updating the Formula

When you release a new version:

1. Create new release in main repository:
```bash
cd /path/to/aiapp-scanner
# Update version in setup.py and aiapp_scanner.py
git commit -am "Bump version to 0.2.0"
git tag v1.1.0
git push origin v1.1.0
```

2. Create tarball and get SHA256:
```bash
git archive --format=tar.gz --prefix=aiapp-scanner-1.1.0/ \
  --output=aiapp-scanner-1.1.0.tar.gz v1.1.0
shasum -a 256 aiapp-scanner-1.1.0.tar.gz
```

3. Update formula:
```bash
cd homebrew-aiapp-scanner
# Edit Formula/aiapp-scanner.rb
# Update url to v1.1.0
# Update sha256 with new hash
git commit -am "Update aiapp-scanner to 1.1.0"
git push origin main
```

4. Users update with:
```bash
brew update
brew upgrade aiapp-scanner
```

## Configuration File Hosting

### Option 1: GitHub Raw URL (Recommended)

1. Create a separate repository for configuration:
```bash
git clone https://github.com/ronaldbradford/aiapp-scanner-config.git
cd aiapp-scanner-config
cp /path/to/scanner_config.json config.json
git add config.json
git commit -m "Initial configuration"
git push origin main
```

2. The public URL will be:
```
https://raw.githubusercontent.com/ronaldbradford/aiapp-scanner-config/main/config.json
```

3. Update this URL in your `scanner_config.json`:
```json
{
  "version": "1.1",
  "update_url": "https://raw.githubusercontent.com/ronaldbradford/aiapp-scanner-config/main/config.json",
  ...
}
```

### Option 2: GitHub Pages

1. Enable GitHub Pages in your config repository settings
2. Access via: `https://ronaldbradford.github.io/aiapp-scanner-config/config.json`

### Option 3: S3 Bucket

1. Create public S3 bucket
2. Upload config.json
3. Set public read permissions
4. Use S3 URL in update_url

## Distribution Options

### Public Distribution

Your tap is public, anyone can install:
```bash
brew tap ronaldbradford/aiapp-scanner
brew install aiapp-scanner
```

### Private/Enterprise Distribution

For internal use only:

1. Make tap repository private
2. Users need GitHub authentication:
```bash
brew tap ronaldbradford/aiapp-scanner
# Homebrew will prompt for GitHub credentials
brew install aiapp-scanner
```

3. Or use GitHub token:
```bash
export HOMEBREW_GITHUB_API_TOKEN=your_token
brew tap ronaldbradford/aiapp-scanner
brew install aiapp-scanner
```

## MDM Deployment

For enterprise deployment via MDM (Jamf, Intune, etc.):

1. Create a package installer:
```bash
# Install locally first
brew install aiapp-scanner

# Create pkg
pkgbuild --root /usr/local/Cellar/aiapp-scanner/0.1.0 \
  --identifier com.yourcompany.aiapp-scanner \
  --version 0.1.0 \
  --install-location /usr/local/Cellar/aiapp-scanner/0.1.0 \
  aiapp-scanner-0.1.0.pkg
```

2. Deploy via MDM with post-install script:
```bash
#!/bin/bash
# Create symlinks
ln -sf /usr/local/Cellar/aiapp-scanner/0.1.0/bin/aiapp-scanner /usr/local/bin/
# Copy configuration
mkdir -p /usr/local/etc/aiapp-scanner
cp /path/to/config.json /usr/local/etc/aiapp-scanner/
```

## Troubleshooting

### Formula doesn't install

```bash
# Audit the formula
brew audit --strict aiapp-scanner

# Test installation in sandbox
brew install --build-from-source aiapp-scanner
```

### Users can't update config

Check:
1. URL is accessible: `curl -L https://your-config-url.json`
2. JSON is valid: `cat config.json | jq .`
3. URL is correct in formula

### Python version conflicts

Specify Python version in formula:
```ruby
depends_on "python@3.12"
```

## Best Practices

1. **Version all configuration changes**: Tag config repo for traceability
2. **Test before releasing**: Install from tap on clean system
3. **Document breaking changes**: In release notes
4. **Keep SHA256 updated**: Always regenerate for new releases
5. **Maintain backwards compatibility**: In config file format
6. **Use semantic versioning**: MAJOR.MINOR.PATCH

## Example Workflow

```bash
# 1. Make changes to scanner
cd aiapp-scanner
vim aiapp_scanner.py
# Update version in setup.py

# 2. Commit and tag
git commit -am "Add new feature"
git tag v1.2.0
git push origin main --tags

# 3. Create release tarball
git archive --format=tar.gz --prefix=aiapp-scanner-1.2.0/ \
  --output=aiapp-scanner-1.2.0.tar.gz v1.2.0

# 4. Get SHA256
SHA256=$(shasum -a 256 aiapp-scanner-1.2.0.tar.gz | cut -d' ' -f1)
echo $SHA256

# 5. Update formula
cd ../homebrew-aiapp-scanner
sed -i '' "s/v[0-9.]*.tar.gz/v1.2.0.tar.gz/" Formula/aiapp-scanner.rb
sed -i '' "s/sha256 \".*\"/sha256 \"$SHA256\"/" Formula/aiapp-scanner.rb

# 6. Commit and push
git commit -am "Update to v1.2.0"
git push origin main

# 7. Test
brew update
brew upgrade aiapp-scanner
aiapp-scanner --pretty
```
