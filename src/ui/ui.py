import gradio as gr
import requests
import json
import os
import sys
import time
import urllib.parse
import threading
from queue import Queue, Empty
import re

# Force immediate output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=== STARTING UI APPLICATION ===", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Current working directory: {os.getcwd()}", flush=True)

# Get the base URLs from the environment, with a default fallback
MCP_BASE = os.getenv("SG_BASE", "http://127.0.0.1:9000")
DIRECT_API_BASE = os.getenv("DIRECT_API_BASE", "http://127.0.0.1:8000")

print(f"MCP_BASE: {MCP_BASE}", flush=True)
print(f"DIRECT_API_BASE: {DIRECT_API_BASE}", flush=True)

# Shared state for communication between threads
q = Queue()
session_id_event = threading.Event()
session_id_container = {}
sse_thread = None

def _wait_for_service(url: str, timeout: int = 60, service_name: str = "service") -> bool:
    """Wait for a service to become available"""
    print(f"Waiting for {service_name} at {url}...", flush=True)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try the SSE endpoint directly for MCP service
            test_url = f"{url}/sse" if "MCP" in service_name else url
            response = requests.get(test_url, timeout=5, stream=True)
            print(f"   - {service_name} responded with status: {response.status_code}", flush=True)
            if response.status_code == 200:
                print(f"{service_name} is ready!", flush=True)
                response.close()
                return True
            elif response.status_code < 500:  # Any non-server error is probably okay
                print(f"{service_name} is responding (status {response.status_code}), considering ready!", flush=True)
                response.close()
                return True
        except requests.exceptions.RequestException as e:
            print(f"Waiting for {service_name}... ({e})", flush=True)
            time.sleep(2)
    
    print(f"Timeout waiting for {service_name}", flush=True)
    return False

def _post_with_retry(endpoint: str, body: dict, retries: int = 3, delay_seconds: float = 0.5) -> tuple[int, str]:
    """
    Sends a POST request with retry logic. Handles '202 Accepted' as a success and retries 
    on intermittent network issues (e.g., 503).
    """
    try:
        r = requests.post(endpoint, json=body, timeout=30)
        # 202 Accepted is the expected response for an async call.
        if r.status_code == 202:
            return 200, "Request Accepted" # Treat as a success for our script
        
        if r.status_code != 503:
            return r.status_code, r.text
        
        # Retry a few times if the gateway returns a a 503
        for i in range(retries):
            time.sleep(delay_seconds * (i + 1)) # Exponential backoff
            r = requests.post(endpoint, json=body, timeout=30)
            if r.status_code != 503:
                return r.status_code, r.text
    except Exception as e:
        return 0, str(e)
    
    return 503, "All retries failed to get a non-503 or 202 response."

def sse_reader(base_url):
    """Continuously reads from the SSE stream in a separate thread, with auto-reconnect."""
    print(f"SSE Reader starting, base_url: {base_url}", flush=True)
    
    # Wait for MCP service to be ready before attempting SSE connection
    if not _wait_for_service(base_url, timeout=120, service_name="MCP service"):
        print("MCP service never became available, SSE reader exiting", flush=True)
        return
    
    while True:
        sse_url = f"{base_url}/sse"
        response = None
        try:
            # Clear previous session ID and event on reconnect
            if session_id_event.is_set():
                session_id_event.clear()
                session_id_container.clear()
                print("\nReconnecting to SSE stream...", flush=True)

            print(f"1. Connecting to SSE stream at: {sse_url}", flush=True)
            response = requests.get(
                sse_url,
                stream=True,
                timeout=(10, None),  # No read timeout for SSE
                headers={
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                },
            )
            print(f"   - Response status: {response.status_code}", flush=True)
            response.raise_for_status()
            print("   - SSE connection established successfully.", flush=True)

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                    
                line = line.strip()
                print(f"   - SSE received: {line}", flush=True)
                
                if line.startswith("data: "):
                    payload = line[6:]  # Remove "data: " prefix
                    print(f"   - Processing payload: {payload}", flush=True)
                    
                    # First, check if we need to extract the session ID
                    if not session_id_event.is_set():
                        # Look for sessionId in the payload
                        if "sessionId=" in payload:
                            try:
                                # Extract sessionId using regex
                                match = re.search(r'sessionId=([a-f0-9\-]+)', payload)
                                if match:
                                    session_id = match.group(1)
                                    session_id_container['id'] = session_id
                                    session_id_event.set()
                                    print(f"2. Found session ID: {session_id}", flush=True)
                                else:
                                    # Try URL parsing as backup
                                    if "/message?sessionId=" in payload:
                                        parsed_url = urllib.parse.urlparse(payload)
                                        query_params = urllib.parse.parse_qs(parsed_url.query)
                                        if "sessionId" in query_params:
                                            session_id_container['id'] = query_params["sessionId"][0]
                                            session_id_event.set()
                                            print(f"2. Found session ID (backup method): {session_id_container['id']}", flush=True)
                            except Exception as e:
                                print(f"Error extracting session ID: {e}", flush=True)
                                continue
                    
                    # Try to parse as JSON for tool responses
                    try:
                        event_data = json.loads(payload)
                        # Once the session is active, put all events in the queue
                        q.put(event_data)
                        print(f"   - Queued JSON event: {event_data.get('id', 'no-id')}", flush=True)
                    except json.JSONDecodeError:
                        # Not JSON, might be initial connection data
                        print(f"   - Non-JSON payload: {payload}", flush=True)
                        pass
                        
        except Exception as e:
            print(f"Reader thread encountered an error: {e}", file=sys.stderr, flush=True)
            print("Attempting to reconnect in 5 seconds...", flush=True)
            time.sleep(5)
        finally:
            if response:
                response.close()

