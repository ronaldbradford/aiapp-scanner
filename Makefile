.PHONY: help install test clean format lint run update-config

help:
	@echo "Available targets:"
	@echo "  install        - Install the scanner locally"
	@echo "  test           - Run tests"
	@echo "  run            - Run scanner with pretty output"
	@echo "  update-config  - Update configuration from URL"
	@echo "  clean          - Remove build artifacts"
	@echo "  format         - Format code with black"
	@echo "  lint           - Lint code with flake8"

install:
	pip install -e .

test:
	python test_scanner.py

run:
	python aiapp_scanner.py --pretty

update-config:
	python aiapp_scanner.py --update-config --pretty

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

format:
	black aiapp_scanner.py test_scanner.py

lint:
	flake8 aiapp_scanner.py test_scanner.py --max-line-length=100

# Development helpers
create-config:
	python aiapp_scanner.py --create-default-config

scan-to-file:
	python aiapp_scanner.py --output scan_results.json --pretty
	@echo "Results written to scan_results.json"

# Homebrew tap helpers
tap-create:
	@echo "To create a Homebrew tap:"
	@echo "1. Create a GitHub repo named 'homebrew-aiapp-scanner'"
	@echo "2. Add aiapp-scanner.rb to the repo"
	@echo "3. Users can install with:"
	@echo "   brew tap yourusername/aiapp-scanner"
	@echo "   brew install aiapp-scanner"

release:
	@echo "To create a release:"
	@echo "1. Update version in setup.py and aiapp_scanner.py"
	@echo "2. Create git tag: git tag v0.1.0"
	@echo "3. Push tag: git push origin v0.1.0"
	@echo "4. Create release tarball: git archive --format=tar.gz --output=aiapp-scanner-0.1.0.tar.gz v0.1.0"
	@echo "5. Calculate SHA256: shasum -a 256 aiapp-scanner-0.1.0.tar.gz"
	@echo "6. Update aiapp-scanner.rb with new SHA256"
