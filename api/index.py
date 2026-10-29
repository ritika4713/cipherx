import io
import os
import sys
from flask import Flask, request, send_file, jsonify
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cipherx_core import CipherXError, EXT, encrypt_bytes, decrypt_bytes

app = Flask(__name__)
MAX_MB = int(os.environ.get("MAX_UPLOAD_MB", "100"))  # note: Vercel itself caps requests at ~4.5 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024


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


@app.post("/", defaults={"path": ""})
@app.post("/<path:path>")
def dispatch(path):
    # Vercel's rewrite may change the path Flask sees, so match on the ending only.
    if path.endswith("encrypt"):
        return _handle(encrypt_bytes, lambda n: n + EXT)
    if path.endswith("decrypt"):
        return _handle(decrypt_bytes, lambda n: n[:-len(EXT)] if n.endswith(EXT) else n + ".decrypted")
    return jsonify(error="Unknown action."), 404


@app.errorhandler(413)
def too_big(_):
    return jsonify(error=f"File is larger than {MAX_MB} MB."), 413
