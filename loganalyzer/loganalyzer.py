import gradio as gr
import requests
import json
from datetime import datetime
import os
from scapy.all import rdpcap
import tempfile
import re
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from scapy.all import PcapReader

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

class LogAnalyzer:
    def __init__(self):
        self.common_patterns = {
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'timestamp': r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*',
            'mac_address': r'(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})',
            'port': r'\b(?:port |:)\d{1,5}\b',
            'error_codes': r'\b(?:4\d{2}|5\d{2}|error|failure|failed)\b'
        }
        
    def extract_patterns(self, text):
        results = {}
        for pattern_name, pattern in self.common_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            results[pattern_name] = [match.group() for match in matches]
        return results

    def generate_statistics(self, text, extracted_patterns):
        stats = {
            'total_lines': len(text.splitlines()),
            'unique_ips': len(set(extracted_patterns['ip_address'])),
            'unique_emails': len(set(extracted_patterns['email'])),
            'error_count': len(extracted_patterns['error_codes']),
            'ip_frequency': Counter(extracted_patterns['ip_address']).most_common(10)
        }
        return stats

def create_visualizations(stats, extracted_patterns):
    # Create temporary directory for visualizations
    temp_dir = tempfile.mkdtemp()
    viz_files = []

    # IP frequency visualization
    if extracted_patterns['ip_address']:
        plt.figure(figsize=(10, 6))
        ip_freq = pd.DataFrame(stats['ip_frequency'], columns=['IP', 'Count'])
        sns.barplot(data=ip_freq, x='Count', y='IP')
        plt.title('Top IP Addresses by Frequency')
        ip_viz_path = os.path.join(temp_dir, 'ip_frequency.png')
        plt.savefig(ip_viz_path)
        plt.close()
        viz_files.append(ip_viz_path)

    return viz_files

def parse_pcap(pcap_file, max_packets=10000):
    """
    Parse PCAP file with optimized performance
    max_packets: Maximum number of packets to process (default 10000)
    """
    try:
        parsed_data = []
        # Use PcapReader instead of rdpcap for memory efficiency
        with PcapReader(pcap_file) as pcap_reader:
            for i, packet in enumerate(pcap_reader):
                if i >= max_packets:
                    break
                    
                packet_info = {}
                
                # Layer 3 info only (focus on essential data)
                if packet.haslayer('IP'):
                    packet_info['src_ip'] = packet['IP'].src
                    packet_info['dst_ip'] = packet['IP'].dst
                    packet_info['protocol'] = str(packet['IP'].proto)
                
                    # Layer 4 info (TCP/UDP)
                    if packet.haslayer('TCP'):
                        packet_info['src_port'] = str(packet['TCP'].sport)
                        packet_info['dst_port'] = str(packet['TCP'].dport)
                        packet_info['tcp_flags'] = str(packet['TCP'].flags)
                    elif packet.haslayer('UDP'):
                        packet_info['src_port'] = str(packet['UDP'].sport)
                        packet_info['dst_port'] = str(packet['UDP'].dport)
                    
                    parsed_data.append(packet_info)
                
                # Give feedback every 1000 packets
                if i % 1000 == 0:
                    print(f"Processed {i} packets...")
        
        print(f"Finished processing {len(parsed_data)} packets")
        return parsed_data
        
    except Exception as e:
        raise Exception(f"Error parsing PCAP file: {str(e)}")

def create_analysis_prompt(file_content, analysis_type, specific_focus=None):
    base_prompts = {
        'security_audit': """Perform a comprehensive security audit of the provided logs. Focus on:
        1. Identifying potential security breaches
        2. Unusual access patterns
        3. Policy violations
        4. Suspicious IP addresses or domains
        5. Known attack signatures""",
        
        'threat_hunting': """Analyze the logs for potential threats. Consider:
        1. Advanced Persistent Threat (APT) indicators
        2. Command and control (C2) traffic patterns
        3. Data exfiltration attempts
        4. Lateral movement indicators
        5. Privilege escalation attempts""",
        
        'compliance_check': """Review logs for compliance-related issues. Check for:
        1. Access control violations
        2. Data privacy concerns
        3. Authentication failures
        4. Regulatory requirement violations
        5. Sensitive data exposure""",
        
        'performance_analysis': """Analyze system performance and reliability. Look for:
        1. Resource utilization patterns
        2. System bottlenecks
        3. Error rates and patterns
        4. Service disruptions
        5. Performance degradation indicators"""
    }
    
    prompt = f"""As an expert log analyzer, please analyze the following data with this specific focus:
    {base_prompts[analysis_type]}
    
    Additional Focus Areas: {specific_focus if specific_focus else 'None specified'}
    
    Data for Analysis:
    {file_content}
    
    Please provide:
    1. Executive Summary
    2. Key Findings
    3. Detailed Analysis
    4. Recommendations
    5. Suggested Next Steps"""
    
    return prompt

def analyze_file(file, selected_model, analysis_type, specific_focus, advanced_options):
    if not file:
        return "No file provided for analysis", None, []
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis_output_{timestamp}.txt"
    analyzer = LogAnalyzer()
    
    try:
        # Process file based on type
        if file.name.endswith('.pcap'):
            print("Starting PCAP analysis...")
            parsed_data = parse_pcap(file.name, max_packets=10000)  # Limit to 10000 packets
            # Convert to JSON more efficiently
            file_content = json.dumps([{k: str(v) for k, v in packet.items()} for packet in parsed_data], indent=2)
        else:
            with open(file.name, 'r') as f:
                file_content = f.read()
        
        print("Extracting patterns...")
        extracted_patterns = analyzer.extract_patterns(file_content)
        stats = analyzer.generate_statistics(file_content, extracted_patterns)
        
        print("Creating analysis prompt...")
        analysis_prompt = create_analysis_prompt(file_content, analysis_type, specific_focus)
        
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
        
        print("Generating visualizations...")
        viz_files = create_visualizations(stats, extracted_patterns)
        
        # Save report
        with open(output_file, 'w') as f:
            f.write(f"Analysis Report - {timestamp}\n")
            # ... rest of the report writing code ...
            
        print("Analysis complete!")
        return full_response, output_file, viz_files
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        with open(output_file, 'w') as f:
            f.write(f"Error: {error_msg}")
        return error_msg, output_file, []

def create_interface():
    with gr.Blocks(title="Enhanced Cyber Threat Analysis Interface") as interface:
        gr.Markdown("# Advanced Cyber Threat Analysis Interface")
        
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
                
                specific_focus = gr.Textbox(
                    label="Specific Focus Areas",
                    placeholder="Enter specific areas to focus on (e.g., 'SSH brute force attempts, SQL injection')",
                    lines=2
                )
                
                with gr.Accordion("Advanced Options", open=False):
                    advanced_options = gr.CheckboxGroup(
                        choices=[
                            "Include raw pattern matches",
                            "Generate visualizations",
                            "Perform entropy analysis",
                            "Extract potential IOCs",
                            "Include MITRE ATT&CK mapping"
                        ],
                        label="Advanced Analysis Options"
                    )
                
                analyze_button = gr.Button("Analyze")
                
            with gr.Column():
                output_text = gr.Textbox(label="Analysis Results", lines=20)
                file_output = gr.File(label="Download Analysis Report")
                gallery = gr.Gallery(label="Visualizations")
                
        analyze_button.click(
            fn=analyze_file,
            inputs=[file_input, model_dropdown, analysis_type, specific_focus, advanced_options],
            outputs=[output_text, file_output, gallery]
        )
        
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)  # Changed to share=True for public access