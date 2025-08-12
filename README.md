# VaultGo

VaultGo is a minimal cloud storage service built with Django and PostgreSQL. Uploaded files are encrypted on disk and served through the Django backend. The project ships with Docker so it can be started with a few commands.

## Tools
- Python / Django
- PostgreSQL
- Docker Compose

## Quick Start

🚀 **Automated setup with secure configuration:**

```bash
./setup.sh
docker compose build
docker compose up
```

The setup script automatically generates:
- Secure Django secret key
- File encryption key
- Random database password
- Environment configuration

## Features

- 🔒 **File Encryption**: All uploaded files are encrypted at rest
- 👤 **User Authentication**: Secure user accounts with Argon2 password hashing
- 📁 **Folder Management**: Create, organize, and navigate folders
- 🖱️ **Drag & Drop**: Move files and folders with drag and drop
- ⌨️ **Keyboard Shortcuts**: Use Enter/Escape for quick actions
- 🎨 **Clean UI**: Dark theme with intuitive file management
