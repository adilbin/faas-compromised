#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/binbhutto/custom-traceloop:latest"
NS="openfaas-fn"
RUNS=100
TIMEOUT=3
INVOCATION_INTERVAL=2
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GATEWAY_URL="http://localhost:8080/function"

# Function to extract function name from pod name
get_function_name() {
  local pod=$1
  # Extract function name by removing the deployment hash suffix
  # e.g., "kmeans-clustering-command-type-6c47876955-2c97l" -> "kmeans-clustering-command-type"
  echo "$pod" | sed -E 's/-[a-z0-9]+-[a-z0-9]+$//'
}

# Function to get the appropriate payload for each function
get_payload() {
  local func_name=$1
  case "$func_name" in
    text-summarizer)
      echo '{"text":"Artificial intelligence is transforming the technology landscape. Machine learning algorithms can now process vast amounts of data. Deep learning has revolutionized computer vision and natural language processing. Companies are investing heavily in AI research and development. The future of AI looks promising with many exciting applications ahead.","num_sentences":2,"method":"tfidf"}'
      ;;
    anomaly-detector)
      echo '{"data":[[1.2,3.4],[2.1,3.5],[1.8,3.3],[2.0,3.6],[100,200]],"train":true,"contamination":0.1}'
      ;;
    sentiment-analyzer)
      echo '{"text":"This product is amazing! I love it."}'
      ;;
    time-series-forecaster)
      echo '{"series":[10,12,15,14,18,21,23,25],"forecast_steps":5,"degree":1}'
      ;;
    kmeans-clustering|kmeans-clustering-info-type|kmeans-clustering-code-type|kmeans-clustering-command-type|kmeans-clustering-fileop-type)
      echo '{"data":[[1,2],[1.5,1.8],[5,8],[8,8],[1,0.6]],"n_clusters":2,"operation":"fit_predict","normalize":true,"model_id":"customer_segments"}'
      ;;
    naivebayes-classifier)
      echo '{"operation":"train","texts":["This is a positive review","Great product, highly recommended","Terrible experience, waste of money","Not satisfied with the quality","Amazing service and fast delivery"],"labels":["positive","positive","negative","negative","positive"],"model_id":"sentiment_model","vectorizer_type":"tfidf"}'
      ;;
    decisiontree-classifier)
      echo '{"operation":"train","X":[[5.1,3.5,1.4,0.2],[4.9,3.0,1.4,0.2],[7.0,3.2,4.7,1.4],[6.4,3.2,4.5,1.5],[6.3,3.3,6.0,2.5],[5.8,2.7,5.1,1.9]],"y":["setosa","setosa","versicolor","versicolor","virginica","virginica"],"model_id":"iris_model","max_depth":3}'
      ;;
    linear-regression)
      echo '{"operation":"train","X":[[1],[2],[3],[4],[5]],"y":[2,4,6,8,10],"model_id":"price_model","model_type":"linear"}'
      ;;
    topic-modeling)
      echo '{"operation":"train","documents":["Machine learning is a subset of artificial intelligence","Deep learning uses neural networks with multiple layers","Python is a popular programming language for data science","Natural language processing helps computers understand text","Computer vision enables machines to interpret images"],"n_topics":2,"model_id":"tech_topics","method":"lda"}'
      ;;
    pcadimensionality-reduction)
      echo '{"operation":"fit","X":[[2.5,2.4],[0.5,0.7],[2.2,2.9],[1.9,2.2],[3.1,3.0],[2.3,2.7]],"n_components":1,"model_id":"feature_reducer"}'
      ;;
    noai-image-generator)
      echo '{"image":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==","operations":[{"type":"resize","width":800,"height":600},{"type":"filter","name":"sharpen"},{"type":"brightness","factor":1.2}],"output_format":"PNG"}'
      ;;
    noai-data-validator)
      echo '{"data":{"email":"test@example.com","age":25,"phone":"1234567890","website":"https://example.com"},"schema":{"email":{"required":true,"type":"string","format":"email"},"age":{"required":true,"type":"integer","min":0,"max":150},"phone":{"required":false,"type":"string","format":"phone"},"website":{"required":false,"type":"string","format":"url"}}}'
      ;;
    noai-hash-generator)
      echo '{"operation":"hash","data":"Hello, World!","algorithm":"sha256"}'
      ;;
    noai-qrcode-generator)
      echo '{"data":"https://example.com","error_correction":"H","box_size":10,"border":4,"fill_color":"black","back_color":"white"}'
      ;;
    noai-jsonxml-converter)
      echo '{"operation":"json_to_xml","data":{"person":{"name":"John Doe","age":30,"hobbies":["reading","coding","gaming"]}},"root_name":"data"}'
      ;;
    noai-email-parser)
      echo '{"operation":"analyze","email":"user+tag@gmail.com"}'
      ;;
    noai-data-encrypter)
      echo '{"operation":"generate_key","key_id":"my_key"}'
      ;;
    noai-csv-processor)
      echo '{"operation":"parse","data":"name,age,city\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago","has_header":true,"delimiter":","}'
      ;;
    noai-url-shortner)
      echo '{"operation":"shorten","url":"https://example.com/very/long/url/path/to/resource","custom_code":"mylink"}'
      ;;
    noai-pdf-generator)
      echo '{"type":"simple","title":"My Document","content":["This is the first paragraph.","This is the second paragraph.","And this is the third paragraph."],"page_size":"letter"}'
      ;;
    *)
      echo '{}'
      ;;
  esac
}

