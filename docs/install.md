# Installation Guide

This guide explains how to install RepoBrain for local development and daily use.

## English

### Requirements

- Python `3.12+`
- PowerShell on Windows, or a POSIX shell on Linux/macOS
- Internet access for the first dependency install

### Windows PowerShell

From the repository root:

```powershell
cd C:\Users\ASUS\Desktop\new-AI
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,tree-sitter,mcp]"
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Linux Or macOS

```bash
cd /path/to/new-AI
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,tree-sitter,mcp]"
```

### Install Profiles

- `python -m pip install -e "."`: install only the core CLI package
- `python -m pip install -e ".[dev]"`: install core package plus test tools
- `python -m pip install -e ".[tree-sitter]"`: install optional parser quality upgrades
- `python -m pip install -e ".[mcp]"`: install optional MCP dependencies
- `python -m pip install -e ".[providers]"`: install optional Gemini, OpenAI, Voyage, and Cohere SDK adapters
- `python -m pip install -e ".[dev,tree-sitter,mcp]"`: install the full local development setup

### Verify

```powershell
repobrain doctor --format text
repobrain index --format text
repobrain query "Where is RepoBrain CLI implemented?" --format text
repobrain report --format text
repobrain chat
```

Expected signs of a healthy install:

- `provider_status.embedding.ready` is `true`
- `provider_status.reranker.ready` is `true`
- `capabilities.tree_sitter_ready` is `true` when tree-sitter extras are installed
- `repobrain index` reports non-zero files, chunks, symbols, and parser usage counts
- `.repobrain/report.html` is generated after `repobrain report`

### Environment File

RepoBrain can load `.env` from the repository root. Start from the template:

```powershell
Copy-Item .env.example .env
```

Fill `GEMINI_API_KEY` only if you explicitly set Gemini in `repobrain.toml`. Keep `.env` private; it is ignored by git.

### One-Click Windows Launchers

After installation, you can launch user-friendly modes from the repository root:

```powershell
.\chat.cmd
.\report.cmd
```

- `chat.cmd` opens the local chat loop.
- `report.cmd` generates `.repobrain/report.html` and opens it in the default browser.

Both launchers prefer `venv\Scripts\python.exe`, fall back to `.venv\Scripts\python.exe`, set `PYTHONPATH=src`, and initialize/index the repo when needed.

## Tiếng Việt

### Yêu Cầu

- Python `3.12+`
- PowerShell trên Windows, hoặc shell POSIX trên Linux/macOS
- Cần mạng ở lần cài dependency đầu tiên

### Windows PowerShell

Chạy từ thư mục gốc của repo:

```powershell
cd C:\Users\ASUS\Desktop\new-AI
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,tree-sitter,mcp]"
```

Nếu PowerShell chặn activate, chạy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Linux Hoặc macOS

```bash
cd /path/to/new-AI
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,tree-sitter,mcp]"
```

### Các Kiểu Cài

- `python -m pip install -e "."`: chỉ cài core CLI package
- `python -m pip install -e ".[dev]"`: cài core package và tool test
- `python -m pip install -e ".[tree-sitter]"`: cài parser optional để tăng chất lượng phân tích code
- `python -m pip install -e ".[mcp]"`: cài dependency optional cho MCP
- `python -m pip install -e ".[providers]"`: cài adapter SDK optional cho Gemini, OpenAI, Voyage và Cohere
- `python -m pip install -e ".[dev,tree-sitter,mcp]"`: cài đầy đủ cho local development

### Kiểm Tra Sau Khi Cài

```powershell
repobrain doctor --format text
repobrain index --format text
repobrain query "Where is RepoBrain CLI implemented?" --format text
repobrain report --format text
repobrain chat
```

Dấu hiệu cài đặt ổn:

- `provider_status.embedding.ready` là `true`
- `provider_status.reranker.ready` là `true`
- `capabilities.tree_sitter_ready` là `true` nếu đã cài tree-sitter extras
- `repobrain index` trả về số lượng files, chunks, symbols và parser usage khác `0`
- `.repobrain/report.html` được tạo sau khi chạy `repobrain report`

### File Môi Trường

RepoBrain có thể tự đọc `.env` từ thư mục gốc repo. Bắt đầu từ template:

```powershell
Copy-Item .env.example .env
```

Chỉ điền `GEMINI_API_KEY` nếu bạn chủ động bật Gemini trong `repobrain.toml`. Giữ `.env` riêng tư; file này đã được git ignore.

### Launcher Một Chạm Trên Windows

Sau khi cài xong, có thể mở các chế độ thân thiện từ thư mục gốc:

```powershell
.\chat.cmd
.\report.cmd
```

- `chat.cmd` mở local chat loop.
- `report.cmd` tạo `.repobrain/report.html` và mở bằng trình duyệt mặc định.

Cả hai launcher đều ưu tiên `venv\Scripts\python.exe`, fallback sang `.venv\Scripts\python.exe`, tự set `PYTHONPATH=src`, và tự init/index repo khi cần.
