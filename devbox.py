#!/usr/bin/env python3
"""
DevArsenal (devbox) - The Zero-Dependency Swiss Army Knife CLI for Developers & DevOps.
Author: Rauf Zen (@raufzen)
License: MIT
"""

import sys
import os
import re
import json
import time
import uuid
import socket
import secrets
import hashlib
import base64
import urllib.parse
import urllib.request
import platform
import shutil
import http.server
import threading
from datetime import datetime, timezone

VERSION = "1.2.0"
AUTHOR = "Rauf Zen (@raufzen)"
REPO_URL = "https://github.com/raufzen/dev-arsenal"

# ANSI Colors
class Colors:
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BG_YELLOW = "\033[43m\033[30m"
    RESET = "\033[0m"

def print_banner():
    banner = f"""{Colors.CYAN}{Colors.BOLD}
  ██████╗ ███████╗██╗   ██╗     █████╗ ██████╗ ███████╗███████╗███╗   ██╗ █████╗ ██╗     
  ██╔══██╗██╔════╝██║   ██║    ██╔══██╗██╔══██╗██╔════╝██╔════╝████╗  ██║██╔══██╗██║     
  ██║  ██║█████╗  ██║   ██║    ███████║██████╔╝███████╗█████╗  ██╔██╗ ██║███████║██║     
  ██║  ██║██╔══╝  ╚██╗ ██╔╝    ██╔══██║██╔══██╗╚════██║██╔══╝  ██║╚██╗██║██╔══██║██║     
  ██████╔╝███████╗ ╚████╔╝     ██║  ██║██║  ██║███████║███████╗██║ ╚████║██║  ██║███████╗
  ╚═════╝ ╚══════╝  ╚═══╝      ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝{Colors.RESET}
  {Colors.MAGENTA}⚡ The Zero-Dependency Swiss Army Knife for Developers & DevOps{Colors.RESET}
  {Colors.DIM}Author: {AUTHOR} · v{VERSION} · {REPO_URL}{Colors.RESET}
"""
    print(banner)

# ==================== 1. CRYPTO & ENCODING ====================

def cmd_hash(text):
    """Calculate multiple cryptographic hashes for given text or file."""
    data = text.encode("utf-8")
    is_file = os.path.isfile(text)
    if is_file:
        with open(text, "rb") as f:
            data = f.read()

    md5 = hashlib.md5(data).hexdigest()
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    sha512 = hashlib.sha512(data).hexdigest()

    print(f"\n{Colors.BOLD}🔐 Cryptographic Hashes ({'File: ' + text if is_file else 'Text: ' + repr(text[:30])}){Colors.RESET}")
    print(f"  {Colors.CYAN}MD5:    {Colors.RESET}{md5}")
    print(f"  {Colors.BLUE}SHA1:   {Colors.RESET}{sha1}")
    print(f"  {Colors.GREEN}SHA256: {Colors.RESET}{sha256}")
    print(f"  {Colors.MAGENTA}SHA512: {Colors.RESET}{sha512}")
    return {"md5": md5, "sha1": sha1, "sha256": sha256, "sha512": sha512}

def cmd_base64(text, decode=False):
    """Encode or decode Base64 string."""
    if decode:
        try:
            pad = len(text) % 4
            if pad:
                text += "=" * (4 - pad)
            decoded = base64.b64decode(text.encode("utf-8")).decode("utf-8", errors="replace")
            print(f"\n{Colors.GREEN}🔓 Base64 Decoded:{Colors.RESET}\n{decoded}")
            return decoded
        except Exception as e:
            print(f"{Colors.RED}❌ Base64 decode failed: {e}{Colors.RESET}")
            return None
    else:
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        print(f"\n{Colors.CYAN}🔒 Base64 Encoded:{Colors.RESET}\n{encoded}")
        return encoded

