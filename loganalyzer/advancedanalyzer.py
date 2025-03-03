import gradio as gr
import requests
import json
from datetime import datetime
import os
from scapy.all import PcapReader
import tempfile
import re
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
import numpy as np
from pathlib import Path
import networkx as nx
from io import BytesIO

def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = [model['name'] for model in response.json()['models']]
            return models if models else ["No models found"]
        return ["Error: Could not fetch models"]
    except requests.exceptions.ConnectionError:
        return ["Error: Could not connect to Ollama"]
    except Exception as e:
        return [f"Error: {str(e)}"]

class PacketFilter:
    """Handles packet filtering operations"""
    
    @staticmethod
    def filter_by_protocol(packets: List[Dict], protocol: str) -> List[Dict]:
        if not protocol:
            return packets
        return [p for p in packets if str(p.get('protocol')).lower() == protocol.lower()]
    
    @staticmethod
    def filter_by_port(packets: List[Dict], port: int) -> List[Dict]:
        if not port:
            return packets
        return [p for p in packets if str(p.get('src_port')) == str(port) or str(p.get('dst_port')) == str(port)]
    
    @staticmethod
    def filter_by_ip(packets: List[Dict], ip: str) -> List[Dict]:
        if not ip:
            return packets
        return [p for p in packets if p.get('src_ip') == ip or p.get('dst_ip') == ip]

class PacketAnalyzer:
    """Handles advanced packet analysis"""
    
    @staticmethod
    def get_protocol_distribution(packets: List[Dict]) -> Dict[str, int]:
        protocols = [p.get('protocol') for p in packets if 'protocol' in p]
        return Counter(protocols)
    
    @staticmethod
    def get_port_distribution(packets: List[Dict]) -> List[tuple]:
        ports = []
        for p in packets:
            if 'src_port' in p:
                ports.append(f"Port {p['src_port']}")
            if 'dst_port' in p:
                ports.append(f"Port {p['dst_port']}")
        return Counter(ports).most_common(10)
    
    @staticmethod
    def get_ip_connections(packets: List[Dict]) -> List[tuple]:
        connections = []
        for p in packets:
            if 'src_ip' in p and 'dst_ip' in p:
                connections.append((p['src_ip'], p['dst_ip']))
        return Counter(connections).most_common(10)
    
    @staticmethod
    def calculate_traffic_volume(packets: List[Dict]) -> Dict[str, int]:
        volumes = {}
        for p in packets:
            src = p.get('src_ip')
            if src:
                volumes[src] = volumes.get(src, 0) + 1
        return dict(sorted(volumes.items(), key=lambda x: x[1], reverse=True)[:10])

class VisualAnalytics:
    """Handles creation of various visualizations"""
    
    @staticmethod
    def create_protocol_pie_chart(data: Dict[str, int]) -> str:
        plt.figure(figsize=(10, 6))
        plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        plt.title('Protocol Distribution')
        
        temp_file = os.path.join(tempfile.mkdtemp(), 'protocol_dist.png')
        plt.savefig(temp_file, bbox_inches='tight', dpi=300)
        plt.close()
        return temp_file
    
    @staticmethod
    def create_traffic_flow_graph(connections: List[tuple]) -> str:
        G = nx.DiGraph()
        
        for connection, weight in connections:
            src, dst = connection
            G.add_edge(src, dst, weight=weight)
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, arrowsize=20, font_size=8,
                width=[G[u][v]['weight']/5 for u,v in G.edges()])
        
        temp_file = os.path.join(tempfile.mkdtemp(), 'traffic_flow.png')
        plt.savefig(temp_file, bbox_inches='tight', dpi=300)
        plt.close()
        return temp_file
    
    @staticmethod
    def create_port_distribution_chart(data: List[tuple]) -> str:
        plt.figure(figsize=(12, 6))
        ports, counts = zip(*data)
        sns.barplot(x=list(counts), y=list(ports))
        plt.title('Top Ports by Usage')
        
        temp_file = os.path.join(tempfile.mkdtemp(), 'port_dist.png')
        plt.savefig(temp_file, bbox_inches='tight', dpi=300)
        plt.close()
        return temp_file

