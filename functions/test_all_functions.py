#!/usr/bin/env python3
"""
OpenFaaS Function Test Script
Dynamically discovers and tests all functions in the functions directory
"""

import os
import sys
import time
import subprocess
import signal
import json
import re
from pathlib import Path
from typing import Optional, Tuple
import requests
import yaml

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

# Configuration
SCRIPT_DIR = Path(os.getcwd()).resolve()
PORT = 8080
WAIT_TIMEOUT = 60*3
HEALTH_CHECK_INTERVAL = 2

# Track results
passed = 0
failed = 0
skipped = 0


# ============================================================================
# Helper Functions
# ============================================================================

def print_step(message: str):
    print(f"\n{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    print(f"{Colors.CYAN}[STEP]{Colors.NC} {message}")
    print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")


def print_success(message: str):
    print(f"{Colors.GREEN}[✓ SUCCESS]{Colors.NC} {message}")


def print_error(message: str):
    print(f"{Colors.RED}[✗ ERROR]{Colors.NC} {message}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}[⚠ WARNING]{Colors.NC} {message}")


def print_info(message: str):
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {message}")


def get_function_name(yaml_file: Path) -> Optional[str]:
    """Extract function name from YAML file."""
    try:
        with open(yaml_file, 'r') as f:
            content = yaml.safe_load(f)
        if content and 'functions' in content:
            # Return the first function name
            return list(content['functions'].keys())[0]
    except Exception as e:
        print_warning(f"Error reading YAML file {yaml_file}: {e}")
    return None


def get_test_payload(func_name: str) -> dict:
    """Get test payload for a specific function."""
    payloads = {
        # AI/ML Functions
        "text-summarizer": {
            "text": "Artificial intelligence is transforming the technology landscape. Machine learning algorithms can now process vast amounts of data. Deep learning has revolutionized computer vision and natural language processing. Companies are investing heavily in AI research and development. The future of AI looks promising with many exciting applications ahead.",
            "num_sentences": 2,
            "method": "tfidf"
        },
        "anomaly-detector": {
            "data": [[1.2, 3.4], [2.1, 3.5], [1.8, 3.3], [2.0, 3.6], [100, 200]],
            "train": True,
            "contamination": 0.1
        },
        "sentiment-analyzer": {
            "text": "This product is amazing! I love it."
        },
        "naivebayes-classifier": {
            "operation": "train",
            "texts": ["This is a positive review", "Great product, highly recommended",
                      "Terrible experience, waste of money", "Not satisfied with the quality",
                      "Amazing service and fast delivery"],
            "labels": ["positive", "positive", "negative", "negative", "positive"],
            "model_id": "sentiment_model",
            "vectorizer_type": "tfidf"
        },
        "linear-regression": {
            "operation": "train",
            "X": [[1], [2], [3], [4], [5]],
            "y": [2, 4, 6, 8, 10],
            "model_id": "price_model",
            "model_type": "linear"
        },
        "topic-modeling": {
            "operation": "train",
            "documents": [
                "Machine learning is a subset of artificial intelligence",
                "Deep learning uses neural networks with multiple layers",
                "Python is a popular programming language for data science",
                "Natural language processing helps computers understand text",
                "Computer vision enables machines to interpret images"
            ],
            "n_topics": 2,
            "model_id": "tech_topics",
            "method": "lda"
        },
        "pcadimensionality-reduction": {
            "operation": "fit",
            "X": [[2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0], [2.3, 2.7]],
            "n_components": 1,
            "model_id": "feature_reducer"
        },
        
        # Utility Functions (no AI) - both noai- prefixed and non-prefixed versions
        "noai-image-generator": {
            "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "operations": [
                {"type": "resize", "width": 800, "height": 600},
                {"type": "filter", "name": "sharpen"},
                {"type": "brightness", "factor": 1.2}
            ],
            "output_format": "PNG"
        },
        "image-processor": {
            "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "operations": [
                {"type": "resize", "width": 800, "height": 600},
                {"type": "filter", "name": "sharpen"},
                {"type": "brightness", "factor": 1.2}
            ],
            "output_format": "PNG"
        },
        "noai-data-validator": {
            "data": {
                "email": "test@example.com",
                "age": 25,
                "phone": "1234567890",
                "website": "https://example.com"
            },
            "schema": {
                "email": {"required": True, "type": "string", "format": "email"},
                "age": {"required": True, "type": "integer", "min": 0, "max": 150},
                "phone": {"required": False, "type": "string", "format": "phone"},
                "website": {"required": False, "type": "string", "format": "url"}
            }
        },
        "data-validator": {
            "data": {
                "email": "test@example.com",
                "age": 25,
                "phone": "1234567890",
                "website": "https://example.com"
            },
            "schema": {
                "email": {"required": True, "type": "string", "format": "email"},
                "age": {"required": True, "type": "integer", "min": 0, "max": 150},
                "phone": {"required": False, "type": "string", "format": "phone"},
                "website": {"required": False, "type": "string", "format": "url"}
            }
        },
        "noai-hash-generator": {
            "operation": "hash",
            "data": "Hello, World!",
            "algorithm": "sha256"
        },
        "hash-generator": {
            "operation": "hash",
            "data": "Hello, World!",
            "algorithm": "sha256"
        },
        "noai-qrcode-generator": {
            "data": "https://example.com",
            "error_correction": "H",
            "box_size": 10,
            "border": 4,
            "fill_color": "black",
            "back_color": "white"
        },
        "qr-code-generator": {
            "data": "https://example.com",
            "error_correction": "H",
            "box_size": 10,
            "border": 4,
            "fill_color": "black",
            "back_color": "white"
        },
        "noai-jsonxml-converter": {
            "operation": "json_to_xml",
            "data": {
                "person": {
                    "name": "John Doe",
                    "age": 30,
                    "hobbies": ["reading", "coding", "gaming"]
                }
            },
            "root_name": "data"
        },
        "json-xml-converter": {
            "operation": "json_to_xml",
            "data": {
                "person": {
                    "name": "John Doe",
                    "age": 30,
                    "hobbies": ["reading", "coding", "gaming"]
                }
            },
            "root_name": "data"
        },
        "noai-email-parser": {
            "operation": "analyze",
            "email": "user+tag@gmail.com"
        },
        "email-parser": {
            "operation": "analyze",
            "email": "user+tag@gmail.com"
        },
        "noai-data-encrypter": {
            "operation": "generate_key",
            "key_id": "my_key"
        },
        "data-encryption": {
            "operation": "generate_key",
            "key_id": "my_key"
        },
        "noai-csv-processor": {
            "operation": "parse",
            "data": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago",
            "has_header": True,
            "delimiter": ","
        },
        "csv-processor": {
            "operation": "parse",
            "data": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago",
            "has_header": True,
            "delimiter": ","
        },
        "noai-url-shortner": {
            "operation": "shorten",
            "url": "https://example.com/very/long/url/path/to/resource",
            "custom_code": "mylink"
        },
        "url-shortener": {
            "operation": "shorten",
            "url": "https://example.com/very/long/url/path/to/resource",
            "custom_code": "mylink"
        },
        "noai-pdf-generator": {
            "type": "simple",
            "title": "My Document",
            "content": [
                "This is the first paragraph.",
                "This is the second paragraph.",
                "And this is the third paragraph."
            ],
            "page_size": "letter"
        },
        "pdf-generator": {
            "type": "simple",
            "title": "My Document",
            "content": [
                "This is the first paragraph.",
                "This is the second paragraph.",
                "And this is the third paragraph."
            ],
            "page_size": "letter"
        },
    }
    
    # Handle kmeans variants
    kmeans_variants = [
        "kmeans-clustering", "kmeans-clustering-code-type",
        "kmeans-clustering-command-type", "kmeans-clustering-fileop-type",
        "kmeans-clustering-info-type"
    ]
    kmeans_payload = {
        "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
        "n_clusters": 2,
        "operation": "fit_predict",
        "normalize": True,
        "model_id": "customer_segments"
    }
    for variant in kmeans_variants:
        payloads[variant] = kmeans_payload
    
    # Handle decisiontree-classifier variants
    decisiontree_variants = [
        "decisiontree-classifier", "decisiontree-classifier-code-type",
        "decisiontree-classifier-command-type", "decisiontree-classifier-fileop-type",
        "decisiontree-classifier-info-type"
    ]
    decisiontree_payload = {
        "operation": "train",
        "X": [[5.1, 3.5, 1.4, 0.2], [4.9, 3.0, 1.4, 0.2], [7.0, 3.2, 4.7, 1.4],
              [6.4, 3.2, 4.5, 1.5], [6.3, 3.3, 6.0, 2.5], [5.8, 2.7, 5.1, 1.9]],
        "y": ["setosa", "setosa", "versicolor", "versicolor", "virginica", "virginica"],
        "model_id": "iris_model",
        "max_depth": 3
    }
    for variant in decisiontree_variants:
        payloads[variant] = decisiontree_payload
    
    # Handle time-series-forecaster variants
    timeseries_variants = [
        "time-series-forecaster", "time-series-forecaster-code-type",
        "time-series-forecaster-command-type", "time-series-forecaster-fileop-type",
        "time-series-forecaster-info-type"
    ]
    timeseries_payload = {
        "series": [10, 12, 15, 14, 18, 21, 23, 25],
        "forecast_steps": 5,
        "degree": 1
    }
    for variant in timeseries_variants:
        payloads[variant] = timeseries_payload
    
    return payloads.get(func_name, {"test": True})


