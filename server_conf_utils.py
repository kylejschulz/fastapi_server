import shutil
import os
import subprocess
import asyncio

def restart_nginx():
    try:
        # Check Nginx status
        status = subprocess.run(["systemctl", "status", "nginx"], capture_output=True, text=True)
        if status.returncode != 0:
            print("Nginx is not running. Starting Nginx...")
        else:
            print("Restarting Nginx...")

        # Restart Nginx
        subprocess.run(["sudo", "systemctl", "restart", "nginx"], check=True)
        print("Nginx restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while restarting Nginx: {e}")

async def restart_nginx_async():
    """Asynchronous wrapper for restarting Nginx."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, restart_nginx)

def delete_subdomain_dir(subdomain):
    subdomain_path = os.path.join("/var/www/subdomains", subdomain)

    try:
        # Check if the directory exists
        if os.path.exists(subdomain_path) and os.path.isdir(subdomain_path):
            # Recursively delete the directory
            shutil.rmtree(subdomain_path)
            print(f"Directory deleted: {subdomain_path}")
        else:
            print(f"No directory found at: {subdomain_path}")
    except Exception as e:
        print(f"Failed to delete directory {subdomain_path}: {e}")


def remove_nginx_site(subdomain):
    """
    Safely removes a file from /etc/nginx/sites-available for a given subdomain.
    
    :param subdomain: The name of the subdomain configuration to remove
    :raises ValueError: If the subdomain contains invalid characters
    :raises FileNotFoundError: If the specified file does not exist
    :raises Exception: For other errors during the removal process
    """
    # Validate subdomain input
    if not subdomain.isalnum() and '-' not in subdomain:
        raise ValueError("Invalid subdomain name. Only alphanumeric characters and dashes are allowed.")
    
    file_path = f"/etc/nginx/sites-available/{subdomain}"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    try:
        # Execute the command to remove the file
        subprocess.run(["rm", file_path], check=True)
        print(f"Successfully removed: {file_path}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to remove the file: {e}")

def run_certbot(subdomain):
    try:
        # Construct the certbot command
        command = ["certbot", "--nginx", "-d", "{}.mariposapro.xyz".format(subdomain)]
        
        # Execute the command
        subprocess.run(command, check=True)
        print(f"Successfully obtained SSL certificate for {subdomain}.mariposapro.xyz")
    except subprocess.CalledProcessError as e:
        print(f"Error executing certbot command: {e}")
    except FileNotFoundError:
        print("Certbot is not installed. Please install it using 'sudo apt install certbot python3-certbot-nginx'.")

def config_server(subdomain):
    nginx_config = """
    # subdomain:{} #
    server {{
      listen         80;
      server_name  {}.mariposapro.xyz;
      return         301 https://$server_name$request_uri;
    }}
    server {{
      listen 443 ssl;
      ssl_certificate /etc/letsencrypt/live/mariposapro.xyz/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/mariposapro.xyz/privkey.pem;
      server_name {}.mariposapro.xyz;
      access_log /var/log/nginx/{}.access.log;
      location / {{
        root /var/www/subdomains/{};
        index index.html;
      }}
    }}
    """.format(subdomain, subdomain, subdomain, subdomain, subdomain)
    
    # Define the path and filename for the config file
    config_path = "/etc/nginx/sites-available/"
    filename = subdomain
    
    # Ensure the directory exists
    os.makedirs(config_path, exist_ok=True)
    
    # Write the nginx config to a file
    config_file_path = os.path.join(config_path, filename)
    try:
        with open(config_file_path, 'w') as f:
            f.write(nginx_config)
        print(f"Configuration file written to {config_file_path}")
    except Exception as e:
        print(f"Failed to write config file: {e}")



def make_server_config(subdomain):
   # This will make the server config file in /etc/nginx/sites-available/{subdomain}.conf
    print("hello")

def make_symlink(subdomain):
    available_path = f"/etc/nginx/sites-available/{subdomain}"
    enabled_path = f"/etc/nginx/sites-enabled/{subdomain}"

    try:
        # Create the symlink
        os.symlink(available_path, enabled_path)
        print(f"Symlink created: {enabled_path} -> {available_path}")
    except FileExistsError:
        print(f"Symlink already exists: {enabled_path}")
    except Exception as e:
        print(f"Failed to create symlink: {e}")

def delete_symlink(subdomain):
    enabled_path = f"/etc/nginx/sites-enabled/{subdomain}"

    try:
        # Check if the symlink exists and delete it
        if os.path.islink(enabled_path):
            os.unlink(enabled_path)
            print(f"Symlink deleted: {enabled_path}")
        else:
            print(f"No symlink exists at: {enabled_path}")
    except Exception as e:
        print(f"Failed to delete symlink: {e}")