def parse_pcap(pcap_file: str, max_packets: int = 10000, filters: Dict = None) -> List[Dict]:
    """
    Enhanced packet capture parser supporting both pcap and pcapng formats
    """
    try:
        parsed_data = []
        packet_count = 0
        
        # Validate file extension
        file_extension = pcap_file.lower()
        if not (file_extension.endswith('.pcap') or file_extension.endswith('.pcapng')):
            raise ValueError("Unsupported file format. Please use .pcap or .pcapng files")

        print(f"Processing packet capture file: {pcap_file}")
        with PcapReader(pcap_file) as pcap_reader:
            for packet in pcap_reader:
                if packet_count >= max_packets:
                    break
                    
                packet_info = {}
                
                # Layer 3 info
                if packet.haslayer('IP'):
                    packet_info['src_ip'] = packet['IP'].src
                    packet_info['dst_ip'] = packet['IP'].dst
                    packet_info['protocol'] = str(packet['IP'].proto)
                    packet_info['length'] = len(packet)
                    
                    # Layer 4 info
                    if packet.haslayer('TCP'):
                        packet_info['src_port'] = str(packet['TCP'].sport)
                        packet_info['dst_port'] = str(packet['TCP'].dport)
                        packet_info['tcp_flags'] = str(packet['TCP'].flags)
                    elif packet.haslayer('UDP'):
                        packet_info['src_port'] = str(packet['UDP'].sport)
                        packet_info['dst_port'] = str(packet['UDP'].dport)
                    
                    if filters:
                        if 'protocol' in filters and filters['protocol'] and \
                           packet_info.get('protocol') != filters['protocol']:
                            continue
                        if 'port' in filters and filters['port'] and \
                           str(filters['port']) not in [packet_info.get('src_port'), 
                                                      packet_info.get('dst_port')]:
                            continue
                        if 'ip' in filters and filters['ip'] and \
                           filters['ip'] not in [packet_info.get('src_ip'), 
                                               packet_info.get('dst_ip')]:
                            continue
                    
                    parsed_data.append(packet_info)
                    packet_count += 1
                
                if packet_count % 1000 == 0:
                    print(f"Processed {packet_count} packets...")
        
        print(f"Finished processing {len(parsed_data)} packets")
        return parsed_data
        
    except Exception as e:
        raise Exception(f"Error parsing packet capture file: {str(e)}")

def create_analysis_prompt(file_content: str, analysis_type: str, specific_focus: str) -> str:
    """Create a prompt for the LLM analysis"""
    base_prompts = {
        'security_audit': """Perform a comprehensive security audit of this network traffic:
        1. Identify potential security breaches or suspicious patterns
        2. Analyze access patterns and potential policy violations
        3. Evaluate protocol usage and potential misuse
        4. Check for indicators of compromise
        5. Review unusual port usage or connections""",
        
        'threat_hunting': """Analyze this traffic for potential threats:
        1. Look for signs of Advanced Persistent Threats (APTs)
        2. Identify potential Command & Control (C2) traffic
        3. Detect possible data exfiltration
        4. Analyze lateral movement indicators
        5. Check for privilege escalation attempts""",
        
        'compliance_check': """Review this traffic for compliance issues:
        1. Verify proper protocol usage
        2. Check for unauthorized services
        3. Identify potential data privacy issues
        4. Analyze authentication patterns
        5. Review access control implementation""",
        
        'performance_analysis': """Analyze network performance metrics:
        1. Evaluate protocol distribution efficiency
        2. Identify potential bottlenecks
        3. Review connection patterns
        4. Assess traffic volume distribution
        5. Check for network optimization opportunities"""
    }
    
    prompt = f"""As an expert network security analyst, please analyze the following network traffic data.

Focus Area: {analysis_type}
{base_prompts[analysis_type]}

Additional Focus Points: {specific_focus if specific_focus else 'None specified'}

Traffic Data and Statistics:
{file_content}

Please provide:
1. Executive Summary
2. Key Findings and Observations
3. Potential Security Implications
4. Detailed Analysis of Patterns
5. Specific Recommendations
6. Suggested Next Steps

Include specific details about:
- Unusual patterns or anomalies
- Security implications of the protocol distribution
- Notable IP addresses or connections
- Port usage analysis
- Potential improvements or mitigations
"""
    return prompt

