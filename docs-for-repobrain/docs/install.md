# Installation Guide

## Windows PowerShell

```powershell
cd C:\Users\ASUS\Desktop\new-AI
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,tree-sitter,mcp]"
```

## Linux Or macOS

```bash
cd /path/to/new-AI
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,tree-sitter,mcp]"
```

## Verify

```powershell
repobrain doctor --format text
repobrain index --format text
repobrain query "Where is RepoBrain CLI implemented?" --format text
repobrain report --format text
repobrain chat
```
