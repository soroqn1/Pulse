.PHONY: install dev build release clean

install:
	poetry install

dev:
	poetry run python -m pulse.main

build: clean
	poetry run pyinstaller --name pulse --onefile --copy-metadata pulse --add-data "pulse/styles.tcss:." pulse/main.py

release: build
	cd dist && tar -czvf pulse-mac.tar.gz pulse
	@echo "\n=== SHA256 HASH FOR HOMEBREW ==="
	@shasum -a 256 dist/pulse-mac.tar.gz

clean:
	rm -rf build/ dist/ *.spec