def _format_emotion_response(emotion: str, confidence: float) -> str:
    """Format emotion response with appropriate indicator"""
    # Use simple text indicators instead of emojis to avoid encoding issues
    emotion_indicators = {
        "happiness": "[HAPPY]",
        "joy": "[JOY]", 
        "happy": "[HAPPY]",
        "sadness": "[SAD]",
        "sad": "[SAD]",
        "anger": "[ANGRY]",
        "angry": "[ANGRY]",
        "fear": "[FEAR]",
        "scared": "[FEAR]",
        "disgust": "[DISGUST]",
        "surprise": "[SURPRISE]",
        "neutral": "[NEUTRAL]",
        "love": "[LOVE]",
        "excitement": "[EXCITED]"
    }
    
    indicator = emotion_indicators.get(emotion.lower(), "[UNKNOWN]")
    return f"{emotion.title()} {indicator} (Confidence: {confidence:.2%})"
    
    emoji = emotion_emojis.get(emotion.lower(), "🤔")
    return f"{emotion.title()} {emoji} (Confidence: {confidence:.2%})"

def _call_direct_api(text: str) -> tuple[int, str]:
    """Sends a request to the direct API endpoint."""
    direct_api_url = f"{DIRECT_API_BASE}/predict"
    payload = {
        "text": text
    }
    
    try:
        # Wait for the direct API to be ready
        if not _wait_for_service(DIRECT_API_BASE, timeout=30, service_name="Direct API"):
            return 0, "Direct API service is not available"
        
        r = requests.post(direct_api_url, json=payload, timeout=30)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

