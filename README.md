# Still Wondering — Weekly Essays

A simple, server-rendered website for publishing weekly essays with section-targeted comments and read acknowledgments.

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY
python scripts/set_password.py admin
flask --app "app:create_app()" run
```

## Features

- **Markdown essays** with YouTube/audio embeds and images
- **Section-targeted comments** — readers click any paragraph to comment
- **"Eye" read acknowledgment** — one click per browser
- **Author login** — password set offline via script (Argon2 hash)
- **Image uploads** — validated, size-limited, randomized filenames

## Custom Markdown Syntax

```
!youtube[VIDEO_ID](start-end)   → YouTube embed (start/end in seconds, optional)
!audio[https://url/file.mp3]    → HTML5 audio player
![alt text](image-url)          → Standard Markdown image
```

## Deploy (Oracle Cloud VM)

1. Copy `deploy/essays.service` to `/etc/systemd/system/`
2. Copy `deploy/nginx-essays` to `/etc/nginx/sites-available/` and symlink to `sites-enabled`
3. Edit paths if not using `/opt/still_wondering`
4. `sudo systemctl enable --now essays`
5. `sudo systemctl restart nginx`

## Security

- Argon2 password hashing (offline-only set)
- CSRF on all forms (Flask-WTF)
- Rate limiting on login (5/min) and comments (10/min)
- CSP headers (YouTube iframe allowlisted, no inline scripts)
- Input sanitized via bleach (allowlist)
- File uploads validated (type + size)
- IP stored as SHA-256 hash only
- Open redirect protection on login