def analyze_file(file, selected_model, analysis_type, specific_focus, filters):
    """
    Analyze a single file with the given parameters
    """
    if not file:
        return "No file provided for analysis", None, []
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis_output_{timestamp}.txt"
    
    try:
        # Process file based on type
        file_extension = file.name.lower()
        if file_extension.endswith(('.pcap', '.pcapng')):
            print(f"Starting packet capture analysis of {file.name}...")
            parsed_data = parse_pcap(
                file.name, 
                max_packets=filters.get('max_packets', 10000),
                filters={k: v for k, v in filters.items() if k != 'max_packets' and v}
            )
            
            # Perform analysis
            analyzer = PacketAnalyzer()
            protocol_dist = analyzer.get_protocol_distribution(parsed_data)
            port_dist = analyzer.get_port_distribution(parsed_data)
            connections = analyzer.get_ip_connections(parsed_data)
            traffic_volume = analyzer.calculate_traffic_volume(parsed_data)
            
            # Create visualizations
            viz = VisualAnalytics()
            viz_files = [
                viz.create_protocol_pie_chart(protocol_dist),
                viz.create_port_distribution_chart(port_dist),
                viz.create_traffic_flow_graph(connections)
            ]
            
            # Convert to JSON-serializable format
            for_json = {
                'Summary': {
                    'total_packets': len(parsed_data),
                    'unique_protocols': len(protocol_dist),
                    'total_connections': sum(count for _, count in connections)
                },
                'protocol_distribution': protocol_dist,
                'port_distribution': dict(port_dist),
                'top_connections': [{'src': src, 'dst': dst, 'count': count} 
                                  for (src, dst), count in connections],
                'traffic_volume': traffic_volume,
                'sample_packets': parsed_data[:50]
            }
            
            file_content = json.dumps(for_json, indent=2)
            
        else:
            with open(file.name, 'r') as f:
                file_content = f.read()
                viz_files = []
        
        # Call Ollama API
        print("Calling Ollama API...")
        response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": selected_model,
                "system": """You are an expert cyber security analyst specializing in network traffic analysis, 
                           threat detection, and security assessment. Provide detailed, actionable insights.""",
                "prompt": create_analysis_prompt(file_content, analysis_type, specific_focus)
            },
            stream=True
        )
        
        print("Processing Ollama response...")
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line.decode('utf-8'))
                if 'response' in json_response:
                    full_response += json_response['response']
        
        # Save report
        with open(output_file, 'w') as f:
            f.write(f"Network Traffic Analysis Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Analysis Configuration:\n")
            f.write(f"- File: {file.name}\n")
            f.write(f"- Model: {selected_model}\n")
            f.write(f"- Analysis Type: {analysis_type}\n")
            f.write(f"- Specific Focus: {specific_focus}\n")
            f.write(f"- Filters Applied: {filters}\n\n")
            
            if file_extension.endswith(('.pcap', '.pcapng')):
                f.write("Traffic Statistics:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total Packets Analyzed: {len(parsed_data)}\n")
                f.write(f"Protocol Distribution: {protocol_dist}\n")
                f.write(f"Top Ports: {dict(port_dist)}\n")
                f.write(f"Top Connections: {[f'{src}->{dst}: {count}' for (src, dst), count in connections]}\n\n")
            
            f.write("LLM Analysis Results:\n")
            f.write("-" * 30 + "\n")
            f.write(full_response)
            
        return full_response, output_file, viz_files
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        with open(output_file, 'w') as f:
            f.write(f"Error: {error_msg}")
        return error_msg, output_file, []
    
def create_interface():
    with gr.Blocks(title="Enhanced Cyber Threat Analysis Interface") as interface:
        gr.Markdown("""# Advanced Cyber Threat Analysis Interface
        
        Supports PCAP, PCAPNG, and text log files.""")
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="Upload File for Analysis", 
                    file_types=[".pcap", ".pcapng", ".txt", ".log"]
                )
                model_dropdown = gr.Dropdown(
                    choices=get_available_models(),
                    label="Select Analysis Model",
                    value=get_available_models()[0] if get_available_models() else None
                )
                
                analysis_type = gr.Radio(
                    choices=["security_audit", "threat_hunting", "compliance_check", "performance_analysis"],
                    label="Analysis Type",
                    value="security_audit"
                )
                
                with gr.Accordion("Filters", open=False):
                    protocol_filter = gr.Textbox(label="Protocol Filter (e.g., TCP, UDP)")
                    port_filter = gr.Number(label="Port Filter")
                    ip_filter = gr.Textbox(label="IP Filter")
                    max_packets = gr.Slider(
                        minimum=1000,
                        maximum=100000,
                        value=10000,
                        step=1000,
                        label="Maximum Packets to Analyze"
                    )
                
                specific_focus = gr.Textbox(
                    label="Specific Focus Areas",
                    placeholder="Enter specific areas to focus on (e.g., 'SSH brute force attempts, SQL injection')",
                    lines=2
                )
                
                analyze_button = gr.Button("Analyze")
                
            with gr.Column():
                output_text = gr.Textbox(label="Analysis Results", lines=20)
                file_output = gr.File(label="Download Analysis Report")
                gallery = gr.Gallery(label="Visualizations")
                
            # Connect button click to analysis function
            analyze_button.click(
                fn=lambda f, m, t, p, pf, pof, ipf, mp, sf: analyze_file(
                    f, m, t, sf, 
                    {'protocol': pf, 'port': pof, 'ip': ipf, 'max_packets': mp}
                ),
                inputs=[
                    file_input, model_dropdown, analysis_type, specific_focus,
                    protocol_filter, port_filter, ip_filter, max_packets,
                    specific_focus
                ],
                outputs=[output_text, file_output, gallery]
            )
    
        return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        share=True,  # Enable public URL
        show_error=True  # Show detailed error messages
    )