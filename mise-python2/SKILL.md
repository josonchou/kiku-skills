---
name: mise-python2
description: Install Python 2.7 on Apple Silicon Mac using mise. Use this skill when the user wants to install Python 2, Python 2.7, or legacy Python on macOS ARM64/Apple Silicon using mise, pyenv, or encounters "no precompiled python found" errors for Python 2.x versions.
---

# Install Python 2.7 with mise on Apple Silicon Mac

## Problem

Python 2.7 cannot be installed via mise on Apple Silicon Mac because:

1. **No precompiled binaries**: python-build-standalone only provides Python 3.8+
2. **Compilation fails**: Python 2.7 source won't compile on modern macOS (26.x)
3. **No ARM64 packages**: Conda/Anaconda don't provide osx-arm64 builds for Python 2.7

## Solution

Use Anaconda's x86_64 Python 2.7 package with Rosetta 2 emulation, then link to mise.

## Quick Install

从 Skill 根目录运行 bundled script：

```bash
bash scripts/install_python2.sh
```

This will:
1. Download Python 2.7.18 from Anaconda (x86_64 version)
2. Create a Rosetta 2 wrapper for transparent execution
3. Link to mise as `python@2.7.18-conda`

## Manual Installation Steps

### 1. Verify Rosetta 2

```bash
arch -x86_64 /usr/bin/true && echo "OK" || softwareupdate --install-rosetta
```

### 2. Download and Extract

```bash
curl -L "https://repo.anaconda.com/pkgs/main/osx-64/python-2.7.18-h47d645e_1.tar.bz2" -o /tmp/python2.tar.bz2
mkdir -p ~/.local/python2.7.18
cd ~/.local/python2.7.18
tar -xjf /tmp/python2.tar.bz2
```

### 3. Create Rosetta Wrapper

```bash
mv bin/python2.7 bin/.python2.7.bin
cat > bin/python2.7 << 'EOF'
#!/bin/bash
exec arch -x86_64 "$(dirname "$0")/.python2.7.bin" "$@"
EOF
chmod +x bin/python2.7
ln -sf python2.7 bin/python
ln -sf python2.7 bin/python2
```

### 4. Link to mise

Use a custom version name to prevent mise from attempting reinstallation:

```bash
mise link python@2.7.18-conda ~/.local/python2.7.18
```

## Usage

```bash
mise use python@2.7.18-conda
mise exec python@2.7.18-conda -- python script.py
mise exec -- python --version
```

## Key Points

- **Version naming**: Use `2.7.18-conda` (not `2.7.18`) to prevent mise from trying to reinstall
- **Rosetta wrapper**: Required because the binary is x86_64, not ARM64
- **External directory**: Install outside `~/.local/share/mise/installs/` to prevent mise from overwriting
