#!/usr/bin/env bash
#
# Kubernetes Development Environment Bootstrap Script
# Installs: Docker, KVM, Minikube, OpenFaaS, Inspektor Gadget
#
# Usage: ./bootstrap.sh
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Constants
readonly SCRIPT_NAME="$(basename "${0}")"
readonly ARKADE_BIN="${HOME}/.arkade/bin"
readonly KREW_BIN="${KREW_ROOT:-${HOME}/.krew}/bin"
readonly MINIKUBE_CPUS=8
readonly MINIKUBE_MEMORY="20g"
readonly MINIKUBE_DISK="200g"
# Disabled kvm2 way due to BPF flag mising error in latest kernel. For now opted for docker as driver.
# readonly MINIKUBE_DRIVER="kvm2"
readonly MINIKUBE_DRIVER="docker"

# Colors for output
readonly COLOR_RED=$'\033[0;31m'
readonly COLOR_GREEN=$'\033[0;32m'
readonly COLOR_YELLOW=$'\033[1;33m'
readonly COLOR_BLUE=$'\033[0;34m'
readonly COLOR_RESET=$'\033[0m'

# Logging functions
log_info() {
    echo -e "${COLOR_GREEN}[INFO]${COLOR_RESET} ${1}" >&2
}

log_warn() {
    echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} ${1}" >&2
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} ${1}" >&2
}

log_step() {
    echo -e "${COLOR_BLUE}==>${COLOR_RESET} ${1}" >&2
}

# Error handler
error_exit() {
    log_error "${1}"
    exit 1
}

# Check if running as root
check_not_root() {
    if [[ "${EUID}" -eq 0 ]]; then
        error_exit "Please do not run this script as root or with sudo"
    fi
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker already installed"
        return 0
    fi

    log_step "Installing Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    rm -f /tmp/get-docker.sh
    
    sudo usermod -aG docker "${USER}"
    log_warn "Added ${USER} to docker group. You may need to log out and back in."
}

# Install KVM and libvirt
install_kvm() {
    log_step "Installing KVM and libvirt..."
    sudo apt-get update -q
    sudo apt-get install -y -q \
        qemu-kvm \
        libvirt-daemon-system \
        libvirt-clients \
        bridge-utils \
        curl \
        wget

    sudo usermod -aG libvirt "${USER}"
    sudo systemctl enable --now libvirtd
    log_info "KVM and libvirt installed successfully"
}

# Install arkade
install_arkade() {
    if command -v arkade &> /dev/null; then
        log_info "arkade already installed"
        return 0
    fi

    log_step "Installing arkade..."
    curl -sLS https://get.arkade.dev | sudo sh
}

# Install krew
install_krew() {
    if [[ -x "${KREW_BIN}/kubectl-krew" ]]; then
        log_info "krew already installed"
        return 0
    fi

    log_step "Installing krew..."
    local temp_dir
    temp_dir="$(mktemp -d)"
    
    (
        cd "${temp_dir}"
        local os arch krew_archive
        os="$(uname | tr '[:upper:]' '[:lower:]')"
        arch="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')"
        krew_archive="krew-${os}_${arch}"
        
        curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${krew_archive}.tar.gz"
        tar zxf "${krew_archive}.tar.gz"
        ./"${krew_archive}" install krew
    )
    
    rm -rf "${temp_dir}"
}

# Install CLI tools via arkade
install_cli_tools() {
    log_step "Installing CLI tools via arkade..."
    
    export PATH="${ARKADE_BIN}:${PATH}"
    
    # Install kubectl if not exists or not working
    if [[ ! -x "${ARKADE_BIN}/kubectl" ]] || ! "${ARKADE_BIN}/kubectl" version --client &>/dev/null; then
        arkade get kubectl
    else
        log_info "kubectl already installed and working"
    fi
    
    # Install minikube if not exists
    if [[ ! -x "${ARKADE_BIN}/minikube" ]]; then
        arkade get minikube
    else
        log_info "minikube already installed"
    fi
    
    # Install faas-cli if not exists
    if [[ ! -x "${ARKADE_BIN}/faas-cli" ]]; then
        arkade get faas-cli
    else
        log_info "faas-cli already installed"
    fi
    
    # Verify installations
    [[ -x "${ARKADE_BIN}/kubectl" ]] || error_exit "kubectl installation failed"
    [[ -x "${ARKADE_BIN}/minikube" ]] || error_exit "minikube installation failed"
    [[ -x "${ARKADE_BIN}/faas-cli" ]] || error_exit "faas-cli installation failed"
    
    log_info "CLI tools installed successfully"
}

# Install kubectl-gadget via krew
install_kubectl_gadget() {
    log_step "Installing kubectl-gadget via krew..."
    
    export PATH="${KREW_BIN}:${ARKADE_BIN}:${PATH}"
    
    "${ARKADE_BIN}/kubectl" krew install gadget
    
    if ! "${ARKADE_BIN}/kubectl" krew list | grep -q "gadget"; then
        error_exit "kubectl-gadget installation via krew failed"
    fi
    
    log_info "kubectl-gadget installed successfully"
}

# Install KVM2 driver for minikube
install_kvm2_driver() {
    if [[ -f /usr/local/bin/docker-machine-driver-kvm2 ]]; then
        log_info "KVM2 driver already installed"
        return 0
    fi

    log_step "Installing KVM2 driver for minikube..."
    curl -fsSLO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
    sudo install docker-machine-driver-kvm2 /usr/local/bin/
    rm -f docker-machine-driver-kvm2
    log_info "KVM2 driver installed successfully"
}