def cmd_jwt(token):
    """Inspect and decode JWT token header and payload without verifying signature."""
    parts = token.strip().split(".")
    if len(parts) != 3:
        print(f"{Colors.RED}❌ Invalid JWT format: Token must have exactly 3 parts separated by dots.{Colors.RESET}")
        return None

    def b64_decode_jwt_part(segment):
        pad = len(segment) % 4
        if pad:
            segment += "=" * (4 - pad)
        return json.loads(base64.urlsafe_b64decode(segment).decode("utf-8", errors="replace"))

    try:
        header = b64_decode_jwt_part(parts[0])
        payload = b64_decode_jwt_part(parts[1])
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to decode JWT: {e}{Colors.RESET}")
        return None

    print(f"\n{Colors.BOLD}🎫 JWT Inspector{Colors.RESET}")
    print(f"{Colors.CYAN}── Header ──────────────────────────────────────────{Colors.RESET}")
    print(json.dumps(header, indent=2))
    print(f"{Colors.GREEN}── Payload ─────────────────────────────────────────{Colors.RESET}")
    print(json.dumps(payload, indent=2))

    if "exp" in payload:
        exp_ts = payload["exp"]
        exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        now_ts = time.time()
        diff = exp_ts - now_ts
        if diff > 0:
            print(f"{Colors.GREEN}✔ Status: ACTIVE (Expires: {exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}, {int(diff)}s remaining){Colors.RESET}")
        else:
            print(f"{Colors.RED}✖ Status: EXPIRED ({abs(int(diff))}s ago at {exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}){Colors.RESET}")
    return {"header": header, "payload": payload}

# ==================== 2. DEVELOPER UTILITIES ====================

def cmd_json(text_or_file):
    """Validate, format, and beautify JSON."""
    raw = text_or_file
    if os.path.isfile(text_or_file):
        with open(text_or_file, "r") as f:
            raw = f.read()
    try:
        parsed = json.loads(raw)
        formatted = json.dumps(parsed, indent=2, sort_keys=True)
        print(f"\n{Colors.GREEN}✔ Valid JSON ({len(parsed) if isinstance(parsed, (dict, list)) else 'scalar'} elements):{Colors.RESET}")
        print(formatted)
        return formatted
    except Exception as e:
        print(f"{Colors.RED}❌ Invalid JSON: {e}{Colors.RESET}")
        return None

def cmd_uuid(count=1):
    """Generate cryptographically sound UUIDv4 identifiers."""
    results = [str(uuid.uuid4()) for _ in range(max(1, count))]
    print(f"\n{Colors.BOLD}🆔 Generated UUIDv4 ({count}):{Colors.RESET}")
    for u in results:
        print(f"  {Colors.CYAN}{u}{Colors.RESET}")
    return results

def cmd_password(length=16, symbols=True):
    """Generate high-entropy, cryptographically secure password."""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    if symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    pwd = "".join(secrets.choice(chars) for _ in range(max(8, length)))
    print(f"\n{Colors.BOLD}🔑 Secure Password ({len(pwd)} chars):{Colors.RESET}")
    print(f"  {Colors.GREEN}{pwd}{Colors.RESET}")
    return pwd

