import subprocess
import urllib.request
import datetime
import ssl
import time
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_container(container_name, timeout=300):
    #Comment
    """
    Wait for a Docker container to become ready.

    Args:
        container_name (str): Name of the Docker container.
        timeout (int): Timeout duration in seconds (default is 300).

    Returns:
        bool: True if container is ready, False otherwise.
    """
    logger.info(f"Waiting for {container_name} container to be ready...")
    start_time = time.time()
    while True:
        try:
            # Check if the container is running
            result = subprocess.run(['docker', 'inspect', '-f', '{{.State.Running}}', container_name], capture_output=True, text=True)
            logger.debug(f"Inspect command output for {container_name}: {result.stdout.strip()}")
            if result.stdout.strip() == "true":
                logger.info(f"{container_name} container is up and running.")
                return True
        except Exception as e:
            logger.error(f"Error checking container status for {container_name}: {e}")
        
        if time.time() - start_time > timeout:
            logger.warning(f"Timeout waiting for {container_name} container to be ready.")
            return False
        
        time.sleep(5)

def send_data_to_url(url, context, container_name):
    """
    Send data to a specified URL.

    Args:
        url (str): URL to send data to.
        context (ssl.SSLContext): SSL context for HTTPS connections.
        container_name (str): Name of the Docker container associated with the data.

    """
    try:
        ts = datetime.datetime.now()
        full_url = f"{url}&container={container_name}"
        with urllib.request.urlopen(full_url, context=context) as response:
            if response.getcode() == 200:
                logger.info(f"{ts} Pushed data to {full_url} successfully!")
            else:
                logger.warning(f"{ts} Failed to push data to {full_url}. Status code: {response.getcode()}")
    except Exception as e:
        logger.error(f"Error sending data to {full_url}: {e}")

if __name__ == "__main__":
    # Get absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    urls_file = os.path.join(script_dir, 'urls.json')

    # Load URLs from JSON file
    with open(urls_file, 'r') as file:
        data = json.load(file)
        urls = data['urls']
    
    docker_container_names = ["emqx", "thingtrax_devices", "mongodb"] 
    context = ssl._create_unverified_context()

    while True:
        # Iterate through containers and URLs sequentially
        for container, url_entry in zip(docker_container_names, urls):
            url_name = url_entry['name']
            url = url_entry['url']
            
            if wait_for_container(container):
                # Container is ready, send data to corresponding URL
                send_data_to_url(url, context, container)
            else
                logger.error(f"Failed to confirm {container} container is running.")
        
        time.sleep(30)  
