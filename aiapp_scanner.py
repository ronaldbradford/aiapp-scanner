#!/usr/bin/env python
"""
AI Application Scanner for macOS
Scans for installed AI applications, CLI tools, and configurations
"""

import os
import sys
import json
import plistlib
import subprocess
import shutil
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def _anonymize_identifier(value: str) -> str:
    """
    Return a deterministic, PII-safe identifier: first 4 chars + last 8 of MD5.
    Same input always produces the same output for correlation by a SaaS.
    """
    if not value or not value.strip():
        value = 'unknown'
    value = value.strip()
    prefix = value[:4] if len(value) >= 4 else value
    digest = hashlib.md5(value.encode('utf-8')).hexdigest()
    return f"{prefix}{digest[-8:]}"


def _anonymize_hostname(hostname: str) -> str:
    """Strip .local and anonymize like other identifiers."""
    if not hostname:
        return _anonymize_identifier('unknown')
    base = hostname.lower().rstrip('.local') if hostname.lower().endswith('.local') else hostname
    return _anonymize_identifier(base)


def _sanitize_paths_in_output(obj: Any, real_home: str, anonymized_home: str) -> None:
    """
    Recursively replace real user home path with anonymized path in all string
    values (in-place). Removes username PII from paths in scan output.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and real_home in v:
                obj[k] = v.replace(real_home, anonymized_home)
            else:
                _sanitize_paths_in_output(v, real_home, anonymized_home)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str) and real_home in item:
                obj[i] = item.replace(real_home, anonymized_home)
            else:
                _sanitize_paths_in_output(item, real_home, anonymized_home)


class ScannerConfig:
    """Manages scanner configuration from JSON file"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Check in order: current dir, ~/.config, /usr/local/etc
        possible_paths = [
            'scanner_config.json',
            os.path.expanduser('~/.config/aiapp-scanner/config.json'),
            '/usr/local/etc/aiapp-scanner/config.json'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Return user config location as default for new installs
        return os.path.expanduser('~/.config/aiapp-scanner/config.json')

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_path):
            # Create default config
            return self._create_default_config()

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}", file=sys.stderr)
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "version": "1.0",
            "update_url": "https://example.com/scanner-config.json",
            "applications": [
                {
                    "name": "Claude.app",
                    "vendor": "Anthropic",
                    "type": "gui",
                    "bundle_id": "com.anthropic.claude"
                },
                {
                    "name": "ChatGPT.app",
                    "vendor": "OpenAI",
                    "type": "gui",
                    "bundle_id": "com.openai.chat"
                },
                {
                    "name": "Cursor.app",
                    "vendor": "Cursor",
                    "type": "gui",
                    "bundle_id": "com.todesktop.230313mzl4w4u92"
                },
                {
                    "name": "Cody.app",
                    "vendor": "Sourcegraph",
                    "type": "gui",
                    "bundle_id": "com.sourcegraph.cody"
                },
                {
                    "name": "GitHub Copilot.app",
                    "vendor": "GitHub",
                    "type": "gui",
                    "bundle_id": "com.github.copilot"
                },
                {
                    "name": "Visual Studio Code.app",
                    "vendor": "Microsoft",
                    "type": "gui",
                    "bundle_id": "com.microsoft.VSCode",
                    "note": "Editor; scan for AI extensions in ~/.vscode/extensions"
                },
                {
                    "name": "LM Studio.app",
                    "vendor": "LM Studio",
                    "type": "gui",
                    "bundle_id": "ai.elementlabs.lmstudio",
                    "note": "Local LLM chat and API"
                },
                {
                    "name": "Goose.app",
                    "vendor": "Block",
                    "type": "gui",
                    "bundle_id": "com.block.goose",
                    "note": "Open source AI agent (desktop)"
                }
            ],
            "vscode_extensions": [
                {
                    "id": "kilocode.Kilo-Code",
                    "name": "Kilo Code",
                    "vendor": "Kilo"
                },
                {
                    "id": "roocode.roocode",
                    "name": "Roo Code",
                    "vendor": "Roo"
                },
                {
                    "id": "rooveterinaryinc.roo-cline",
                    "name": "Roo Cline",
                    "vendor": "Roo"
                }
            ],
            "cli_tools": [
                {
                    "name": "claude",
                    "vendor": "Anthropic",
                    "version_cmd": ["claude", "--version"],
                    "config_paths": [
                        "~/.config/claude",
                        "~/.claude"
                    ]
                },
                {
                    "name": "aichat",
                    "vendor": "sigoden",
                    "version_cmd": ["aichat", "--version"],
                    "config_paths": [
                        "~/.config/aichat"
                    ]
                },
                {
                    "name": "gemini",
                    "vendor": "Google",
                    "version_cmd": ["gemini", "--version"],
                    "config_paths": [
                        "~/.config/gemini"
                    ]
                },
                {
                    "name": "github-copilot-cli",
                    "vendor": "GitHub",
                    "version_cmd": ["github-copilot-cli", "--version"],
                    "config_paths": [
                        "~/.config/github-copilot"
                    ]
                },
                {
                    "name": "ollama",
                    "vendor": "Ollama",
                    "version_cmd": ["ollama", "--version"],
                    "config_paths": [
                        "~/.ollama"
                    ]
                },
                {
                    "name": "goose",
                    "vendor": "Block",
                    "version_cmd": ["goose", "--version"],
                    "config_paths": [
                        "~/Library/Application Support/Goose",
                        "~/.config/goose"
                    ]
                }
            ],
            "config_locations": [
                {
                    "name": "OpenAI",
                    "paths": [
                        "~/.openai",
                        "~/.config/openai"
                    ]
                },
                {
                    "name": "Anthropic",
                    "paths": [
                        "~/.anthropic",
                        "~/.config/anthropic"
                    ]
                }
            ]
        }

    def save_config(self):
        """Save current configuration to file"""
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def update_from_url(self, url: Optional[str] = None) -> bool:
        """Update configuration from remote URL"""
        update_url = url or self.config.get('update_url')
        if not update_url:
            print("No update URL configured", file=sys.stderr)
            return False

        try:
            req = Request(update_url, headers={'User-Agent': 'aiapp-scanner/1.0'})
            with urlopen(req, timeout=10) as response:
                new_config = json.loads(response.read().decode('utf-8'))

            # Validate new config has required fields
            if 'applications' in new_config or 'cli_tools' in new_config or 'vscode_extensions' in new_config:
                # Backup old config
                backup_path = f"{self.config_path}.bak"
                if os.path.exists(self.config_path):
                    shutil.copy2(self.config_path, backup_path)

                self.config = new_config
                self.save_config()
                print(f"Configuration updated from {update_url}")
                return True
            else:
                print("Invalid configuration format from URL", file=sys.stderr)
                return False

        except (URLError, HTTPError, json.JSONDecodeError) as e:
            print(f"Failed to update configuration: {e}", file=sys.stderr)
            return False


