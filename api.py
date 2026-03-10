from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

GITHUB_TOKEN = ""
GITHUB_REPO = ""
BRANCH = "main"
FOLDER = "data"


def github_api_url(path):
 return f"{GITHUB_REPO}/contents/{path}"

def get_headers():
 return {
  "Authorization": f"token {GITHUB_TOKEN}",
  "Accept": "application/vnd.github.v3+json"
 }

def file_exists(filename):
 url = github_api_url(f"{FOLDER}/{filename}.txt")
 response = requests.get(url, headers=get_headers())
 return response.status_code == 200, response.json().get("sha") if response.status_code == 200 else None

@app.route("/add-file", methods=["POST"])
def add_file():
 filename = request.args.get("filename")
 if not filename:
  return jsonify({"error": "Filename is required"}), 400
 exists, _ = file_exists(filename)
 if exists:
  return jsonify({"error": "File already exists"}), 400
 data = {
  "message": f"Add file {filename}",
  "content": base64.b64encode("".encode()).decode(),
  "branch": BRANCH
 }
 response = requests.put(github_api_url(f"{FOLDER}/{filename}.txt"), headers=get_headers(), json=data)
 if response.status_code in [200, 201]:
  return jsonify({"message": f"File {filename} created successfully"}), 200
 return jsonify({"error": "GitHub error", "details": response.json()}), 500

@app.route("/edit-file", methods=["PUT"])
def edit_file():
 filename = request.args.get("filename")
 if not filename:
  return jsonify({"error": "Filename is required"}), 400
 try:
  content = request.get_data(as_text=True)
 except:
  return jsonify({"error": "Failed to read content from body"}), 400
 if content is None:
  return jsonify({"error": "Content is required in body"}), 400
 exists, sha = file_exists(filename)
 if not exists:
  return jsonify({"error": "File does not exist"}), 404
 data = {
  "message": f"Edit file {filename}",
  "content": base64.b64encode(content.encode()).decode(),
  "branch": BRANCH,
  "sha": sha
 }
 response = requests.put(
  github_api_url(f"{FOLDER}/{filename}.txt"),
  headers=get_headers(),
  json=data
 )
 if response.status_code in [200, 201]:
  return jsonify({"message": f"File {filename} updated successfully"}), 200
 return jsonify({"error": "GitHub error", "details": response.json()}), 500

@app.route("/del-file", methods=["DELETE"])
def delete_file():
 filename = request.args.get("filename")
 if not filename:
  return jsonify({"error": "Filename is required"}), 400
 exists, sha = file_exists(filename)
 if not exists:
  return jsonify({"error": "File does not exist"}), 404
 data = {
  "message": f"Delete file {filename}",
  "sha": sha,
  "branch": BRANCH
 }
 response = requests.delete(github_api_url(f"{FOLDER}/{filename}.txt"), headers=get_headers(), json=data)
 if response.status_code == 200:
  return jsonify({"message": f"File {filename} deleted successfully"}), 200
 return jsonify({"error": "GitHub error", "details": response.json()}), 500


def get_file_content(data):
 if "content" in data and data["content"]:
  try:
   return base64.b64decode(data["content"]).decode()
  except Exception:
   return ""
 elif "download_url" in data and data["download_url"]:
  try:
   r = requests.get(data["download_url"])
   return r.text if r.status_code == 200 else ""
  except Exception:
   return ""
 else:
  return ""


@app.route("/check", methods=["GET"])
def check_file():
 filename = request.args.get("filename")
 if not filename:
  return jsonify({"error": "Filename is required"}), 400
 url = github_api_url(f"{FOLDER}/{filename}.txt")
 response = requests.get(url, headers=get_headers())
 if response.status_code == 200:
  data = response.json()
  content = get_file_content(data)
  return jsonify({"filename": filename, "content": content}), 200
 return jsonify({"error": "File does not exist"}), 404


@app.route("/check-all", methods=["GET"])
def check_all():
 url = github_api_url(FOLDER)
 response = requests.get(url, headers=get_headers())
 if response.status_code != 200:
  return jsonify({"error": "Failed to list files", "details": response.json()}), 500

 files = []
 for item in response.json():
  filename = item["name"].replace(".txt", "")
  file_resp = requests.get(item["url"], headers=get_headers())
  if file_resp.status_code == 200:
   data = file_resp.json()
   content = get_file_content(data)
  else:
   content = ""
  files.append({"filename": filename, "content": content})

 return jsonify({"files": files}), 200


if __name__ == "__main__":
 app.run()