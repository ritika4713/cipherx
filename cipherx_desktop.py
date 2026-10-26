"""CipherX desktop app (Tkinter). Run: python cipherx_desktop.py"""
import os, sys, tkinter as tk
from tkinter import filedialog, messagebox
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))
from cipherx_core import CipherXError, EXT, encrypt_bytes, decrypt_bytes

root = tk.Tk(); root.title("CipherX - Secure File Encryption and Decryption Tool")
root.geometry("460x230"); root.resizable(False, False)
path, pw = tk.StringVar(), tk.StringVar()

def browse():
    p = filedialog.askopenfilename()
    if p: path.set(p)

def run(encrypt):
    p = path.get()
    if not p or not os.path.isfile(p):
        return messagebox.showerror("CipherX", "Select a file first.")
    try:
        data = open(p, "rb").read()
        if encrypt:
            out, res = p + EXT, encrypt_bytes(data, pw.get())
        else:
            out = p[:-len(EXT)] if p.endswith(EXT) else p + ".decrypted"
            res = decrypt_bytes(data, pw.get())
        open(out, "wb").write(res)
        messagebox.showinfo("CipherX", f"Success. Saved as:\n{out}")
    except CipherXError as e:
        messagebox.showerror("CipherX", str(e))
    except OSError as e:
        messagebox.showerror("CipherX", f"File error: {e}")

tk.Label(root, text="File").pack(anchor="w", padx=16, pady=(16, 0))
r = tk.Frame(root); r.pack(fill="x", padx=16)
tk.Entry(r, textvariable=path).pack(side="left", fill="x", expand=True)
tk.Button(r, text="Browse", command=browse).pack(side="left", padx=(6, 0))
tk.Label(root, text="Password").pack(anchor="w", padx=16, pady=(12, 0))
tk.Entry(root, textvariable=pw, show="*").pack(fill="x", padx=16)
b = tk.Frame(root); b.pack(pady=18)
tk.Button(b, text="Encrypt", width=14, command=lambda: run(True)).pack(side="left", padx=6)
tk.Button(b, text="Decrypt", width=14, command=lambda: run(False)).pack(side="left", padx=6)
root.mainloop()