def process_message(input_text, api_choice):
    """
    Main function for the Gradio UI. It handles the message submission,
    sends the POST request, and waits for a result.
    """
    if api_choice == "Direct API":
        yield "Calling Direct API..."
        status_code, response_text = _call_direct_api(input_text)
        if status_code == 200:
            try:
                response_data = json.loads(response_text)
                emotion = response_data.get("emotion")
                confidence = response_data.get("confidence")
                
                if emotion is not None and confidence is not None:
                    # Convert confidence to float if it's not already
                    if isinstance(confidence, (int, float)):
                        confidence_float = float(confidence)
                    else:
                        confidence_float = 1.0  # Default if parsing fails
                    
                    formatted_result = _format_emotion_response(emotion, confidence_float)
                    yield f"Direct API Response:\n{formatted_result}"
                else:
                    yield f"Direct API Response: {response_text}"
            except json.JSONDecodeError:
                yield f"ERROR: Direct API response was not valid JSON: {response_text}"
        else:
            yield f"ERROR: Direct API call failed. Status: {status_code}. Response: {response_text}"
        return
    
    elif api_choice == "Supergateway (MCP)":
        # Wait for the session ID to be set by the background thread
        yield "Waiting for SSE connection to be established..."
        if not session_id_event.wait(timeout=30):  # Increased timeout
            yield "ERROR: Failed to establish SSE connection within 30 seconds. Please check the MCP service."
            return

        session_id = session_id_container.get('id')
        if not session_id:
            yield "ERROR: Session ID was not captured. Please restart the application."
            return

        # Clear the queue before sending request
        while not q.empty():
            try:
                q.get_nowait()
            except Empty:
                break

        # Send the 'tools/call' request with retry logic.
        message_url = f"{MCP_BASE}/message?sessionId={urllib.parse.quote_plus(session_id)}"
        print(f"3. Sending 'tools/call' request to {message_url}...", flush=True)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "emotion_detection",
                "arguments": {"text": input_text},
            },
        }
        
        post_response_code, post_response_text = _post_with_retry(message_url, payload)
        
        if post_response_code != 200:
            yield f"ERROR: POST request failed. Status: {post_response_code}. Response: {post_response_text}"
            return
        
        yield "Request sent. Waiting for response..."
        
        # Wait for the result from the reader thread's queue.
        deadline = time.time() + 60  # Set a timeout for waiting
        while time.time() < deadline:
            try:
                event_data = q.get(timeout=1.0)
                print(f"Processing queue item: {event_data}", flush=True)
                
                # Check if this is our response
                if isinstance(event_data, dict) and event_data.get("id") == 1:
                    if "result" in event_data:
                        result = event_data["result"]
                        print(f"MCP result received: {json.dumps(result, indent=2)}", flush=True)
                        if isinstance(result, dict) and "content" in result:
                            content = result["content"]
                            if isinstance(content, list) and len(content) > 0:
                                text_content = content[0].get("text", "")
                                print(f"MCP text content: '{text_content}'", flush=True)
                                if text_content:
                                    # Try to parse the MCP response to extract emotion and confidence
                                    # Expected format: "Emotion: <emotion> (Confidence: <confidence>%)"
                                    try:
                                        # Try to extract emotion and confidence from the text
                                        import re
                                        # Look for pattern like "Emotion: <emotion> (Confidence: <confidence>%)"
                                        # This now expects NO emoji from the MCP server
                                        match = re.search(r'Emotion:\s*([^(]+?)\s*\(Confidence:\s*([0-9.]+)%\)', text_content)
                                        if match:
                                            emotion_part = match.group(1).strip()
                                            confidence_str = match.group(2)
                                            confidence = float(confidence_str) / 100.0
                                            
                                            # Use the UI's emoji mapping function consistently
                                            formatted_response = _format_emotion_response(emotion_part, confidence)
                                            yield f"MCP Response: {formatted_response}"
                                            return
                                    except Exception as e:
                                        print(f"Error parsing MCP response: {e}", flush=True)
                                    
                                    # Fallback: just show the original text
                                    yield f"MCP Response: {text_content}"
                                    return
                        # Fallback - just show the result as is
                        yield f"MCP Response: {json.dumps(result, indent=2)}"
                        return
                    elif "error" in event_data:
                        yield f"MCP Error: {event_data['error']}"
                        return
            except Empty:
                continue
            except Exception as e:
                print(f"Error processing queue item: {e}", flush=True)
                continue
        
        yield "TIMEOUT: Waited too long for the result from MCP service."

# Function to start the background thread on Gradio load
def start_sse_thread():
    global sse_thread
    if sse_thread is None or not sse_thread.is_alive():
        print("Starting background SSE reader thread...", flush=True)
        sse_thread = threading.Thread(target=sse_reader, args=(MCP_BASE,), daemon=True)
        sse_thread.start()

# Gradio UI components
with gr.Blocks(title="MCP Emotion Detector") as demo:
    gr.Markdown("# MCP Emotion Detector")
    gr.Markdown("Select your API endpoint and enter a message to send to the Supergateway.")
    
    with gr.Row():
        api_choice = gr.Radio(choices=["Supergateway (MCP)", "Direct API"], label="API Endpoint", value="Supergateway (MCP)")
    
    with gr.Row():
        message_input = gr.Textbox(
            label="Message to Analyze"
        )
        output_textbox = gr.Textbox(label="Result", interactive=False)
    
    # Add a separate gr.Examples component
    gr.Examples(
        examples=[
            "I am so happy with this test!",
            "I feel quite neutral about this.",
            "I am getting angry with this failure.",
            "I am filled with sadness.",
            "This news has made me feel love.",
            "I am so angry right now.",
            "I am scared of the dark."
        ],
        inputs=message_input,
        label="Try these examples"
    )

    with gr.Row():
        submit_btn = gr.Button("Submit", variant="primary")

    submit_btn.click(
        fn=process_message,
        inputs=[message_input, api_choice],
        outputs=output_textbox
    )
    
    # Start the SSE thread when the Gradio app is loaded in the browser
    demo.load(fn=start_sse_thread)

if __name__ == "__main__":
    print("=== LAUNCHING GRADIO APP ===", flush=True)
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )
    print("=== GRADIO APP LAUNCHED ===", flush=True)
