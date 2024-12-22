# pip install speedtest-cli psutil python-whois gradio requests python-nmap

import gradio as gr
import socket
import requests
import nmap
import ipaddress
import subprocess
import whois
import warnings
import logging
import platform
import speedtest
import psutil
from datetime import datetime

# Configure logging to suppress unnecessary warnings
logging.getLogger("gradio").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
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
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        network = str(ipaddress.IPv4Interface(f"{local_ip}/24").network)
        nm = nmap.PortScanner()
        result = nm.scan(hosts=network, arguments="-sn")
        
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

def perform_dig(domain):
    """Perform DNS lookup using dig"""
    try:
        if not domain:
            return "Please enter a domain name"
        
        try:
            result = subprocess.check_output(['dig', domain], universal_newlines=True)
        except FileNotFoundError:
            result = subprocess.check_output(['nslookup', domain], universal_newlines=True)
        
        return result
    except Exception as e:
        return f"Error performing DNS lookup: {str(e)}"

def perform_whois(domain):
    """Perform WHOIS lookup"""
    try:
        if not domain:
            return "Please enter a domain name"
        
        w = whois.whois(domain)
        whois_info = []
        for key, value in w.items():
            if value:
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                whois_info.append(f"{key}: {value}")
        
        return "\n".join(whois_info)
    except Exception as e:
        return f"Error performing WHOIS lookup: {str(e)}"

def perform_traceroute(host):
    """Perform traceroute to a host"""
    try:
        if not host:
            return "Please enter a host name or IP address"
        
        if platform.system().lower() == "windows":
            cmd = ['tracert', host]
        else:
            cmd = ['traceroute', host]
        
        result = subprocess.check_output(cmd, universal_newlines=True)
        return result
    except Exception as e:
        return f"Error performing traceroute: {str(e)}"

def perform_port_scan(host, port_range="1-1024"):
    """Scan specified ports on a host"""
    try:
        if not host:
            return "Please enter a host name or IP address"
        
        start_port, end_port = map(int, port_range.split('-'))
        nm = nmap.PortScanner()
        result = nm.scan(host, f"{start_port}-{end_port}")
        
        output = [f"Port Scan Results for {host}:", "----------------------------------------"]
        
        if host in nm.all_hosts():
            for protocol in nm[host].all_protocols():
                output.append(f"\nProtocol: {protocol}")
                ports = nm[host][protocol].keys()
                for port in ports:
                    state = nm[host][protocol][port]['state']
                    service = nm[host][protocol][port]['name']
                    output.append(f"Port {port}: {state} ({service})")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error performing port scan: {str(e)}"

def check_speed():
    """Perform a speed test"""
    try:
        st = speedtest.Speedtest()
        output = ["Running speed test (this may take a minute)..."]
        
        output.append("\nFinding best server...")
        st.get_best_server()
        
        output.append("Testing download speed...")
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        
        output.append("Testing upload speed...")
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        
        output.append("Testing ping...")
        ping = st.results.ping
        
        output.extend([
            "\nResults:",
            f"Download Speed: {download_speed:.2f} Mbps",
            f"Upload Speed: {upload_speed:.2f} Mbps",
            f"Ping: {ping:.2f} ms"
        ])
        
        return "\n".join(output)
    except Exception as e:
        return f"Error performing speed test: {str(e)}"

def get_network_stats():
    """Get current network interface statistics"""
    try:
        stats = []
        stats.append("Network Interface Statistics:")
        stats.append("----------------------------------------")
        
        # Get network interfaces
        interfaces = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        io_counters = psutil.net_io_counters(pernic=True)
        
        for nic, stats_data in interfaces.items():
            stats.append(f"\nInterface: {nic}")
            stats.append(f"Status: {'Up' if stats_data.isup else 'Down'}")
            stats.append(f"Speed: {stats_data.speed} Mbps")
            
            # Add IP addresses
            if nic in addrs:
                for addr in addrs[nic]:
                    if addr.family == socket.AF_INET:
                        stats.append(f"IPv4 Address: {addr.address}")
                    elif addr.family == socket.AF_INET6:
                        stats.append(f"IPv6 Address: {addr.address}")
            
            # Add IO statistics
            if nic in io_counters:
                io = io_counters[nic]
                stats.append(f"Bytes Sent: {io.bytes_sent:,}")
                stats.append(f"Bytes Received: {io.bytes_recv:,}")
                stats.append(f"Packets Sent: {io.packets_sent:,}")
                stats.append(f"Packets Received: {io.packets_recv:,}")
        
        return "\n".join(stats)
    except Exception as e:
        return f"Error getting network statistics: {str(e)}"

