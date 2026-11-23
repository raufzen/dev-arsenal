# DevArsenal (devbox) ⚡

> **Lightweight, Zero-Dependency Developer Utility Suite & CLI Tool**

Built and maintained by **[Rauf Zen](https://github.com/raufzen)**.

---

## 🚀 Overview

`devbox` is a standalone, cross-platform CLI tool built entirely on the Python 3 standard library. It requires zero third-party packages and works on Linux, macOS, Windows, and Android (Termux / AntiGem).

---

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/raufzen/dev-arsenal.git
cd dev-arsenal

# Make executable and run interactive menu
chmod +x devbox.py
./devbox.py menu
```

---

## 🛠️ Command Reference

| Command | Description | Example |
|---|---|---|
| `hash <text/file>` | Calculate MD5, SHA1, SHA256, SHA512 | `./devbox.py hash "sample text"` |
| `b64 <text> [-d]` | Encode or decode Base64 strings | `./devbox.py b64 "hello" -d` |
| `jwt <token>` | Inspect and decode JWT token payload & expiry | `./devbox.py jwt <token>` |
| `json <str/file>` | Format and validate JSON payload | `./devbox.py json '{"a":1}'` |
| `uuid [-n count]` | Generate random UUIDv4 IDs | `./devbox.py uuid -n 5` |
| `pass [-l len]` | Generate secure random passwords | `./devbox.py pass -l 24` |
| `time [ts/now]` | Convert timestamp to UTC or get current epoch | `./devbox.py time now` |
| `ip` | Show public IP, local IP, and hostname | `./devbox.py ip` |
| `http <url>` | Measure HTTP status code and latency | `./devbox.py http github.com` |
| `port <host> <port>` | Check TCP port availability | `./devbox.py port 8.8.8.8 53` |
| `sys` | View system specs and disk space | `./devbox.py sys` |
| `audit [dir]` | Scan directory for exposed secrets | `./devbox.py audit .` |

---

## 🧪 Testing

Run the built-in test suite:

```bash
python3 -m unittest discover -s tests
```

---

## 📄 License

Released under the [MIT License](LICENSE).
