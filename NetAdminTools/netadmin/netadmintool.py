#  pip install gradio requests python-nmap


import gradio as gr
import socket
import requests
import nmap
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import warnings
import logging

# Configure logging to suppress unnecessary warnings
logging.getLogger("gradio").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return f"Local IP Address: {local_ip}"
    except Exception as e:
        return f"Error detecting local IP: {str(e)}"

def get_public_ip():
    """Get the public IP address as seen from the internet"""
    try:
        response = requests.get("https://api.ipify.org?format=json")
        public_ip = response.json()["ip"]
        return f"Public IP Address: {public_ip}"
    except Exception as e:
        return f"Error detecting public IP: {str(e)}"

def scan_network(progress=gr.Progress()):
    """Scan the local network for active devices"""
    try:
        # Get local IP and construct network address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Calculate network address (assuming /24 network)
        network = str(ipaddress.IPv4Interface(f"{local_ip}/24").network)
        
        # Initialize scanner
        nm = nmap.PortScanner()
        
        # Perform quick ping scan
        result = nm.scan(hosts=network, arguments="-sn")
        
        # Format results
        active_hosts = []
        for host in nm.all_hosts():
            try:
                hostname = socket.gethostbyaddr(host)[0]
            except:
                hostname = "Unknown"
            active_hosts.append(f"Host: {host} (Hostname: {hostname})")
        
        return "\n".join([
            f"Network Scan Results ({network}):",
            "----------------------------------------",
            *active_hosts
        ])
    except Exception as e:
        return f"Error scanning network: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Network Admin Utility") as iface:
    gr.Markdown("# Network Administrator Utility")
    
    with gr.Row():
        with gr.Column():
            local_ip_btn = gr.Button("Detect Local IP")
            local_ip_output = gr.Textbox(label="Local IP Result")
            
        with gr.Column():
            public_ip_btn = gr.Button("Detect Public IP")
            public_ip_output = gr.Textbox(label="Public IP Result")
    
    with gr.Row():
        scan_btn = gr.Button("Scan Local Network")
        scan_output = gr.Textbox(label="Network Scan Results", lines=10)
    
    # Connect buttons to functions
    local_ip_btn.click(get_local_ip, outputs=local_ip_output)
    public_ip_btn.click(get_public_ip, outputs=public_ip_output)
    scan_btn.click(scan_network, outputs=scan_output)

if __name__ == "__main__":
    try:
        # Try to launch with sharing first
        iface.launch(server_name="0.0.0.0", server_port=8760, share=True)
    except Exception as e:
        print(f"\nNote: Couldn't enable sharing feature. Running in local-only mode.")
        # Fall back to local-only mode if sharing fails
        iface.launch(server_name="0.0.0.0", server_port=8760, share=False)