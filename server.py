#uvicorn server:app --reload
# curl -X POST "http://143.198.30.142:8000/deploy/static/subdomain/test-subdomain" \ 
# -F "file=@/Users/kyleschulz/Desktop/index.html"
#pip install python-multipart

from fastapi import FastAPI, HTTPException, Path, UploadFile, File
from pydantic import BaseModel
import os
from server_conf_utils import *
from typing import List

app = FastAPI()

# Directory to save uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/deploy/static/subdomain/{subdomain}")
async def deploy_static(
    subdomain: str = Path(..., description="The subdomain to deploy"),
    files: List[UploadFile] = File(..., description="The files to upload"),
):
    
    saved_files = []

    for file in files:
        subdomain_path = os.path.join("/var/www/subdomains/", subdomain)
        file_path = os.path.join("/var/www/subdomains/", subdomain, file.filename)

        os.makedirs(subdomain_path, exist_ok=True)

        try:
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_files.append({"filename": file.filename, "saved_path": file_path})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save {file.filename}: {e}")
    config_server(subdomain)
    make_symlink(subdomain)
    #run_certbot(subdomain)

    new_subdomain = "{}.mariposapro.xyz".format(subdomain)

    asyncio.create_task(restart_nginx_async())

    return {
        "message": "Files uploaded successfully",
        "subdomain": subdomain,
        "saved_files": saved_files,
        "new_site": new_subdomain,
    }

@app.delete("/deploy/static/subdomain/{subdomain}")
async def delete_static(
    subdomain: str = Path(..., description="The subdomain to delete")
):
    remove_nginx_site(subdomain)
    delete_subdomain_dir(subdomain)
    delete_symlink(subdomain)
    
    return {
        "message": "Files deleted successfully",
        "subdomain": subdomain,
    }


# To run the server, save this code to a file (e.g., `server.py`) and run:
# `uvicorn server:app --reload`