def test_connectivity(host="8.8.8.8"):
    """Test connectivity to a host using ping"""
    try:
        if platform.system().lower() == "windows":
            ping_cmd = ['ping', '-n', '4', host]
        else:
            ping_cmd = ['ping', '-c', '4', host]
        
        result = subprocess.check_output(ping_cmd, universal_newlines=True)
        return result
    except Exception as e:
        return f"Error testing connectivity: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Network Admin Utility") as iface:
    gr.Markdown("# Enhanced Network Administrator Utility")
    
    with gr.Tab("Basic Network Info"):
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
    
    with gr.Tab("DNS Tools"):
        with gr.Row():
            with gr.Column():
                dig_input = gr.Textbox(label="Enter domain for DNS lookup")
                dig_btn = gr.Button("Perform DNS Lookup")
                dig_output = gr.Textbox(label="DNS Lookup Results", lines=10)
                
            with gr.Column():
                whois_input = gr.Textbox(label="Enter domain for WHOIS lookup")
                whois_btn = gr.Button("Perform WHOIS Lookup")
                whois_output = gr.Textbox(label="WHOIS Results", lines=10)
    
    with gr.Tab("Network Diagnostics"):
        with gr.Row():
            with gr.Column():
                traceroute_input = gr.Textbox(label="Enter host for traceroute")
                traceroute_btn = gr.Button("Perform Traceroute")
                traceroute_output = gr.Textbox(label="Traceroute Results", lines=15)
            
            with gr.Column():
                connectivity_input = gr.Textbox(label="Enter host for ping test", value="8.8.8.8")
                connectivity_btn = gr.Button("Test Connectivity")
                connectivity_output = gr.Textbox(label="Ping Results", lines=15)
    
    with gr.Tab("Advanced Tools"):
        with gr.Row():
            with gr.Column():
                port_scan_host = gr.Textbox(label="Enter host for port scan")
                port_scan_range = gr.Textbox(label="Port range (e.g., 1-1024)", value="1-1024")
                port_scan_btn = gr.Button("Scan Ports")
                port_scan_output = gr.Textbox(label="Port Scan Results", lines=15)
            
            with gr.Column():
                speed_test_btn = gr.Button("Run Speed Test")
                speed_test_output = gr.Textbox(label="Speed Test Results", lines=15)
        
        with gr.Row():
            network_stats_btn = gr.Button("Get Network Interface Statistics")
            network_stats_output = gr.Textbox(label="Network Statistics", lines=15)
    
    # Connect buttons to functions
    local_ip_btn.click(get_local_ip, outputs=local_ip_output)
    public_ip_btn.click(get_public_ip, outputs=public_ip_output)
    scan_btn.click(scan_network, outputs=scan_output)
    dig_btn.click(perform_dig, inputs=dig_input, outputs=dig_output)
    whois_btn.click(perform_whois, inputs=whois_input, outputs=whois_output)
    traceroute_btn.click(perform_traceroute, inputs=traceroute_input, outputs=traceroute_output)
    port_scan_btn.click(perform_port_scan, inputs=[port_scan_host, port_scan_range], outputs=port_scan_output)
    speed_test_btn.click(check_speed, outputs=speed_test_output)
    network_stats_btn.click(get_network_stats, outputs=network_stats_output)
    connectivity_btn.click(test_connectivity, inputs=connectivity_input, outputs=connectivity_output)

# Place this at the very end of the file, replacing the existing launch code

if __name__ == "__main__":
    def try_launch(start_port=8760, max_attempts=10):
        """Try to launch the interface on an available port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                print(f"Attempting to start server on port {port}...")
                iface.launch(server_name="0.0.0.0", server_port=port, share=True)
                return True
            except Exception as e:
                if "Cannot find empty port" in str(e) or "error while attempting to bind" in str(e):
                    print(f"Port {port} is in use, trying next port...")
                    continue
                else:
                    print(f"Unexpected error: {str(e)}")
                    return False
        return False

    # Try to launch with sharing enabled
    if not try_launch():
        print("\nAttempting to launch in local-only mode...")
        # Try again without sharing
        if not try_launch():
            print("\nFailed to find an available port. Please try the following:")
            print("1. Check for other running instances of this tool")
            print("2. Use a different starting port by modifying the start_port parameter")
            print("3. Wait a few minutes and try again")