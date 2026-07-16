#!/bin/bash
# Install Python 2.7.18 for mise on Apple Silicon Mac (via Anaconda + Rosetta 2)
# Usage: ./install_python2.sh [version]
# Default version: 2.7.18-conda

set -e

VERSION="${1:-2.7.18-conda}"
INSTALL_DIR="$HOME/.local/python2.7.18"
CONDA_PKG_URL="https://repo.anaconda.com/pkgs/main/osx-64/python-2.7.18-h47d645e_1.tar.bz2"
TMP_FILE="/tmp/python-2.7.18-osx64.tar.bz2"

echo "==> Installing Python 2.7.18 for mise (Apple Silicon via Rosetta 2)"

# Check Rosetta 2
if ! arch -x86_64 /usr/bin/true 2>/dev/null; then
    echo "ERROR: Rosetta 2 is not installed. Install it with:"
    echo "  softwareupdate --install-rosetta"
    exit 1
fi
echo "==> Rosetta 2: OK"

# Download Anaconda Python 2.7.18 (x86_64)
if [ ! -f "$TMP_FILE" ]; then
    echo "==> Downloading Python 2.7.18 from Anaconda..."
    curl -L "$CONDA_PKG_URL" -o "$TMP_FILE"
else
    echo "==> Using cached download: $TMP_FILE"
fi

# Extract to install directory
echo "==> Extracting to $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
tar -xjf "$TMP_FILE"

# Create Rosetta 2 wrapper for python2.7
echo "==> Creating Rosetta 2 wrapper..."
mv bin/python2.7 bin/.python2.7.bin
cat > bin/python2.7 << 'WRAPPER'
#!/bin/bash
exec arch -x86_64 "$(dirname "$0")/.python2.7.bin" "$@"
WRAPPER
chmod +x bin/python2.7

# Update symlinks
rm -f bin/python bin/python2
ln -s python2.7 bin/python
ln -s python2.7 bin/python2

# Verify installation
echo "==> Verifying installation..."
"$INSTALL_DIR/bin/python" --version

# Link to mise
echo "==> Linking to mise as python@$VERSION..."
mise link --force "python@$VERSION" "$INSTALL_DIR"

echo ""
echo "==> Installation complete!"
echo ""
echo "Usage:"
echo "  mise use python@$VERSION           # Use in current directory"
echo "  mise use -g python@$VERSION        # Use globally"
echo "  mise exec python@$VERSION -- python script.py"
echo ""
