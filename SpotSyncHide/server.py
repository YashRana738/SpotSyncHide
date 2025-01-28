from flask import Flask, request, send_file
import os
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/process-file", methods=["POST"])
def process_file():
    # Get the uploaded file
    file = request.files["file"]

    # Save the file temporarily
    original_filename = file.filename
    file_path = f"temp_{original_filename}"
    file.save(file_path)

    # Read the file as binary data
    with open(file_path, "rb") as f:
        data = f.read()

    # Hardcoded search and replace strings
    search_str = "connect-state"
    replace_str = "skibidi-sigma"

    # Convert strings to bytes
    search_bytes = search_str.encode("utf-8")
    replace_bytes = replace_str.encode("utf-8")

    # Replace the hex values
    if search_bytes in data:
        data = data.replace(search_bytes, replace_bytes)

        # Save the modified file
        with open(file_path, "wb") as f:
            f.write(data)

        # Rename the file
        output_filename = original_filename.replace(".", "_no-Jam.")
        output_path = f"temp_{output_filename}"
        os.rename(file_path, output_path)

        # Sign the APK if it's an APK file
        if output_filename.endswith(".apk"):
            try:
                subprocess.run(["apktool", "d", output_path, "-o", "temp_apk"], check=True)
                subprocess.run(["apktool", "b", "temp_apk", "-o", output_path], check=True)
                subprocess.run(["apksigner", "sign", "--ks", "myKeystore.jks", "--ks-pass", "pass:your_password", output_path], check=True)
            except subprocess.CalledProcessError as e:
                return f"Error signing APK: {e}", 500

        # Send the modified file back to the user
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    else:
        return "Search string not found in file!", 400

if __name__ == "__main__":
    app.run(debug=True)