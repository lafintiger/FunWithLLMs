import gradio as gr
import socket
import requests
import nmap
import ipaddress
import subprocess
import whois
import warnings
import logging
from datetime import datetime

# The existing HTML_CONTENT string remains unchanged
# Only modify the HTML_CONTENT - rest of your code stays the same

# Replace just the HTML_CONTENT in your code

HTML_CONTENT = """
<div id="scanner-app">
    <h2>Client Network Scanner</h2>
    <p>This scanner will run on your local network, not the server's network.</p>
    
    <button id="scanButtonClient" style="background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 10px 0;">
        Start Network Scan
    </button>
    
    <div id="statusClient" style="margin: 10px 0; font-style: italic; color: #666;"></div>
    <div id="localIPClient" style="border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 4px;"></div>
    <div id="resultsClient" style="border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 4px;"></div>
</div>

<script>
    (function() {
        // Wait for DOM to be fully loaded
        document.addEventListener('DOMContentLoaded', function() {
            setupScanner();
        });

        // Also try immediate setup in case DOMContentLoaded already fired
        setupScanner();

        function setupScanner() {
            const scanButton = document.getElementById('scanButtonClient');
            if (!scanButton) {
                console.log('Scanner button not found, waiting...');
                return;
            }

            console.log('Setting up network scanner...');
            scanButton.addEventListener('click', startScan);
        }

        async function getLocalIP() {
            try {
                const pc = new RTCPeerConnection({ iceServers: [] });
                pc.createDataChannel('');
                await pc.createOffer().then(offer => pc.setLocalDescription(offer));
                
                return new Promise((resolve) => {
                    setTimeout(() => {
                        const sdp = pc.localDescription.sdp;
                        const matches = sdp.match(/\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/);
                        pc.close();
                        resolve(matches ? matches[0] : null);
                    }, 500);
                });
            } catch (e) {
                console.error('Error getting local IP:', e);
                return null;
            }
        }

        async function pingIP(ip) {
            return new Promise((resolve) => {
                const timeout = 1000;
                const start = Date.now();
                const img = new Image();

                img.onload = () => resolve({ ip, status: 'active', time: Date.now() - start });
                img.onerror = () => resolve({ ip, status: 'inactive', time: Date.now() - start });
                img.src = `http://${ip}:1/favicon.ico?t=${Date.now()}`;

                setTimeout(() => {
                    img.src = '';
                    resolve({ ip, status: 'timeout', time: timeout });
                }, timeout);
            });
        }

        function updateStatus(message) {
            const statusElement = document.getElementById('statusClient');
            if (statusElement) {
                statusElement.textContent = message;
            }
        }

        function displayResults(localIP, results) {
            const localIPElement = document.getElementById('localIPClient');
            const resultsElement = document.getElementById('resultsClient');

            if (localIPElement) {
                localIPElement.innerHTML = `<strong>Your Local IP:</strong> ${localIP}`;
            }

            if (resultsElement) {
                if (results.length === 0) {
                    resultsElement.innerHTML = '<p>No active devices found.</p>';
                } else {
                    const resultHTML = results
                        .map(result => `<div>Active device found: ${result.ip} (Response time: ${result.time}ms)</div>`)
                        .join('');
                    resultsElement.innerHTML = `
                        <strong>Active Devices Found:</strong>
                        <div style="margin-top: 10px">${resultHTML}</div>
                    `;
                }
            }
        }

        async function scanNetwork(baseIP) {
            const results = [];
            const scanPromises = [];
            const subnet = baseIP.split('.').slice(0, 3).join('.');

            updateStatus(`Scanning network ${subnet}.0/24...`);

            const batchSize = 10;
            for (let i = 1; i <= 254; i++) {
                const ip = `${subnet}.${i}`;
                scanPromises.push(pingIP(ip));

                if (scanPromises.length === batchSize || i === 254) {
                    const batchResults = await Promise.all(scanPromises);
                    results.push(...batchResults);
                    updateStatus(`Scanned ${results.length} addresses...`);
                    scanPromises.length = 0;
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }

            return results.filter(r => r.status === 'active');
        }

        async function startScan() {
            const scanButton = document.getElementById('scanButtonClient');
            if (scanButton) {
                scanButton.disabled = true;
            }
            
            updateStatus('Getting local IP...');
            
            try {
                const localIP = await getLocalIP();
                if (!localIP) {
                    throw new Error('Could not determine local IP');
                }

                updateStatus('Starting network scan...');
                const results = await scanNetwork(localIP);
                updateStatus('Scan complete!');
                displayResults(localIP, results);
            } catch (error) {
                console.error('Scan error:', error);
                updateStatus(`Error: ${error.message}`);
            } finally {
                if (scanButton) {
                    scanButton.disabled = false;
                }
            }
        }
    })();
</script>
"""

# Rest of your Python code stays exactly the same...

# Rest of your Python code stays exactly the same...

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
        
        if subprocess.call("traceroute", shell=True) == 0:
            cmd = ['traceroute', host]
        else:
            cmd = ['tracert', host]
        
        result = subprocess.check_output(cmd, universal_newlines=True)
        return result
    except Exception as e:
        return f"Error performing traceroute: {str(e)}"

def create_scanner_interface():
    """Create a hybrid interface with both server and client-side scanning"""
    with gr.Blocks(title="Network Scanner") as iface:
        gr.Markdown("# Network Administrator Utility")
        
        with gr.Tab("Server-Side Scan"):
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
            
            with gr.Row():
                with gr.Column():
                    dig_input = gr.Textbox(label="Enter domain for DNS lookup")
                    dig_btn = gr.Button("Perform DNS Lookup")
                    dig_output = gr.Textbox(label="DNS Lookup Results", lines=10)
                
                with gr.Column():
                    whois_input = gr.Textbox(label="Enter domain for WHOIS lookup")
                    whois_btn = gr.Button("Perform WHOIS Lookup")
                    whois_output = gr.Textbox(label="WHOIS Results", lines=10)
            
            with gr.Row():
                traceroute_input = gr.Textbox(label="Enter host for traceroute")
                traceroute_btn = gr.Button("Perform Traceroute")
                traceroute_output = gr.Textbox(label="Traceroute Results", lines=15)
            
            # Connect the server-side buttons to functions
            local_ip_btn.click(fn=get_local_ip, outputs=local_ip_output)
            public_ip_btn.click(fn=get_public_ip, outputs=public_ip_output)
            scan_btn.click(fn=scan_network, outputs=scan_output)
            dig_btn.click(fn=perform_dig, inputs=dig_input, outputs=dig_output)
            whois_btn.click(fn=perform_whois, inputs=whois_input, outputs=whois_output)
            traceroute_btn.click(fn=perform_traceroute, inputs=traceroute_input, outputs=traceroute_output)
        
        with gr.Tab("Client-Side Scan"):
            gr.HTML(HTML_CONTENT)
        
    return iface

if __name__ == "__main__":
    def try_launch(start_port=8760, max_attempts=10):
        """Try to launch the interface on an available port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                print(f"Attempting to start server on port {port}...")
                iface = create_scanner_interface()
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
        if not try_launch():
            print("\nFailed to find an available port. Please try the following:")
            print("1. Check for other running instances of this tool")
            print("2. Use a different starting port by modifying the start_port parameter")
            print("3. Wait a few minutes and try again")