def cmd_timestamp(val=None):
    """Convert timestamp to ISO datetime or current time to timestamp."""
    if val is None or val == "now":
        now = time.time()
        dt = datetime.fromtimestamp(now, tz=timezone.utc)
        print(f"\n{Colors.BOLD}⏰ Current Epoch Timestamp:{Colors.RESET}")
        print(f"  {Colors.CYAN}Unix Seconds: {Colors.RESET}{int(now)}")
        print(f"  {Colors.BLUE}Unix Millis:  {Colors.RESET}{int(now * 1000)}")
        print(f"  {Colors.GREEN}UTC String:   {Colors.RESET}{dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  {Colors.MAGENTA}ISO 8601:     {Colors.RESET}{dt.isoformat()}")
        return int(now)
    else:
        try:
            ts = float(val)
            if ts > 1e11:
                ts /= 1000.0
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            print(f"\n{Colors.BOLD}⏰ Timestamp {val} Converted:{Colors.RESET}")
            print(f"  {Colors.GREEN}UTC Time: {Colors.RESET}{dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"  {Colors.CYAN}ISO 8601: {Colors.RESET}{dt.isoformat()}")
            return dt.isoformat()
        except ValueError:
            print(f"{Colors.RED}❌ Expected numeric timestamp or 'now'.{Colors.RESET}")
            return None

def cmd_url(raw_url):
    """Parse URL components, paths, and query parameters."""
    if not (raw_url.startswith("http://") or raw_url.startswith("https://")):
        raw_url = "https://" + raw_url
    p = urllib.parse.urlparse(raw_url)
    qs = urllib.parse.parse_qs(p.query)

    print(f"\n{Colors.BOLD}🔗 URL Component Breakdown:{Colors.RESET}")
    print(f"  {Colors.CYAN}Scheme:  {Colors.RESET}{p.scheme}")
    print(f"  {Colors.BLUE}Host:    {Colors.RESET}{p.netloc}")
    print(f"  {Colors.GREEN}Path:    {Colors.RESET}{p.path or '/'}")
    if p.fragment:
        print(f"  {Colors.MAGENTA}Fragment:{Colors.RESET}{p.fragment}")
    if qs:
        print(f"\n  {Colors.BOLD}Query Parameters ({len(qs)}):{Colors.RESET}")
        for k, v in qs.items():
            print(f"    {Colors.YELLOW}{k}{Colors.RESET} = {', '.join(v)}")
    else:
        print(f"  {Colors.DIM}No query parameters present.{Colors.RESET}")
    return {"scheme": p.scheme, "host": p.netloc, "path": p.path, "params": qs}

def cmd_regex(pattern, text):
    """Test regular expression patterns with colorized match highlights."""
    print(f"\n{Colors.BOLD}🔍 Regex Match Tester:{Colors.RESET}")
    print(f"  Pattern: {Colors.CYAN}/{pattern}/{Colors.RESET}")
    print(f"  Input:   {Colors.DIM}{repr(text)}{Colors.RESET}\n")
    try:
        matches = list(re.finditer(pattern, text))
        if not matches:
            print(f"  {Colors.RED}✖ No matches found.{Colors.RESET}")
            return []

        print(f"  {Colors.GREEN}✔ Found {len(matches)} match(es):{Colors.RESET}")
        for i, m in enumerate(matches, 1):
            print(f"    Match #{i}: {Colors.YELLOW}{repr(m.group(0))}{Colors.RESET} [span: {m.start()}..{m.end()}]")
            if m.groups():
                print(f"      Groups: {m.groups()}")
        return matches
    except Exception as e:
        print(f"  {Colors.RED}Regex syntax error: {e}{Colors.RESET}")
        return None

def cmd_color(val):
    """Convert HEX to RGB, HSL, and render live TrueColor swatch."""
    clean = val.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join([c*2 for c in clean])
    try:
        r, g, b = tuple(int(clean[i:i+2], 16) for i in (0, 2, 4))
        swatch = f"\033[48;2;{r};{g};{b}m        \033[0m"
        print(f"\n{Colors.BOLD}🎨 Color Swatch & Converter:{Colors.RESET}")
        print(f"  Swatch:  {swatch}")
        print(f"  HEX:     {Colors.CYAN}#{clean.upper()}{Colors.RESET}")
        print(f"  RGB:     {Colors.GREEN}rgb({r}, {g}, {b}){Colors.RESET}")
        print(f"  CSS:     {Colors.MAGENTA}rgba({r}, {g}, {b}, 1.0){Colors.RESET}")
        return {"hex": f"#{clean.upper()}", "r": r, "g": g, "b": b}
    except Exception:
        print(f"{Colors.RED}❌ Invalid hex color code: '{val}'. Example: #38bdf8 or 38bdf8{Colors.RESET}")
        return None

# ==================== 3. NETWORK & WEB ====================

def cmd_ip():
    """Discover external IP, hostname, and basic location."""
    print(f"\n{Colors.BOLD}🌐 Public IP & Network Intelligence...{Colors.RESET}")
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={"User-Agent": "devbox/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            ip_data = json.loads(res.read().decode())
            ip = ip_data.get("ip")
            print(f"  {Colors.GREEN}Public IP:{Colors.RESET}   {ip}")
    except Exception:
        ip = "Unavailable"

    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    print(f"  {Colors.CYAN}Local IP:{Colors.RESET}    {local_ip}")
    print(f"  {Colors.BLUE}Hostname:{Colors.RESET}    {hostname}")
    return {"public_ip": ip, "local_ip": local_ip, "hostname": hostname}

def cmd_dns(domain):
    """Resolve DNS records (A / AAAA / Canonical names) for a domain."""
    print(f"\n{Colors.BOLD}🔎 DNS Lookup for {domain}...{Colors.RESET}")
    try:
        info = socket.getaddrinfo(domain, 80, proto=socket.IPPROTO_TCP)
        ips = sorted(list(set([r[4][0] for r in info])))
        print(f"  {Colors.GREEN}Resolved IP Addresses ({len(ips)}):{Colors.RESET}")
        for ip in ips:
            print(f"    • {Colors.CYAN}{ip}{Colors.RESET}")
        return ips
    except Exception as e:
        print(f"  {Colors.RED}DNS resolution failed: {e}{Colors.RESET}")
        return None

def cmd_http(url):
    """Check HTTP response status, headers, and response latency."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    print(f"\n{Colors.BOLD}📡 Inspecting {url}...{Colors.RESET}")
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "devbox-cli/1.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            elapsed = int((time.time() - t0) * 1000)
            status = res.status
            print(f"  {Colors.GREEN}Status:{Colors.RESET}     {status} {res.reason}")
            print(f"  {Colors.CYAN}Latency:{Colors.RESET}    {elapsed} ms")
            print(f"  {Colors.BLUE}Headers:{Colors.RESET}")
            for k, v in list(res.headers.items())[:10]:
                print(f"    {Colors.DIM}{k}:{Colors.RESET} {v}")
            return {"status": status, "latency_ms": elapsed}
    except Exception as e:
        print(f"  {Colors.RED}Request failed: {e}{Colors.RESET}")
        return None

def cmd_port(host, port):
    """Test TCP port reachability."""
    port = int(port)
    print(f"\n{Colors.BOLD}🔌 Testing TCP Connection to {host}:{port}...{Colors.RESET}")
    t0 = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4.0)
    try:
        result = sock.connect_ex((host, port))
        elapsed = int((time.time() - t0) * 1000)
        sock.close()
        if result == 0:
            print(f"  {Colors.GREEN}✔ PORT OPEN{Colors.RESET} ({elapsed} ms)")
            return True
        else:
            print(f"  {Colors.RED}✖ PORT CLOSED / FILTERED{Colors.RESET} (code {result})")
            return False
    except Exception as e:
        print(f"  {Colors.RED}Connection error: {e}{Colors.RESET}")
        return False

def cmd_serve(port=8080, directory="."):
    """Launch instant local HTTP file server for Wi-Fi file transfer."""
    os.chdir(directory)
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("0.0.0.0", port), handler)
    print(f"\n{Colors.BOLD}🚀 Instant HTTP Server Running!{Colors.RESET}")
    print(f"  {Colors.GREEN}Local Address:{Colors.RESET}    http://127.0.0.1:{port}")
    print(f"  {Colors.CYAN}Wi-Fi / LAN Share:{Colors.RESET} http://{local_ip}:{port}")
    print(f"  {Colors.DIM}Serving directory: {os.path.abspath(directory)}{Colors.RESET}")
    print(f"  {Colors.YELLOW}Press Ctrl+C to stop the server.{Colors.RESET}\n")
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n{Colors.RED}Server stopped.{Colors.RESET}")

# ==================== 4. SYSTEM & AUDIT ====================

def cmd_sys():
    """Print system summary, architecture, and disk metrics."""
    print(f"\n{Colors.BOLD}💻 System Diagnostics{Colors.RESET}")
    print(f"  {Colors.CYAN}OS / Platform:{Colors.RESET}  {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  {Colors.BLUE}Python:{Colors.RESET}         {platform.python_version()} ({sys.executable})")
    
    total, used, free = shutil.disk_usage("/")
    to_gb = lambda b: f"{b / (1024**3):.1f} GB"
    print(f"  {Colors.GREEN}Disk Space:{Colors.RESET}     {to_gb(used)} used / {to_gb(total)} total ({to_gb(free)} free)")
    return {"os": platform.system(), "python": platform.python_version()}

def cmd_du(target_dir="."):
    """Analyze directory disk usage and report top 10 largest files."""
    print(f"\n{Colors.BOLD}📊 Disk Hog Analyzer for '{target_dir}'...{Colors.RESET}")
    file_list = []
    ignored = {".git", "node_modules", ".venv", "venv", "__pycache__"}
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignored]
        for f in files:
            p = os.path.join(root, f)
            try:
                size = os.path.getsize(p)
                file_list.append((size, p))
            except Exception:
                pass
    file_list.sort(key=lambda x: x[0], reverse=True)
    if not file_list:
        print(f"  {Colors.DIM}No files found.{Colors.RESET}")
        return []

    def format_size(bytes_num):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.1f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.1f} TB"

    print(f"  {Colors.CYAN}Top {min(10, len(file_list))} Largest Files:{Colors.RESET}")
    for sz, p in file_list[:10]:
        print(f"    {Colors.YELLOW}{format_size(sz):>10}{Colors.RESET}  {p}")
    return file_list[:10]

def cmd_audit(target_dir="."):
    """Scan local directory for exposed secrets, API keys, and sensitive tokens."""
    patterns = {
        "AWS Access Key": r"AKIA[0-9A-Z]{16}",
        "Generic API Key": r"(?i)(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][0-9a-zA-Z\-_]{16,}['\"]",
        "Private Key": r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
        "GitHub Token": r"(ghp|gho|ghu|ghs|ghr)_[0-9a-zA-Z]{36}",
        "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
    }
    print(f"\n{Colors.BOLD}🛡️ Scanning '{target_dir}' for accidental secrets...{Colors.RESET}")
    found = 0
    ignored_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__"}
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    for name, pat in patterns.items():
                        if re.search(pat, content):
                            print(f"  {Colors.RED}⚠ Found potential {name} in: {path}{Colors.RESET}")
                            found += 1
            except Exception:
                pass
    if found == 0:
        print(f"  {Colors.GREEN}✔ Clean! No common hardcoded secrets detected in scanned files.{Colors.RESET}")
    return found

# ==================== INTERACTIVE MENU ====================

def interactive_menu():
    print_banner()
    menu = f"""
  {Colors.BOLD}Select an Arsenal Tool:{Colors.RESET}
  {Colors.CYAN}1.{Colors.RESET} 🔐 Hash Generator (MD5, SHA1, SHA256, SHA512)
  {Colors.CYAN}2.{Colors.RESET} 🔓 Base64 Encoder / Decoder
  {Colors.CYAN}3.{Colors.RESET} 🎫 JWT Inspector (Decode Header & Claims)
  {Colors.CYAN}4.{Colors.RESET} 📋 JSON Formatter & Validator
  {Colors.CYAN}5.{Colors.RESET} 🆔 UUIDv4 Generator
  {Colors.CYAN}6.{Colors.RESET} 🔑 High-Entropy Password Generator
  {Colors.CYAN}7.{Colors.RESET} ⏰ Epoch Timestamp Converter
  {Colors.CYAN}8.{Colors.RESET} 🔗 URL Breakdown & Query Parameter Inspector
  {Colors.CYAN}9.{Colors.RESET} 🔍 Regex Match Tester & Visualizer
  {Colors.CYAN}10.{Colors.RESET} 🎨 Color Swatch Converter (HEX to RGB)
  {Colors.CYAN}11.{Colors.RESET} 🌐 Public IP & Network Info
  {Colors.CYAN}12.{Colors.RESET} 🔎 DNS Address Resolution
  {Colors.CYAN}13.{Colors.RESET} 📡 HTTP Status & Latency Check
  {Colors.CYAN}14.{Colors.RESET} 🔌 TCP Port Ping
  {Colors.CYAN}15.{Colors.RESET} 🚀 Instant Wi-Fi HTTP File Sharing Server
  {Colors.CYAN}16.{Colors.RESET} 💻 System Specs & Environment
  {Colors.CYAN}17.{Colors.RESET} 📊 Disk Hog File Analyzer
  {Colors.CYAN}18.{Colors.RESET} 🛡️ Local Secret Leak Scanner
  {Colors.RED}0.{Colors.RESET} 🚪 Exit
"""
    print(menu)
    try:
        choice = input(f"{Colors.BOLD}devbox > {Colors.RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        return

    if choice == "1":
        val = input("Enter text or file path to hash: ").strip()
        cmd_hash(val)
    elif choice == "2":
        mode = input("1. Encode | 2. Decode [default 1]: ").strip()
        val = input("Enter text: ").strip()
        cmd_base64(val, decode=(mode == "2"))
    elif choice == "3":
        val = input("Paste JWT token: ").strip()
        cmd_jwt(val)
    elif choice == "4":
        val = input("Enter JSON string or file path: ").strip()
        cmd_json(val)
    elif choice == "5":
        n = input("Number of UUIDs [default 1]: ").strip()
        cmd_uuid(int(n) if n.isdigit() else 1)
    elif choice == "6":
        l = input("Password length [default 16]: ").strip()
        cmd_password(int(l) if l.isdigit() else 16)
    elif choice == "7":
        ts = input("Timestamp or 'now' [default now]: ").strip()
        cmd_timestamp(ts or "now")
    elif choice == "8":
        url = input("Enter URL with params: ").strip()
        cmd_url(url)
    elif choice == "9":
        pat = input("Regex pattern: ").strip()
        txt = input("Test string: ").strip()
        cmd_regex(pat, txt)
    elif choice == "10":
        col = input("HEX Color (e.g. #38bdf8): ").strip()
        cmd_color(col)
    elif choice == "11":
        cmd_ip()
    elif choice == "12":
        dom = input("Domain name (e.g. github.com): ").strip()
        cmd_dns(dom)
    elif choice == "13":
        url = input("Enter URL (e.g. google.com): ").strip()
        cmd_http(url)
    elif choice == "14":
        host = input("Host (e.g. github.com): ").strip()
        port = input("Port (e.g. 443): ").strip()
        cmd_port(host, int(port) if port.isdigit() else 80)
    elif choice == "15":
        port = input("Port [default 8080]: ").strip()
        cmd_serve(int(port) if port.isdigit() else 8080)
    elif choice == "16":
        cmd_sys()
    elif choice == "17":
        path = input("Directory to analyze [default .]: ").strip()
        cmd_du(path or ".")
    elif choice == "18":
        path = input("Directory to scan [default .]: ").strip()
        cmd_audit(path or ".")
    elif choice == "0":
        print("Goodbye!")
        return
    else:
        print("Invalid option.")

# ==================== CLI DISPATCHER ====================

def main():
    if len(sys.argv) < 2:
        if sys.stdin.isatty():
            interactive_menu()
        else:
            print_banner()
            print("Usage: devbox <command> [arguments]")
            print("Run './devbox' without arguments for interactive menu.")
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd in ("-h", "--help", "help"):
        print_banner()
        print(f"""{Colors.BOLD}COMMANDS:{Colors.RESET}
  hash <text|file>          Calculate MD5, SHA1, SHA256, SHA512
  b64 <text> [--decode]     Base64 encode or decode
  jwt <token>               Inspect and decode JWT payload & expiry
  json <str|file>           Validate and pretty-print JSON
  uuid [-n count]           Generate cryptographically random UUIDv4
  pass [-l len]             Generate secure high-entropy password
  time [timestamp|now]      Convert Unix epoch to human UTC or get current
  url <url>                 Parse URL components & query parameters
  regex <pattern> <text>    Test regular expression matches
  color <#hex>              Display TrueColor swatch and RGB values
  ip                        Show public IP, local IP, and hostname
  dns <domain>              Resolve DNS IP addresses
  http <url>                Inspect HTTP status code, headers & latency
  port <host> <port>        Check if a TCP port is open
  serve [port]              Launch instant local Wi-Fi file server
  sys                       Display OS, architecture, disk metrics
  du [dir]                  Analyze largest files in directory
  audit [dir]               Audit directory for exposed secrets
  menu                      Launch interactive terminal menu
""")
        return

    if cmd == "hash" and args:
        cmd_hash(args[0])
    elif cmd == "b64" and args:
        cmd_base64(args[0], decode=("--decode" in args or "-d" in args))
    elif cmd == "jwt" and args:
        cmd_jwt(args[0])
    elif cmd == "json" and args:
        cmd_json(args[0])
    elif cmd == "uuid":
        n = 1
        if "-n" in args:
            idx = args.index("-n")
            if idx + 1 < len(args) and args[idx+1].isdigit():
                n = int(args[idx+1])
        cmd_uuid(n)
    elif cmd == "pass":
        l = 16
        if "-l" in args:
            idx = args.index("-l")
            if idx + 1 < len(args) and args[idx+1].isdigit():
                l = int(args[idx+1])
        cmd_password(l)
    elif cmd == "time":
        cmd_timestamp(args[0] if args else "now")
    elif cmd == "url" and args:
        cmd_url(args[0])
    elif cmd == "regex" and len(args) >= 2:
        cmd_regex(args[0], " ".join(args[1:]))
    elif cmd == "color" and args:
        cmd_color(args[0])
    elif cmd == "ip":
        cmd_ip()
    elif cmd == "dns" and args:
        cmd_dns(args[0])
    elif cmd == "http" and args:
        cmd_http(args[0])
    elif cmd == "port" and len(args) >= 2:
        cmd_port(args[0], args[1])
    elif cmd == "serve":
        p = int(args[0]) if args and args[0].isdigit() else 8080
        cmd_serve(p)
    elif cmd == "sys":
        cmd_sys()
    elif cmd == "du":
        cmd_du(args[0] if args else ".")
    elif cmd == "audit":
        cmd_audit(args[0] if args else ".")
    elif cmd == "menu":
        interactive_menu()
    else:
        print(f"{Colors.RED}Unknown command: '{cmd}'. Run 'devbox --help' for usage.{Colors.RESET}")

if __name__ == "__main__":
    main()
