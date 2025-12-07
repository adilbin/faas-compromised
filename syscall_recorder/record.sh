#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/binbhutto/custom-traceloop:latest"
NS="openfaas-fn"
RUNS=100
# RUNS=3
TIMEOUT=3
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Dynamically fetch all running pods in the namespace
echo "Fetching pods from namespace: $NS"
mapfile -t PODS < <(kubectl get pods -n "$NS" --field-selector=status.phase=Running -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n')

if [ ${#PODS[@]} -eq 0 ]; then
  echo "Error: No running pods found in namespace $NS"
  exit 1
fi

echo "Found ${#PODS[@]} running pods:"
printf '  - %s\n' "${PODS[@]}"
echo

# Process each pod separately
for POD in "${PODS[@]}"; do
  LOG_DIR="data/func_invc_absent/${TIMESTAMP}"
  LOG_FILE="${LOG_DIR}/logs_${POD}.json"
  
  # Create directory if it doesn't exist
  mkdir -p "$LOG_DIR"
  
  # Ensure the log exists and is writable
  : > "$LOG_FILE"
  
  echo "Starting recording for pod: $POD"
  
  for i in $(seq 1 "$RUNS"); do
    echo "=== Run $i/$RUNS started at $(date -Is) ===" >> "$LOG_FILE"
    # Run gadget with built-in --timeout targeting specific pod
    # Use tee -a if also wanting to see live output on terminal
    if kubectl gadget run "$IMAGE" --output json --timeout "$TIMEOUT" --namespace "$NS" --podname "$POD" >> "$LOG_FILE" 2>&1; then
      echo "=== Run $i completed at $(date -Is) ===" >> "$LOG_FILE"
    else
      rc=$?
      echo "=== Run $i failed with exit code $rc at $(date -Is) ===" >> "$LOG_FILE"
    fi
    # Small pause between runs to avoid overlap
    sleep 1
  done
  
  echo "Completed recording for pod: $POD (log: $LOG_FILE)"
  curl -d "Completed recording for pod: $POD (log: $LOG_FILE)" https://ntfy.sh/adilbb_umea_se_cs

done

echo "All pod recordings completed!"

curl -d "Syscall record script complete" https://ntfy.sh/adilbb_umea_se_cs