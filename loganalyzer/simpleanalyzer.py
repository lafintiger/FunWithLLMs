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

def parse_pcap(pcap_file):
    packets = rdpcap(pcap_file)
    parsed_data = []
    
    for packet in packets:
        packet_info = {}
        
        # Layer 2 info
        if packet.haslayer('Ether'):
            packet_info['src_mac'] = packet['Ether'].src
            packet_info['dst_mac'] = packet['Ether'].dst
        
        # Layer 3 info
        if packet.haslayer('IP'):
            packet_info['src_ip'] = packet['IP'].src
            packet_info['dst_ip'] = packet['IP'].dst
            packet_info['protocol'] = packet['IP'].proto
        
        # Layer 4 info
        if packet.haslayer('TCP'):
            packet_info['src_port'] = packet['TCP'].sport
            packet_info['dst_port'] = packet['TCP'].dport
            packet_info['tcp_flags'] = packet['TCP'].flags
        elif packet.haslayer('UDP'):
            packet_info['src_port'] = packet['UDP'].sport
            packet_info['dst_port'] = packet['UDP'].dport
        
        parsed_data.append(packet_info)
    
    return parsed_data

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis_output_{timestamp}.txt"
    analyzer = LogAnalyzer()
    
    # Process file based on type
    if file.name.endswith('.pcap'):
        parsed_data = parse_pcap(file.name)
        file_content = json.dumps(parsed_data, indent=2)
    else:
        with open(file.name, 'r') as f:
            file_content = f.read()
    
    # Extract patterns and generate statistics
    extracted_patterns = analyzer.extract_patterns(file_content)
    stats = analyzer.generate_statistics(file_content, extracted_patterns)
    
    # Create analysis prompt
    analysis_prompt = create_analysis_prompt(file_content, analysis_type, specific_focus)
    
    # Call Ollama API with streaming response
    try:
        response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": selected_model,
                "system": "You are an expert cyber security analyst specializing in log analysis and threat detection.",
                "prompt": analysis_prompt
            },
            stream=True
        )
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line.decode('utf-8'))
                if 'response' in json_response:
                    full_response += json_response['response']
        
        # Generate visualizations
        viz_files = create_visualizations(stats, extracted_patterns)
        
        # Save comprehensive report
        with open(output_file, 'w') as f:
            f.write(f"Analysis Report - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Analysis Configuration:\n")
            f.write(f"- Model: {selected_model}\n")
            f.write(f"- Analysis Type: {analysis_type}\n")
            f.write(f"- Specific Focus: {specific_focus}\n")
            f.write(f"- Advanced Options: {advanced_options}\n\n")
            
            f.write("Statistical Analysis:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Lines Analyzed: {stats['total_lines']}\n")
            f.write(f"Unique IP Addresses: {stats['unique_ips']}\n")
            f.write(f"Unique Email Addresses: {stats['unique_emails']}\n")
            f.write(f"Error Count: {stats['error_count']}\n\n")
            
            f.write("Top IP Addresses:\n")
            for ip, count in stats['ip_frequency']:
                f.write(f"- {ip}: {count} occurrences\n")
            f.write("\n")
            
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
    interface.launch(share=False)