from pathlib import Path
import zipfile, shutil

base = Path("/mnt/data/rat_security_review_github")
(base / "docs" / "images").mkdir(parents=True, exist_ok=True)

readme = """# 🔐 RAT Security Review Lab

<p align="center">
  <img src="docs/images/banner.png" alt="RAT Security Review Lab" width="100%">
</p>

<p align="center"><strong>Defensive Code Review • Threat Analysis • Safe Malware Research</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/Focus-Defensive%20Security-0A84FF?style=for-the-badge" alt="Defensive Security">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Status-Analysis%20Only-DC2626?style=for-the-badge" alt="Analysis Only">
</p>

---

## ⚠️ Safety Notice

The supplied Python client/server sample includes remote command delivery, directory browsing, and file encryption/decryption. These capabilities can cause data loss or enable unauthorized access.

**Do not run this code on a personal, production, or third-party system.** This documentation is for defensive code review, threat modeling, and incident-response learning; it intentionally omits deployment instructions and operational command sequences.

## 🔎 Project Overview

- **`Client.py`** — initiates HTTP communication, reports directory listings, receives server-provided commands, and contains file encryption/decryption routines.
- **`Server.py`** — exposes an HTTP listener and a Tkinter GUI for tracking client identifiers, viewing activity logs, and queuing commands.

Treat this sample as potentially harmful software, not as a secure remote administration tool.

## 🧩 High-Level Architecture

```text
             CLIENT HOST
     ┌─────────────────────────┐
     │ Client.py               │
     │ • HTTP polling          │
     │ • Directory enumeration │
     │ • File operations       │
     └────────────┬────────────┘
                  │ HTTP
                  │ No transport TLS
                  ▼
     ┌─────────────────────────┐
     │ Server.py               │
     │ • HTTP listener         │
     │ • Client tracking       │
     │ • Command queue         │
     │ • Activity GUI / logs   │
     └─────────────────────────┘
```

## 🛡️ Security Findings

| Finding | Risk | Defensive recommendation |
|---|---|---|
| Plain HTTP transport | Commands, responses, and keys may be exposed or altered in transit. | Do not expose the service; use authenticated, encrypted protocols in legitimate administration software. |
| UUID header used as client identifier | An identifier is not authentication. | Require strong client authentication and server-side authorization. |
| Destructive file handling | The client attempts to delete originals after writing encrypted copies. | Remove destructive behavior from demos; use synthetic test fixtures and non-destructive simulations. |
| Keys written to a text file | Key material may be disclosed if the server host is compromised. | Avoid logging secrets; use a managed secret store and strict access controls. |
| Broad filesystem access | The client can enumerate files under the current user profile. | Apply explicit directory allowlists and least-privilege permissions. |
| Unrestricted command queue | Connected clients may receive file-operation commands. | Use a fixed allowlist of harmless actions, authorization, and audit trails. |
| Listener binds to all interfaces | The service may be reachable from other hosts, depending on network controls. | Keep analysis isolated and restrict network exposure. |

## 🧪 Safe Analysis Workflow

1. Review the source statically before executing anything.
2. If dynamic analysis is authorized, use a disposable, isolated virtual machine with snapshots.
3. Disconnect the lab from production networks and block outbound access.
4. Use synthetic files only—never personal or business data.
5. Record network requests, filesystem changes, and process behavior.
6. Revert the VM snapshot after analysis and securely remove test artifacts.

## 🧰 Technologies Observed

- **Python** — application logic
- **Requests** — HTTP client communication
- **`http.server`** — basic HTTP server
- **Tkinter** — desktop GUI
- **Fernet (`cryptography`)** — symmetric authenticated encryption

## 📁 Project Structure

```text
repository/
├── README.md
├── Client.py
├── Server.py
└── docs/
    └── images/
        └── banner.png
```

This layout describes the supplied source files and documentation assets; it does not mean the code is safe to execute.

## 🚑 Incident-Response Notes

If you find this software running without authorization:

- Isolate the affected host from the network.
- Preserve relevant logs and evidence.
- Investigate files with unexpected `.enc` extensions and determine whether originals remain available.
- Do not assume a saved key file is trustworthy or that decryption will succeed.
- Restore from verified offline backups where necessary.
- Follow your organization's incident-response process and involve qualified security personnel.

## 🚀 Safe Future Direction

For a portfolio-ready defensive project, replace remote command execution and destructive file operations with:

- A **read-only telemetry simulator** using synthetic events.
- A local dashboard showing mock clients and harmless event logs.
- A ransomware-behavior detector that flags suspicious mass file modifications.
- A test harness that operates only on in-memory strings or temporary generated fixtures without deleting originals.
- Unit tests and documented detection rules.

## 👨‍💻 Author

**David Hany**  
Computer Science & Artificial Intelligence • Cybersecurity

GitHub: [@davidhany10](https://github.com/davidhany10)

---

<p align="center"><strong>Analyze Safely • Detect Threats • Protect Systems</strong></p>
"""

(base / "README.md").write_text(readme, encoding="utf-8")

banner_src = Path("/mnt/data/a_clean_dark_cyberpunk_themed_project_readme_post.png")
if banner_src.exists():
    shutil.copy2(banner_src, base / "docs" / "images" / "banner.png")
else:
    (base / "docs" / "images" / "IMAGE_PLACEHOLDER.txt").write_text(
        "Place an approved defensive-security banner here as banner.png.\n",
        encoding="utf-8"
    )

zip_path = Path("/mnt/data/rat_security_review_github.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in base.rglob("*"):
        if p.is_file():
            zf.write(p, p.relative_to(base.parent))

print("Created:")
print(zip_path)
print(base / "README.md")
print(base / "docs" / "images" / "banner.png")
