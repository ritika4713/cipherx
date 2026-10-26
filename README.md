# CipherX – Secure File Encryption and Decryption Tool

B.Tech CSE mini project (Lloyd Institute of Engineering & Technology, AKTU).
Password-based file protection using Python and the `cryptography` library.

- **Encryption:** AES-256-GCM (authenticated encryption, FIPS 197)
- **Key derivation:** PBKDF2-HMAC-SHA256, 600,000 iterations, random 16-byte salt (NIST SP 800-132)
- **Integrity:** wrong passwords and modified/damaged files fail with a clear error
- **Interfaces:** web app (Flask on Vercel) and desktop app (Tkinter)

## Structure
```
api/cipherx_core.py   crypto logic (shared)
api/index.py          Flask API: /api/encrypt, /api/decrypt
public/index.html     web interface
cipherx_desktop.py    Tkinter desktop app
vercel.json           routing
```

## Run locally
```
pip install -r requirements.txt
python cipherx_desktop.py          # desktop app
```

## Deploy on Vercel
1. Push this folder to a GitHub repository.
2. On vercel.com choose **Add New → Project**, import the repo, keep the defaults, click **Deploy**.

Limits: Vercel allows ~4.5 MB per request, so the web version accepts files up to 4 MB. Use the desktop app for larger files.
