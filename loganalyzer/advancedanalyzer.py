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
        return [p for p in packets if str(p.get('protocol')).lower() == protocol.lower()]
    
    @staticmethod
    def filter_by_port(packets: List[Dict], port: int) -> List[Dict]:
        return [p for p in packets if str(p.get('src_port')) == str(port) or str(p.get('dst_port')) == str(port)]
    
    @staticmethod
    def filter_by_ip(packets: List[Dict], ip: str) -> List[Dict]:
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
        plt.savefig(temp_file)
        plt.close()
        return temp_file
    
    @staticmethod
    def create_traffic_flow_graph(connections: List[tuple]) -> str:
        G = nx.DiGraph()
        
        # Convert connections from Counter output to edge list with weights
        for connection, weight in connections:
            src, dst = connection  # Unpack the connection tuple
            G.add_edge(src, dst, weight=weight)
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        
        # Draw the graph
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=1500, arrowsize=20, font_size=8)
        
        temp_file = os.path.join(tempfile.mkdtemp(), 'traffic_flow.png')
        plt.savefig(temp_file)
        plt.close()
        return temp_file
    
    @staticmethod
    def create_port_distribution_chart(data: List[tuple]) -> str:
        plt.figure(figsize=(12, 6))
        ports, counts = zip(*data)
        sns.barplot(x=list(counts), y=list(ports))
        plt.title('Top Ports by Usage')
        
        temp_file = os.path.join(tempfile.mkdtemp(), 'port_dist.png')
        plt.savefig(temp_file)
        plt.close()
        return temp_file
    
def parse_pcap(pcap_file: str, max_packets: int = 10000, filters: Dict = None) -> List[Dict]:
    """
    Enhanced PCAP parser with filtering capabilities
    """
    try:
        parsed_data = []
        packet_count = 0
        
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
                    
                    # Layer 4 info
                    if packet.haslayer('TCP'):
                        packet_info['src_port'] = str(packet['TCP'].sport)
                        packet_info['dst_port'] = str(packet['TCP'].dport)
                        packet_info['tcp_flags'] = str(packet['TCP'].flags)
                    elif packet.haslayer('UDP'):
                        packet_info['src_port'] = str(packet['UDP'].sport)
                        packet_info['dst_port'] = str(packet['UDP'].dport)
                    
                    # Apply filters if specified
                    if filters:
                        if 'protocol' in filters and packet_info.get('protocol') != filters['protocol']:
                            continue
                        if 'port' in filters and str(filters['port']) not in [
                            packet_info.get('src_port'), packet_info.get('dst_port')
                        ]:
                            continue
                        if 'ip' in filters and filters['ip'] not in [
                            packet_info.get('src_ip'), packet_info.get('dst_ip')
                        ]:
                            continue
                    
                    parsed_data.append(packet_info)
                    packet_count += 1
                
                if packet_count % 1000 == 0:
                    print(f"Processed {packet_count} packets...")
        
        print(f"Finished processing {len(parsed_data)} packets")
        return parsed_data
        
    except Exception as e:
        raise Exception(f"Error parsing PCAP file: {str(e)}")
        
    except Exception as e:
        raise Exception(f"Error parsing PCAP file: {str(e)}")

def create_analysis_prompt(file_content: str, analysis_type: str, specific_focus: str) -> str:
    """Create a prompt for the LLM analysis"""
    prompt = f"""Analyze the following network traffic data with a focus on {analysis_type}.
    
Additional focus areas: {specific_focus}

Data:
{file_content}

Please provide:
1. Overview of the traffic patterns
2. Potential security concerns
3. Recommendations for improvement
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
        if file.name.endswith('.pcap'):
            print("Starting PCAP analysis...")
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
                'parsed_data': parsed_data[:100],  # First 100 packets for LLM
                'protocol_distribution': protocol_dist,
                'port_distribution': dict(port_dist),
                'top_connections': [{'src': src, 'dst': dst, 'count': count} 
                                  for (src, dst), count in connections],
                'traffic_volume': traffic_volume
            }
            
            file_content = json.dumps(for_json, indent=2)
            
        else:
            with open(file.name, 'r') as f:
                file_content = f.read()
                viz_files = []
        
        # Create analysis prompt
        analysis_prompt = create_analysis_prompt(file_content, analysis_type, specific_focus)
        
        # Call Ollama API
        print("Calling Ollama API...")
        response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": selected_model,
                "system": "You are an expert cyber security analyst specializing in log analysis and threat detection.",
                "prompt": analysis_prompt
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
            f.write(f"Analysis Report - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Analysis Configuration:\n")
            f.write(f"- Model: {selected_model}\n")
            f.write(f"- Analysis Type: {analysis_type}\n")
            f.write(f"- Specific Focus: {specific_focus}\n")
            f.write(f"- Filters Applied: {filters}\n\n")
            
            if file.name.endswith('.pcap'):
                f.write("PCAP Analysis Statistics:\n")
                f.write("-" * 30 + "\n")
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
        gr.Markdown("# Advanced Cyber Threat Analysis Interface")
        
        with gr.Tabs():
            with gr.TabItem("Single File Analysis"):
                with gr.Row():
                    with gr.Column():
                        file_input = gr.File(label="Upload PCAP or Text File")
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
                            placeholder="Enter specific areas to focus on",
                            lines=2
                        )
                        
                        analyze_button = gr.Button("Analyze")
                        
                    with gr.Column():
                        output_text = gr.Textbox(label="Analysis Results", lines=20)
                        file_output = gr.File(label="Download Analysis Report")
                        gallery = gr.Gallery(label="Visualizations")
            
        # Single file analysis event
        analyze_button.click(
            fn=lambda f, m, t, p, pf, pof, ipf, mp, sf: analyze_file(
                f, m, t, sf, 
                {'protocol': pf,
                 
                 'port': pof, 'ip': ipf, 'max_packets': mp}
            ),
            inputs=[
                file_input, model_dropdown, analysis_type, specific_focus,
                protocol_filter, port_filter, ip_filter, max_packets,
                specific_focus
            ],
            outputs=[output_text, file_output, gallery]
        )
    
    return interface

def create_analysis_prompt(file_content: str, analysis_type: str, specific_focus: str) -> str:
    """Create a prompt for the LLM analysis"""
    prompt = f"""Analyze the following network traffic data with a focus on {analysis_type}.
    
Additional focus areas: {specific_focus}

Data:
{file_content}

Please provide:
1. Overview of the traffic patterns
2. Potential security concerns
3. Recommendations for improvement
"""
    return prompt

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)