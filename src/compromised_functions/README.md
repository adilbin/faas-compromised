# Compromised Function Handlers

This directory contains four compromised Python function handlers that demonstrate malicious behaviors as documented in the literature. Each handler maintains legitimate functionality (generating random integers) while performing malicious operations in the background.

## Handler Files

### 1. Information Stealing (`info_stealing.py`)

**Pattern**: `S -> [Cf(Path)] -> [Ch] -> [Ce] -> Cn(URL) -> E`

**Description**: Steals sensitive information from the host system and exfiltrates it to a remote server.

**Malicious Behaviors**:
- **File Operations (Cf)**: Reads sensitive local files such as:
  - `/etc/passwd` - System user accounts
  - `/etc/shadow` - Password hashes
  - `~/.ssh/id_rsa` - SSH private keys
  - `~/.aws/credentials` - AWS credentials
  - `~/.bash_history` - Command history
- **Host Information (Ch)**: Collects system information:
  - Environment variables
  - Current working directory
  - User ID and Group ID
- **Encoding (Ce)**: Obfuscates stolen data using base64 encoding
- **Network Connection (Cn)**: Sends encoded data to `http://attacker-server.com/collect`

### 2. Code Execution (`code_execution.py`)

**Pattern**: `S -> [Cn(URL)] -> [Ce] -> [Compile] -> Cc -> E`

**Description**: Downloads and executes arbitrary Python code from a remote server or embedded payload.

**Malicious Behaviors**:
- **Network Connection (Cn)**: Downloads obfuscated code from `http://attacker-server.com/payload`
- **Encoding (Ce)**: Decodes base64-encoded malicious Python code
- **Compile**: Compiles decoded string into executable Python code object using `compile()`
- **Code Execution (Cc)**: Executes the compiled code using `exec()`

**Embedded Payload**: Contains a fallback base64-encoded script that:
- Steals environment variables
- Executes shell commands (e.g., `whoami`)

### 3. Command Execution (`command_execution.py`)

**Pattern**: `S -> [Ce] -> Cs -> [Ce] -> [Cn(URL)] -> E`

**Description**: Executes malicious shell commands and exfiltrates the results.

**Malicious Behaviors**:
- **Encoding (Ce)**: Decodes base64-encoded shell commands
- **Command/Shell Execution (Cs)**: Executes system commands including:
  - `whoami` - Current user identity
  - `pwd` - Current directory
  - `ls -la /` - List root directory contents
  - `cat /etc/passwd` - Read system users
  - `ps aux` - List running processes
  - `netstat -tulpn` - Network connections
  - `env` - Environment variables
- **Encoding (Ce)**: Encodes command output using base64
- **Network Connection (Cn)**: Sends results to `http://attacker-server.com/cmd-results`

### 4. Unauthorized File Operation (`file_operation.py`)

**Pattern**: `S -> [Cn(URL)] -> Cf -> Cs -> [Cf] -> E`

**Description**: Downloads, executes, and removes malicious executables to avoid detection.

**Malicious Behaviors**:
- **Network Connection (Cn)**: Downloads malware from remote URLs:
  - `http://attacker-server.com/malware/trojan.sh`
  - `http://attacker-server.com/malware/backdoor.py`
  - `http://attacker-server.com/malware/keylogger.bin`
- **File Operations (Cf)**: Writes downloaded content to `/tmp` with execute permissions
- **Command/Shell Execution (Cs)**: Executes the malicious files as background processes
- **File Operations (Cf)**: Deletes executables after execution to erase traces

**Embedded Script**: Contains a bash script that:
- Establishes a reverse shell to attacker server
- Steals SSH keys and exfiltrates them
- Creates a backdoor user account

## Usage

Each handler follows the OpenFaaS function handler template and can be invoked with:

```python
def handle(event, context):
    # event.body contains the request payload
    # Returns a dictionary with statusCode, body, and headers
```

**Request Format**:
```json
{
  "n": 10  // Number of random integers to generate (1-100)
}
```

**Response Format**:
```json
{
  "statusCode": 200,
  "body": [12, 45, 67, 23, 89, ...],
  "headers": {
    "Content-Type": "application/json"
  }
}
```

## Security Notes

⚠️ **WARNING**: These handlers contain actual malicious code patterns for research purposes only. They should:
- **NEVER** be deployed to production environments
- Only be used in isolated, controlled testing environments
- Be used for security research and FaaS vulnerability analysis
- Not be used for any malicious or illegal activities

## API Patterns

The malicious behaviors follow these API pattern categories:

- **Cf (File Operations)**: `open()`, `read()`, `write()`, `os.remove()`, `os.chmod()`
- **Ch (Host Information)**: `os.environ`, `os.getcwd()`, `os.getuid()`, `os.getgid()`
- **Ce (Encoding)**: `base64.b64encode()`, `base64.b64decode()`
- **Cn (Network Connection)**: `urllib.request.urlopen()`, `urllib.request.Request()`
- **Cs (Command/Shell Execution)**: `subprocess.check_output()`, `subprocess.Popen()`
- **Cc (Code Execution)**: `compile()`, `exec()`

## Literature Reference

These implementations are based on malicious behavior patterns documented in FaaS security research, specifically:
- Pattern 2: Information Stealing
- Pattern 3: Code Execution
- Pattern 4: Command Execution
- Pattern 5: Unauthorized File Operation

