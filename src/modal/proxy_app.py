import modal
import subprocess
import time
import threading
import requests
from flask import Flask, request, Response

# Define the custom Docker image using your Dockerfile
go_image = modal.Image.from_dockerfile("Dockerfile")

# Define the app
app = modal.App("go-web-server-example")

# Global variable to store the Go server process
go_process = None

def start_go_server():
    global go_process
    go_process = subprocess.Popen(["./server"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
    print(f"Started Go server with PID: {go_process.pid}")
    time.sleep(2)  # Wait for server to start

# Use the Go image directly for the web server
@app.function(image=go_image)
@modal.web_server(port=8000)
def serve():
    # Start the Go server in a separate thread
    go_thread = threading.Thread(target=start_go_server)
    go_thread.daemon = True
    go_thread.start()
    
    # Wait for the Go server to start
    time.sleep(3)
    
    # Check if the Go server is running
    if go_process and go_process.poll() is None:
        print("Go server is running successfully")
    else:
        print("Go server failed to start")
        return "Go server failed to start"
    
    # Create a Flask app to proxy requests to the Go server
    web_app = Flask(__name__)
    
    @web_app.route('/', defaults={'path': ''})
    @web_app.route('/<path:path>')
    def proxy(path):
        try:
            # Forward the request to the Go server
            url = f"http://localhost:8000/{path}"
            if request.query_string:
                url += f"?{request.query_string.decode()}"
            
            # Make the request to the Go server
            response = requests.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                data=request.get_data(),
                timeout=30
            )
            
            # Return the response from the Go server
            return Response(
                response.content,
                status=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            return f"Error proxying request: {str(e)}", 500
    
    # Return the Flask app
    return web_app
