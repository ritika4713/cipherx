import io
from flask import Flask, request, send_file, jsonify
from cipherx_core import CipherXError, EXT, encrypt_bytes, decrypt_bytes

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # Vercel request limit is ~4.5 MB


def _handle(fn, out_name):
    f, pw = request.files.get("file"), request.form.get("password", "")
    if not f or not f.filename:
        return jsonify(error="Choose a file first."), 400
    try:
        out = fn(f.read(), pw)
    except CipherXError as e:
        return jsonify(error=str(e)), 400
    name = out_name(f.filename)
    resp = send_file(io.BytesIO(out), mimetype="application/octet-stream",
                     as_attachment=True, download_name=name)
    resp.headers["X-Filename"] = name
    resp.headers["Access-Control-Expose-Headers"] = "X-Filename"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.post("/api/encrypt")
def encrypt():
    return _handle(encrypt_bytes, lambda n: n + EXT)


@app.post("/api/decrypt")
def decrypt():
    return _handle(decrypt_bytes, lambda n: n[:-len(EXT)] if n.endswith(EXT) else n + ".decrypted")


@app.errorhandler(413)
def too_big(_):
    return jsonify(error="File is larger than 4 MB. Use the desktop version for bigger files."), 413
