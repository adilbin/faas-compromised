# FaaS Compromised Function Detection and Dataset

Produced system call dataset and detecting compromised serverless functions using system call analysis and machine learning.

## Overview

This research project investigates whether malicious behavior in serverless (FaaS) functions can be detected by analyzing their system call patterns. We deploy functions on OpenFaaS, record their system calls, and train ML models to distinguish between benign and compromised functions.

## Attack Types

Based on [academic research](https://sites.google.com/view/pypiempircal) on malicious PyPi packages:

| Type | Description |
|------|-------------|
| **Information Stealing** | Reads sensitive files, collects host info, exfiltrates data |
| **Code Execution** | Downloads and executes arbitrary Python code |
| **Command Execution** | Runs shell commands and sends results to attacker |
| **File Operation** | Downloads, executes, and removes malicious binaries |

## Repository Structure

```
├── functions/                  # 30 OpenFaaS function definitions
│   ├── utility_functions/      # 20 benign functions (AI & non-AI)
│   └── compromised_functions/  # 10 compromised variants (4 attack types)
├── src/                        # Source code for function handlers
├── syscall_recorder/           # Scripts to record syscalls using traceloop
├── dataset/                    # Collected syscall data
├── data_analysis/              # EDA notebooks and visualizations
├── detection_methods/          # ML models for detection
│   ├── 01_svm/
│   ├── 02_xgboost/
│   ├── 03_1d-cnn/
│   ├── 04_transformer/
│   └── 05_gnn/
└── configs/                    # Configuration files
```

## Quick Start

1. **Setup environment** — Run `syscall_recorder/system_bootstrap.bash` (Tested on Ubuntu 24.04)
2. **Deploy functions** — Use scripts in `functions/` to push to OpenFaaS
3. **Record syscalls** — Run `./syscall_recorder/record.sh` from repo root
4. **Train models** — Use notebooks in `detection_methods/`

## Tech Stack

- **OpenFaaS** on Kubernetes for function deployment
- **traceloop** (inspektor-gadget) for syscall recording
- **Python** ML stack (scikit-learn, XGBoost, PyTorch)

## License

Research use only. Compromised function code is for security analysis — do not deploy to production.