class ApplicationScanner:
    """Scans for GUI applications"""

    def __init__(self, config: ScannerConfig):
        self.config = config
        self.app_dirs = [
            '/Applications',
            os.path.expanduser('~/Applications'),
            '/System/Applications'
        ]

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for known AI applications"""
        found_apps = []
        known_apps = {app['name']: app for app in self.config.config.get('applications', [])}

        for app_dir in self.app_dirs:
            if not os.path.exists(app_dir):
                continue

            try:
                for item in os.listdir(app_dir):
                    if not item.endswith('.app'):
                        continue

                    if item in known_apps:
                        app_path = os.path.join(app_dir, item)
                        app_info = self._get_app_info(app_path, known_apps[item])
                        if app_info:
                            found_apps.append(app_info)
            except PermissionError:
                continue

        return found_apps

    def _get_app_info(self, app_path: str, known_info: Dict) -> Optional[Dict[str, Any]]:
        """Extract application information from Info.plist"""
        info_plist_path = os.path.join(app_path, 'Contents/Info.plist')

        if not os.path.exists(info_plist_path):
            return None

        try:
            with open(info_plist_path, 'rb') as f:
                plist = plistlib.load(f)

            return {
                'type': 'application',
                'name': known_info['name'],
                'vendor': known_info['vendor'],
                'version': plist.get('CFBundleShortVersionString', 'unknown'),
                'bundle_version': plist.get('CFBundleVersion', 'unknown'),
                'bundle_id': plist.get('CFBundleIdentifier', 'unknown'),
                'path': app_path,
                'install_location': os.path.dirname(app_path)
            }
        except Exception as e:
            print(f"Error reading {info_plist_path}: {e}", file=sys.stderr)
            return None


class CLIToolScanner:
    """Scans for CLI tools"""

    def __init__(self, config: ScannerConfig):
        self.config = config

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for known CLI tools"""
        found_tools = []

        for tool in self.config.config.get('cli_tools', []):
            tool_info = self._check_tool(tool)
            if tool_info:
                found_tools.append(tool_info)

        return found_tools

    def _check_tool(self, tool_config: Dict) -> Optional[Dict[str, Any]]:
        """Check if CLI tool is installed and get version"""
        tool_name = tool_config['name']
        tool_path = shutil.which(tool_name)

        if not tool_path:
            return None

        version = self._get_version(tool_config)
        config_info = self._check_config(tool_config.get('config_paths', []))

        return {
            'type': 'cli_tool',
            'name': tool_name,
            'vendor': tool_config['vendor'],
            'path': tool_path,
            'version': version,
            'configurations': config_info
        }

    def _get_version(self, tool_config: Dict) -> str:
        """Get version information for CLI tool"""
        version_cmd = tool_config.get('version_cmd', [])

        if not version_cmd:
            return 'unknown'

        try:
            result = subprocess.run(
                version_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            version_output = result.stdout.strip() or result.stderr.strip()
            # Clean up common version output patterns
            version_output = version_output.replace('\n', ' ').strip()
            return version_output[:200] if version_output else 'unknown'

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return f'error: {type(e).__name__}'

    def _check_config(self, config_paths: List[str]) -> List[Dict[str, Any]]:
        """Check for configuration files"""
        configs = []

        for path in config_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                config_info = {
                    'path': expanded_path,
                    'exists': True
                }

                if os.path.isdir(expanded_path):
                    try:
                        files = os.listdir(expanded_path)
                        config_info['type'] = 'directory'
                        config_info['file_count'] = len(files)
                        config_info['files'] = sorted(files)[:20] # Limit for privacy
                    except PermissionError:
                        config_info['error'] = 'permission_denied'
                else:
                    config_info['type'] = 'file'
                    try:
                        stat = os.stat(expanded_path)
                        config_info['size'] = stat.st_size
                        config_info['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    except Exception:
                        pass

                configs.append(config_info)

        return configs


class ConfigurationScanner:
    """Scans for standalone configuration directories"""

    def __init__(self, config: ScannerConfig):
        self.config = config

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for configuration directories"""
        found_configs = []

        for config_location in self.config.config.get('config_locations', []):
            for path in config_location['paths']:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    config_info = {
                        'type': 'configuration',
                        'name': config_location['name'],
                        'path': expanded_path,
                        'exists': True
                    }

                    try:
                        if os.path.isdir(expanded_path):
                            files = os.listdir(expanded_path)
                            config_info['file_count'] = len(files)
                            config_info['files'] = sorted(files)[:20]
                        else:
                            stat = os.stat(expanded_path)
                            config_info['size'] = stat.st_size

                        found_configs.append(config_info)
                    except PermissionError:
                        config_info['error'] = 'permission_denied'
                        found_configs.append(config_info)

        return found_configs


class VSCodeExtensionScanner:
    """Scans for AI-related extensions in VSCode extension directories."""

    EXTENSION_DIRS = [
        (os.path.expanduser('~/.vscode/extensions'), 'vscode'),
        (os.path.expanduser('~/.vscode-insiders/extensions'), 'vscode-insiders'),
    ]

    def __init__(self, config: ScannerConfig):
        self.config = config

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for configured VSCode extensions (e.g. roocode)."""
        found = []
        wanted = self.config.config.get('vscode_extensions', [])

        for ext_dir, vscode_type in self.EXTENSION_DIRS:
            if not os.path.isdir(ext_dir):
                continue
            try:
                for entry in os.listdir(ext_dir):
                    for ext_cfg in wanted:
                        ext_id = ext_cfg.get('id') or ext_cfg.get('name', '')
                        if not ext_id or '.' not in ext_id:
                            continue
                        # Extension folders are publisher.name-version (often lowercase on disk)
                        prefix = ext_id + '-'
                        if entry.startswith(prefix) or entry.lower().startswith(prefix.lower()):
                            info = self._read_extension_info(
                                os.path.join(ext_dir, entry),
                                ext_cfg,
                                vscode_type
                            )
                            if info:
                                found.append(info)
                            break
            except PermissionError:
                continue

        return found

    def _read_extension_info(
        self,
        ext_path: str,
        ext_cfg: Dict,
        vscode_type: str
    ) -> Optional[Dict[str, Any]]:
        """Read package.json from extension folder for version and display name."""
        pkg_path = os.path.join(ext_path, 'package.json')
        if not os.path.isfile(pkg_path):
            return {
                'type': 'vscode_extension',
                'extension_id': ext_cfg.get('id', ''),
                'name': ext_cfg.get('name', ext_cfg.get('id', '')),
                'vendor': ext_cfg.get('vendor', ''),
                'version': 'unknown',
                'path': ext_path,
                'vscode_type': vscode_type
            }
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
            display_name = pkg.get('displayName') or ''
            if '%' in display_name or not display_name:
                display_name = ext_cfg.get('name') or pkg.get('name', '') or ext_cfg.get('id', '')
            return {
                'type': 'vscode_extension',
                'extension_id': ext_cfg.get('id', ''),
                'name': display_name,
                'vendor': ext_cfg.get('vendor', pkg.get('publisher', '')),
                'version': pkg.get('version', 'unknown'),
                'path': ext_path,
                'vscode_type': vscode_type
            }
        except (json.JSONDecodeError, OSError):
            return {
                'type': 'vscode_extension',
                'extension_id': ext_cfg.get('id', ''),
                'name': ext_cfg.get('name', ext_cfg.get('id', '')),
                'vendor': ext_cfg.get('vendor', ''),
                'version': 'unknown',
                'path': ext_path,
                'vscode_type': vscode_type
            }


class AIAppScanner:
    """Main scanner orchestrator"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = ScannerConfig(config_path)
        self.app_scanner = ApplicationScanner(self.config)
        self.cli_scanner = CLIToolScanner(self.config)
        self.config_scanner = ConfigurationScanner(self.config)
        self.vscode_scanner = VSCodeExtensionScanner(self.config)

    def scan(self) -> Dict[str, Any]:
        """Perform complete scan"""
        import platform

        raw_hostname = platform.node()
        raw_user = os.getenv('USER', 'unknown')
        anonymized_user = _anonymize_identifier(raw_user)
        real_home = os.path.expanduser('~')
        anonymized_home = f"/Users/{anonymized_user}"

        results = {
            'scan_metadata': {
                'timestamp': datetime.now().isoformat(),
                'scanner_version': '0.2.0',
                'hostname': _anonymize_hostname(raw_hostname),
                'os_version': platform.mac_ver()[0],
                'config_version': self.config.config.get('version', 'unknown'),
                'user': anonymized_user
            },
            'applications': self.app_scanner.scan(),
            'cli_tools': self.cli_scanner.scan(),
            'configurations': self.config_scanner.scan(),
            'vscode_extensions': self.vscode_scanner.scan()
        }

        # Remove username from any paths in output (e.g. /Users/realname -> /Users/anonymized)
        _sanitize_paths_in_output(results, real_home, anonymized_home)

        # Add summary counts
        results['summary'] = {
            'total_applications': len(results['applications']),
            'total_cli_tools': len(results['cli_tools']),
            'total_configurations': len(results['configurations']),
            'total_vscode_extensions': len(results['vscode_extensions'])
        }

        return results

    def update_config(self, url: Optional[str] = None) -> bool:
        """Update scanner configuration from URL"""
        return self.config.update_from_url(url)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Scan for installed AI applications and tools on macOS'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file',
        default=None
    )
    parser.add_argument(
        '--output',
        help='Output file for scan results (JSON)',
        default=None
    )
    parser.add_argument(
        '--update-config',
        help='Update configuration from URL before scanning',
        action='store_true'
    )
    parser.add_argument(
        '--update-url',
        help='URL to fetch updated configuration from',
        default=None
    )
    parser.add_argument(
        '--create-default-config',
        help='Create default configuration file and exit',
        action='store_true'
    )
    parser.add_argument(
        '--pretty',
        help='Pretty-print JSON output',
        action='store_true'
    )

    args = parser.parse_args()

    scanner = AIAppScanner(args.config)

    if args.create_default_config:
        scanner.config.save_config()
        print(f"Default configuration created at: {scanner.config.config_path}")
        return 0

    if args.update_config:
        if not scanner.update_config(args.update_url):
            print("Warning: Configuration update failed, using existing config", file=sys.stderr)

    # Perform scan
    results = scanner.scan()

    # Output results
    indent = 2 if args.pretty else None
    output_json = json.dumps(results, indent=indent)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Scan results written to: {args.output}")
    else:
        print(output_json)

    return 0


if __name__ == '__main__':
    sys.exit(main())