def cleanup_port(port: int, exclude_pid: int = None):
    """Kill any process on the port, excluding the current Python process."""
    current_pid = os.getpid()
    try:
        result = subprocess.run(
            ['lsof', '-t', f'-i:{port}'],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    pid_int = int(pid)
                    # Don't kill ourselves or excluded pid
                    if pid_int == current_pid or pid_int == exclude_pid:
                        continue
                    print_info(f"Cleaning up process on port {port} (PID: {pid})")
                    try:
                        os.kill(pid_int, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            time.sleep(1)
    except Exception as e:
        pass  # lsof might not be available or no process on port


def terminate_process(process: subprocess.Popen):
    """Safely terminate a subprocess and all its children."""
    if process is None:
        return
    
    current_pgid = os.getpgid(os.getpid())
    
    try:
        # Check if process is still running
        if process.poll() is not None:
            return  # Already terminated
        
        # Try to get the process group and kill all children
        try:
            pgid = os.getpgid(process.pid)
            # Only kill the process group if it's different from our own
            if pgid != current_pgid:
                os.killpg(pgid, signal.SIGTERM)
                time.sleep(0.5)
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass
        except (ProcessLookupError, OSError):
            pass
        
        # Also try direct termination
        try:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        except Exception:
            pass
    except Exception as e:
        print_warning(f"Error terminating process: {e}")


def wait_for_function(port: int, timeout: int) -> bool:
    """Wait for function to be ready."""
    print_info(f"Waiting for function to be ready on port {port}...")
    
    elapsed = 0
    while elapsed < timeout:
        try:
            # Earlier the timeout was 2 seconds, now it is 10 seconds. It is to avoid the timeout error.
            response = requests.get(f"http://localhost:{port}", timeout=10)
            if response.status_code in [200, 400, 404, 405]:
                print_success("Function is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        print(".", end="", flush=True)
        time.sleep(HEALTH_CHECK_INTERVAL)
        elapsed += HEALTH_CHECK_INTERVAL
    
    print("")
    print_error(f"Function did not become ready within {timeout} seconds")
    return False


def test_function(yaml_file: Path, func_name: str) -> bool:
    """Test a single function."""
    func_dir = yaml_file.parent
    
    print_step(f"Testing function: {func_name}")
    print_info(f"YAML file: {yaml_file}")
    print_info(f"Directory: {func_dir}")
    
    # Get test payload
    payload = get_test_payload(func_name)
    print_info(f"Test payload: {json.dumps(payload)}")
    
    # Cleanup any existing process on the port
    cleanup_port(PORT)
    
    # Start the function in background
    print_info(f"Starting function with: faas-cli local-run {func_name} -f {yaml_file.name}")
    
    log_file = f"/tmp/faas_output_{os.getpid()}.log"
    
    # Change to function directory and run
    original_dir = os.getcwd()
    os.chdir(func_dir)
    
    process = None
    try:
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                ['faas-cli', 'local-run', func_name, '-f', yaml_file.name, '--port', str(PORT)],
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True  # Create new session so SIGTERM doesn't affect parent
            )
        
        print_info(f"Function started with PID: {process.pid}")
        
        # Wait for function to be ready
        if not wait_for_function(PORT, WAIT_TIMEOUT):
            print_error("Function failed to start")
            print_info("faas-cli output:")
            try:
                with open(log_file, 'r') as f:
                    print(f.read())
            except Exception:
                pass
            
            terminate_process(process)
            cleanup_port(PORT)
            return False
        
        # Make the HTTP request
        print_info("Sending HTTP request...")
        
        try:
            response = requests.post(
                f"http://localhost:{PORT}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            http_code = response.status_code
            body = response.text
        except requests.exceptions.RequestException as e:
            print_error(f"HTTP request failed: {e}")
            http_code = 0
            body = str(e)
        
        print_info(f"HTTP Response Code: {http_code}")
        print_info(f"Response Body: {body}")
        
        # Stop the function
        print_info("Stopping function...")
        terminate_process(process)
        cleanup_port(PORT)
        time.sleep(1)
        
        # Check response
        if 200 <= http_code < 300:
            # Check if response body contains error
            if '"error"' in body.lower():
                if '"statusCode": 4' in body or '"statuscode": 4' in body.lower():
                    print_warning("Function returned validation error (4xx), but HTTP succeeded")
                else:
                    print_error(f"Response contains error: {body}")
                    return False
            
            print_success(f"Function {func_name} passed!")
            return True
        else:
            print_error(f"HTTP request failed with code: {http_code}")
            print_error(f"Response: {body}")
            return False
            
    finally:
        # Always cleanup process and restore directory
        if process is not None:
            terminate_process(process)
            cleanup_port(PORT)
        os.chdir(original_dir)


def discover_functions() -> list:
    """Find all YAML files (excluding template and build directories)."""
    yaml_files = []
    
    for yaml_file in SCRIPT_DIR.rglob("*.yaml"):
        # Skip template, build, and archived directories
        parts = yaml_file.parts
        if 'template' in parts or 'build' in parts or 'archived' in parts:
            continue
        yaml_files.append(yaml_file)
    
    return sorted(yaml_files)


def main():
    global passed, failed, skipped
    
    print(f"{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║              OpenFaaS Function Test Suite                                    ║")
    print("║              Testing all functions in the functions directory                ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")
    
    print_step("Discovering functions...")
    
    yaml_files = discover_functions()
    
    if not yaml_files:
        print_error(f"No YAML files found in {SCRIPT_DIR}")
        sys.exit(1)
    
    total = len(yaml_files)
    print_info(f"Found {total} function YAML files")
    
    print("")
    print_info("Functions to test:")
    for yaml_file in yaml_files:
        func_name = get_function_name(yaml_file)
        rel_path = yaml_file.relative_to(SCRIPT_DIR)
        print(f"  - {func_name} ({rel_path})")
    
    # Ask for confirmation
    print("")
    print_warning(f"This will start each function one by one on port {PORT}")
    print_info("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(0)
    
    # Test each function
    for current, yaml_file in enumerate(yaml_files, 1):
        func_name = get_function_name(yaml_file)
        
        print("")
        print(f"{Colors.YELLOW}════════════════════════════════════════════════════════════════════════════════{Colors.NC}")
        print(f"{Colors.YELLOW}  Function {current} of {total}: {func_name}{Colors.NC}")
        print(f"{Colors.YELLOW}════════════════════════════════════════════════════════════════════════════════{Colors.NC}")
        
        if not func_name:
            print_warning(f"Could not extract function name from {yaml_file}, skipping...")
            skipped += 1
            continue
        
        if test_function(yaml_file, func_name):
            passed += 1
        else:
            failed += 1
            print_error(f"Function {func_name} FAILED - exiting as per requirements")
            
            # Summary before exit
            print("")
            print(f"{Colors.RED}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.NC}")
            print(f"{Colors.RED}║                          TEST FAILED                                         ║{Colors.NC}")
            print(f"{Colors.RED}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.NC}")
            print("")
            print(f"Results: {passed} passed, {failed} failed, {skipped} skipped out of {total} total")
            print(f"Failed at: {func_name}")
            sys.exit(1)
    
    # Final summary
    print("")
    print(f"{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║                          ALL TESTS PASSED                                    ║{Colors.NC}")
    print(f"{Colors.GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.NC}")
    print("")
    print(f"Results: {Colors.GREEN}{passed} passed{Colors.NC}, {Colors.RED}{failed} failed{Colors.NC}, {Colors.YELLOW}{skipped} skipped{Colors.NC} out of {total} total")
    print("")
    print_success("All function tests completed successfully!")
    
    sys.exit(0)


if __name__ == "__main__":
    main()