# Setup minikube cluster
setup_minikube() {
    local minikube="${ARKADE_BIN}/minikube"

    # Option 2: Ask before deleting
    if "${minikube}" status &> /dev/null; then
        read -p "Existing cluster found. Delete and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            "${minikube}" delete
        else
            log_info "Keeping existing cluster"
            return 0
        fi
    fi

    log_step "Starting minikube (${MINIKUBE_CPUS} CPUs, ${MINIKUBE_MEMORY} RAM, ${MINIKUBE_DISK} disk)..."
    "${minikube}" start \
        --driver="${MINIKUBE_DRIVER}" \
        --kubernetes-version=v1.28.3 \
        --cpus="${MINIKUBE_CPUS}" \
        --memory="${MINIKUBE_MEMORY}" \
        --disk-size="${MINIKUBE_DISK}"

    log_info "Waiting for cluster to be ready..."
    "${ARKADE_BIN}/kubectl" wait --for=condition=Ready nodes --all --timeout=300s
    log_info "Minikube cluster is ready"
}

# Install OpenFaaS
install_openfaas() {
    local kubectl="${ARKADE_BIN}/kubectl"
    
    log_step "Installing OpenFaaS via arkade..."
    arkade install openfaas

    log_info "Waiting for OpenFaaS to be ready..."
    "${kubectl}" rollout status -n openfaas deploy/gateway --timeout=300s
    "${kubectl}" wait --for=condition=Ready pods --all -n openfaas --timeout=300s
    
    log_info "OpenFaaS installed successfully"
}

# Install Inspektor Gadget
install_inspektor_gadget() {
    local kubectl="${ARKADE_BIN}/kubectl"
    
    log_step "Installing Inspektor Gadget..."
    "${kubectl}" gadget deploy --verify-image=false

    log_info "Waiting for Inspektor Gadget to be ready..."
    "${kubectl}" wait --for=condition=Ready pods -n gadget --all --timeout=300s
    log_info "Inspektor Gadget installed successfully"
}

# Get OpenFaaS credentials
get_openfaas_credentials() {
    local kubectl="${ARKADE_BIN}/kubectl"
    local password
    
    password=$("${kubectl}" get secret -n openfaas basic-auth \
        -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
    
    echo "${password}"
}

# Update shell configuration
update_shell_config() {
    local shell_rc=""
    
    if [[ -n "${BASH_VERSION:-}" ]]; then
        shell_rc="${HOME}/.bashrc"
    elif [[ -n "${ZSH_VERSION:-}" ]]; then
        shell_rc="${HOME}/.zshrc"
    fi
    
    if [[ -z "${shell_rc}" ]] || [[ ! -f "${shell_rc}" ]]; then
        log_warn "Could not detect shell configuration file"
        return 0
    fi
    
    log_step "Updating PATH in ${shell_rc}..."
    
    # Add arkade to PATH
    if ! grep -q 'arkade/bin' "${shell_rc}"; then
        cat >> "${shell_rc}" << 'EOF'

# Arkade binaries
export PATH="${HOME}/.arkade/bin:${PATH}"
EOF
        log_info "Added arkade to PATH"
    fi
    
    # Add krew to PATH
    if ! grep -q 'krew/bin' "${shell_rc}"; then
        cat >> "${shell_rc}" << 'EOF'

# Krew binaries
export PATH="${KREW_ROOT:-${HOME}/.krew}/bin:${PATH}"
EOF
        log_info "Added krew to PATH"
    fi
}

# Print summary
print_summary() {
    local openfaas_password="${1}"
    
    cat << EOF

${COLOR_GREEN}================================
Bootstrap Complete!
================================${COLOR_RESET}

${COLOR_BLUE}Summary:${COLOR_RESET}
  • Minikube: Running with ${MINIKUBE_DRIVER} driver
  • Resources: ${MINIKUBE_CPUS} CPUs, ${MINIKUBE_MEMORY} RAM, ${MINIKUBE_DISK} disk
  • OpenFaaS: Installed and running
  • Inspektor Gadget: Installed and running

${COLOR_BLUE}OpenFaaS Details:${COLOR_RESET}
  • Gateway URL: http://127.0.0.1:8080 (after port-forward)
  • Username: admin
  • Password: ${openfaas_password}

${COLOR_BLUE}Next Steps:${COLOR_RESET}

  1. Reload your shell configuration:
     ${COLOR_YELLOW}source ~/.bashrc${COLOR_RESET}  (or ~/.zshrc)

  2. Port-forward OpenFaaS gateway:
     ${COLOR_YELLOW}kubectl port-forward -n openfaas svc/gateway 8080:8080 &${COLOR_RESET}

  3. Login to OpenFaaS:
     ${COLOR_YELLOW}echo '${openfaas_password}' | faas-cli login --username admin --password-stdin${COLOR_RESET}

${COLOR_BLUE}Useful Commands:${COLOR_RESET}
  • minikube status              - Check cluster status
  • minikube stop                - Stop the cluster
  • minikube delete              - Delete the cluster
  • minikube dashboard           - Open Kubernetes dashboard
  • kubectl get pods -A          - List all pods
  • kubectl gadget --help        - Inspektor Gadget commands
  • faas-cli list                - List OpenFaaS functions
  • arkade install --help        - Browse arkade apps

EOF
}

# Main execution
main() {
    echo ""
    log_step "Starting Kubernetes Development Environment Bootstrap"
    echo ""
    
    check_not_root
    # Uncomment the below line if minikube driver is kvm2
    # install_kvm
    install_docker
    install_arkade
    install_krew
    install_cli_tools
    install_kubectl_gadget
    # Uncomment the below line if minikube driver is kvm2
    # install_kvm2_driver
    setup_minikube
    install_openfaas
    install_inspektor_gadget
    
    local openfaas_password
    openfaas_password="$(get_openfaas_credentials)"
    
    update_shell_config
    print_summary "${openfaas_password}"
}

# Run main function
main "$@"