# Function to continuously trigger HTTP calls
trigger_function_loop() {
  local func_name=$1
  local payload=$2
  local url="${GATEWAY_URL}/${func_name}"
  
  while true; do
    curl -s -X POST "$url" \
      -H "Content-Type: application/json" \
      -d "$payload" > /dev/null 2>&1 || true
    sleep "${INVOCATION_INTERVAL}"
  done
}

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
  LOG_DIR="data/func_invc_present/${TIMESTAMP}"
  LOG_FILE="${LOG_DIR}/logs_${POD}.json"
  
  # Create directory if it doesn't exist
  mkdir -p "$LOG_DIR"
  
  # Ensure the log exists and is writable
  : > "$LOG_FILE"
  
  # Extract function name from pod name
  FUNC_NAME=$(get_function_name "$POD")
  PAYLOAD=$(get_payload "$FUNC_NAME")
  
  echo "Starting recording for pod: $POD (function: $FUNC_NAME)"
  
  # Start background process to trigger function every second
  trigger_function_loop "$FUNC_NAME" "$PAYLOAD" &
  TRIGGER_PID=$!
  
  echo "Started function trigger loop (PID: $TRIGGER_PID)"

  for i in $(seq 1 "$RUNS"); do
    echo "=== Run $i/$RUNS started at $(date -Is) ===" >> "$LOG_FILE"
    
    
    # Run gadget with built-in --timeout targeting specific pod
    if kubectl gadget run "$IMAGE" --output json --timeout "$TIMEOUT" --namespace "$NS" --podname "$POD" >> "$LOG_FILE" 2>&1; then
      echo "=== Run $i completed at $(date -Is) ===" >> "$LOG_FILE"
    else
      rc=$?
      echo "=== Run $i failed with exit code $rc at $(date -Is) ===" >> "$LOG_FILE"
    fi
    
    
    # Small pause between runs to avoid overlap
    sleep 1
  done

  # Kill the background trigger process
  kill "$TRIGGER_PID" 2>/dev/null || true
  echo "Stopped function trigger loop (PID: $TRIGGER_PID)"
  
  echo "Completed recording for pod: $POD (log: $LOG_FILE)"
  curl -d "Completed recording for pod: $POD (log: $LOG_FILE)" https://ntfy.sh/adilbb_umea_se_cs
done

echo "All pod recordings completed!"

curl -d "Syscall record script complete" https://ntfy.sh/adilbb_umea_se_cs