# ML Serverless Functions

Machine learning inference functions for OpenFaaS edge deployment.

## Available Functions

### AI/ML Functions

| Function | Model | Purpose |
|----------|-------|---------|
| `text_summarizer.py` | TF-IDF/TextRank | Extractive text summarization |
| `anomaly_detector.py` | Isolation Forest | Anomaly detection in numerical data |
| `sentiment_analyzer.py` | DistilBERT | Text sentiment analysis |
| `time_series_forecaster.py` | Linear/Polynomial Regression | Time series forecasting |
| `kmeans_clustering.py` | K-Means | Data clustering |
| `naive_bayes_classifier.py` | Naive Bayes | Text classification |
| `decision_tree_classifier.py` | Decision Tree | Structured data classification |
| `linear_regression.py` | Linear/Ridge/Lasso | Numerical prediction |
| `topic_modeling.py` | LDA/NMF | Topic extraction from documents |
| `pca_dimensionality_reduction.py` | PCA | Feature dimensionality reduction |

### Utility Functions

| Function | Purpose |
|----------|---------|
| `image_processor.py` | Image resize, crop, filter, and manipulation |
| `data_validator.py` | Data validation against schemas |
| `hash_generator.py` | Hash generation (MD5, SHA256, HMAC, etc.) |
| `qr_code_generator.py` | QR code generation from text/URLs |
| `json_xml_converter.py` | Convert between JSON and XML formats |
| `email_parser.py` | Email validation and parsing |
| `data_encryption.py` | Data encryption/decryption (Fernet) |
| `csv_processor.py` | CSV/Excel data processing and analysis |
| `url_shortener.py` | Hash-based URL shortening |
| `pdf_generator.py` | PDF document generation |

---

## 1. Text Summarizer

**Endpoint:** `POST /function/text-summarizer`

**Request (Single Text):**
```bash
curl -X POST http://localhost:8080/function/text-summarizer \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial intelligence is transforming the technology landscape. Machine learning algorithms can now process vast amounts of data. Deep learning has revolutionized computer vision and natural language processing. Companies are investing heavily in AI research and development. The future of AI looks promising with many exciting applications ahead.",
    "num_sentences": 2,
    "method": "tfidf"
  }'
```

**Request (Batch):**
```bash
curl -X POST http://localhost:8080/function/text-summarizer \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Long text 1...", "Long text 2..."],
    "num_sentences": 3,
    "method": "textrank"
  }'
```

**Request Body:**
```json
{
  "text": "Long text to summarize...",
  "num_sentences": 3,
  "method": "tfidf"
}
```
OR
```json
{
  "texts": ["Text 1...", "Text 2..."],
  "num_sentences": 3,
  "method": "textrank"
}
```

**Parameters:**
- `text` / `texts` - Single text or array of texts (required)
- `num_sentences` - Number of sentences in summary (default: 3)
- `method` - Summarization method: `tfidf` or `textrank` (default: tfidf)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "summary": "Artificial intelligence is transforming the technology landscape. The future of AI looks promising with many exciting applications ahead.",
      "sentences": [
        "Artificial intelligence is transforming the technology landscape.",
        "The future of AI looks promising with many exciting applications ahead."
      ],
      "scores": [0.89, 0.76],
      "compression_ratio": 0.4
    },
    "statistics": {
      "original_sentences": 5,
      "summary_sentences": 2,
      "compression_ratio": 0.4
    },
    "model": "TF-IDF-TFIDF"
  }
}
```

---

## 2. Anomaly Detector

**Endpoint:** `POST /function/anomaly-detector`

**Request:**
```bash
curl -X POST http://localhost:8080/function/anomaly-detector \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1.2, 3.4], [2.1, 3.5], [100, 200]],
    "train": true,
    "contamination": 0.1
  }'
```

**Request Body:**
```json
{
  "data": [[1.2, 3.4], [2.1, 3.5], [100, 200]],
  "train": true,
  "contamination": 0.1
}
```

**Parameters:**
- `data` - 2D array of numerical features (required)
- `train` - Train new model (default: false)
- `contamination` - Expected anomaly proportion (default: 0.1)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "is_anomaly": [false, false, true],
    "anomaly_scores": [-0.05, -0.03, -0.45],
    "statistics": {
      "n_samples": 3,
      "n_anomalies": 1,
      "anomaly_rate": 0.33
    },
    "model": "IsolationForest"
  }
}
```

---

## 3. Sentiment Analyzer

**Endpoint:** `POST /function/sentiment-analyzer`

**Request (Single Text):**
```bash
curl -X POST http://localhost:8080/function/sentiment-analyzer \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product is amazing! I love it."
  }'
```

**Request (Batch):**
```bash
curl -X POST http://localhost:8080/function/sentiment-analyzer \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Great service!", "Terrible experience."]
  }'
```

**Request Body:**
```json
{
  "text": "This product is amazing!"
}
```
OR
```json
{
  "texts": ["Great service!", "Terrible experience."]
}
```

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "text": "This product is amazing!",
      "sentiment": "POSITIVE",
      "confidence": 0.9998
    },
    "statistics": {
      "total_samples": 1,
      "positive_count": 1,
      "negative_count": 0
    },
    "model": "DistilBERT-SST-2"
  }
}
```

---

## 4. Time Series Forecaster

**Endpoint:** `POST /function/time-series-forecaster`

**Request:**
```bash
curl -X POST http://localhost:8080/function/time-series-forecaster \
  -H "Content-Type: application/json" \
  -d '{
    "series": [10, 12, 15, 14, 18, 21, 23, 25],
    "forecast_steps": 5,
    "degree": 1
  }'
```

**Request Body:**
```json
{
  "series": [10, 12, 15, 14, 18, 21, 23, 25],
  "forecast_steps": 5,
  "degree": 1,
  "model_id": "sales_forecast"
}
```

**Parameters:**
- `series` - Historical time series data (required)
- `forecast_steps` - Number of future steps to predict (required)
- `degree` - Polynomial degree (default: 1, linear)
- `model_id` - Model identifier for persistence (optional)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "forecasts": [
      {"step": 8, "forecast": 26.8, "lower_bound": 24.2, "upper_bound": 29.4},
      {"step": 9, "forecast": 28.9, "lower_bound": 26.1, "upper_bound": 31.7}
    ],
    "statistics": {
      "n_samples": 8,
      "mse": 1.23,
      "mae": 0.85,
      "r2_score": 0.94
    },
    "model": "LinearRegression(degree=1)"
  }
}
```

---

## 5. K-Means Clustering

**Endpoint:** `POST /function/kmeans-clustering`

**Request (Train and Predict):**
```bash
curl -X POST http://localhost:8080/function/kmeans-clustering \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
    "n_clusters": 2,
    "operation": "fit_predict"
  }'
```

**Request (Predict Only):**
```bash
curl -X POST http://localhost:8080/function/kmeans-clustering \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[2, 3], [7, 9]],
    "operation": "predict",
    "model_id": "customer_segments"
  }'
```

**Request Body:**
```json
{
  "data": [[1, 2], [1.5, 1.8], [5, 8]],
  "n_clusters": 2,
  "operation": "fit_predict",
  "normalize": true,
  "model_id": "customer_segments"
}
```

**Parameters:**
- `data` - 2D array of numerical features (required)
- `n_clusters` - Number of clusters (default: 3)
- `operation` - `fit_predict` or `predict` (default: fit_predict)
- `normalize` - Normalize data (default: true)
- `model_id` - Model identifier for persistence (optional)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "cluster_assignments": [0, 0, 1, 1, 0],
    "cluster_statistics": [
      {
        "cluster_id": 0,
        "size": 3,
        "centroid": [1.17, 1.47]
      },
      {
        "cluster_id": 1,
        "size": 2,
        "centroid": [6.5, 8.0]
      }
    ],
    "statistics": {
      "n_samples": 5,
      "n_clusters": 2
    },
    "model": "KMeans"
  }
}
```

---

## Error Response

All functions return standardized error responses:

```json
{
  "statusCode": 400,
  "body": {
    "error": "Error description here"
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input (missing data, bad JSON, invalid parameters)
- `500` - Internal error (model failure, processing error)

---

## Installation

**Dependencies:**
```bash
pip install -r requirements.txt
```

**Required packages:**
- numpy>=1.21.0
- scikit-learn>=1.0.0
- transformers>=4.20.0

**Model Downloads:**
- DistilBERT: ~268MB (downloads on first use)
- Models are cached automatically
- Text Summarizer uses no pre-trained models (lightweight TF-IDF/TextRank)

---

## Deployment

**1. Create OpenFaaS Function:**
```bash
faas-cli new --lang python3-http text-summarizer
```

**2. Copy Handler:**
```bash
cp src/utility_functions/text_summarizer.py functions/text-summarizer/handler.py
cp src/utility_functions/requirements.txt functions/text-summarizer/requirements.txt
```

**3. Build and Deploy:**
```bash
faas-cli build -f text-summarizer.yml
faas-cli deploy -f text-summarizer.yml
```

**4. Test:**
```bash
echo '{"text":"Your long text here...","num_sentences":3}' | faas-cli invoke text-summarizer
```

---

## Performance

**Cold Start Times (first invocation):**
- Text Summarizer: <1 second
- Sentiment Analyzer: ~5-8 seconds (model download on first use)
- Others: <1 second

**Subsequent invocations:** <100ms (models cached)

**Memory Requirements:**
- Text Summarizer: <100MB
- Sentiment Analyzer: ~1GB
- Others: <100MB each

---

---

## 6. Naive Bayes Classifier

**Endpoint:** `POST /function/naive-bayes-classifier`

**Request (Training):**
```bash
curl -X POST http://localhost:8080/function/naive-bayes-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "train",
    "texts": [
      "This is a positive review",
      "Great product, highly recommended",
      "Terrible experience, waste of money",
      "Not satisfied with the quality",
      "Amazing service and fast delivery"
    ],
    "labels": ["positive", "positive", "negative", "negative", "positive"],
    "model_id": "sentiment_model",
    "vectorizer_type": "tfidf"
  }'
```

**Request (Prediction):**
```bash
curl -X POST http://localhost:8080/function/naive-bayes-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "predict",
    "texts": ["This product exceeded my expectations"],
    "model_id": "sentiment_model"
  }'
```

**Parameters:**
- `operation` - `train` or `predict` (required)
- `texts` - Array of text documents (required)
- `labels` - Array of labels for training (required for train)
- `model_id` - Model identifier for storage/retrieval (optional, default: "default")
- `vectorizer_type` - `tfidf` or `count` (optional, default: "tfidf")

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "results": [
      {
        "text": "This product exceeded my expectations",
        "prediction": "positive",
        "confidence": 0.89,
        "probabilities": {"positive": 0.89, "negative": 0.11}
      }
    ],
    "statistics": {"total_samples": 1},
    "model": "Naive Bayes",
    "model_id": "sentiment_model"
  }
}
```

---

## 7. Decision Tree Classifier

**Endpoint:** `POST /function/decisiontree-classifier`

**Request (Training):**
```bash
curl -X POST http://localhost:8080/function/decisiontree-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "train",
    "X": [
      [5.1, 3.5, 1.4, 0.2],
      [4.9, 3.0, 1.4, 0.2],
      [7.0, 3.2, 4.7, 1.4],
      [6.4, 3.2, 4.5, 1.5],
      [6.3, 3.3, 6.0, 2.5],
      [5.8, 2.7, 5.1, 1.9]
    ],
    "y": ["setosa", "setosa", "versicolor", "versicolor", "virginica", "virginica"],
    "model_id": "iris_model",
    "max_depth": 3
  }'
```

**Request (Prediction):**
```bash
curl -X POST http://localhost:8080/function/decisiontree-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "predict",
    "X": [[5.0, 3.6, 1.4, 0.2], [6.5, 3.0, 5.2, 2.0]],
    "model_id": "iris_model"
  }'
```

**Parameters:**
- `operation` - `train` or `predict` (required)
- `X` - 2D array of features (required)
- `y` - Array of labels for training (required for train)
- `model_id` - Model identifier (optional, default: "default")
- `max_depth` - Maximum tree depth (optional)
- `min_samples_split` - Minimum samples to split (optional, default: 2)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "results": [
      {
        "sample_index": 0,
        "prediction": "setosa",
        "confidence": 1.0,
        "probabilities": {"setosa": 1.0, "versicolor": 0.0, "virginica": 0.0}
      }
    ],
    "statistics": {"total_samples": 2},
    "model": "Decision Tree",
    "model_id": "iris_model"
  }
}
```

---

## 8. Linear Regression

**Endpoint:** `POST /function/linear-regression`

**Request (Training):**
```bash
curl -X POST http://localhost:8080/function/linear-regression \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "train",
    "X": [[1], [2], [3], [4], [5]],
    "y": [2, 4, 6, 8, 10],
    "model_id": "price_model",
    "model_type": "linear"
  }'
```

**Request (Prediction):**
```bash
curl -X POST http://localhost:8080/function/linear-regression \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "predict",
    "X": [[6], [7], [8]],
    "model_id": "price_model"
  }'
```

**Parameters:**
- `operation` - `train` or `predict` (required)
- `X` - 2D array of features (required)
- `y` - Array of target values for training (required for train)
- `model_id` - Model identifier (optional, default: "default")
- `model_type` - `linear`, `ridge`, or `lasso` (optional, default: "linear")
- `alpha` - Regularization strength for ridge/lasso (optional, default: 1.0)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "results": [
      {"sample_index": 0, "prediction": 12.0, "features": [6]},
      {"sample_index": 1, "prediction": 14.0, "features": [7]}
    ],
    "statistics": {
      "total_samples": 3,
      "mean_prediction": 14.0,
      "std_prediction": 2.0
    },
    "model": "Linear Regression",
    "model_id": "price_model"
  }
}
```

---

## 9. Topic Modeling

**Endpoint:** `POST /function/topic-modeling`

**Request (Training):**
```bash
curl -X POST http://localhost:8080/function/topic-modeling \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Request (Prediction):**
```bash
curl -X POST http://localhost:8080/function/topic-modeling \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "predict",
    "documents": ["Neural networks are used for image classification"],
    "model_id": "tech_topics"
  }'
```

**Parameters:**
- `operation` - `train` or `predict` (required)
- `documents` - Array of text documents (required)
- `n_topics` - Number of topics to extract (optional, default: 5)
- `model_id` - Model identifier (optional, default: "default")
- `method` - `lda` or `nmf` (optional, default: "lda")
- `n_top_words` - Number of top words per topic (optional, default: 10)
- `max_features` - Maximum vocabulary size (optional, default: 1000)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "topics": [
        {"topic_id": 0, "top_words": ["learning", "machine", "neural"], "weights": [0.45, 0.32, 0.28]},
        {"topic_id": 1, "top_words": ["python", "data", "programming"], "weights": [0.51, 0.38, 0.25]}
      ],
      "document_topics": [
        {"document_index": 0, "dominant_topic": 0, "topic_distribution": [0.78, 0.22]}
      ]
    },
    "model": "LDA"
  }
}
```

---

## 10. PCA Dimensionality Reduction

**Endpoint:** `POST /function/pca-dimensionality-reduction`

**Request (Fit):**
```bash
curl -X POST http://localhost:8080/function/pca-dimensionality-reduction \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "fit",
    "X": [
      [2.5, 2.4],
      [0.5, 0.7],
      [2.2, 2.9],
      [1.9, 2.2],
      [3.1, 3.0],
      [2.3, 2.7]
    ],
    "n_components": 1,
    "model_id": "feature_reducer"
  }'
```

**Request (Transform):**
```bash
curl -X POST http://localhost:8080/function/pca-dimensionality-reduction \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "transform",
    "X": [[2.0, 2.5], [3.0, 3.2]],
    "model_id": "feature_reducer"
  }'
```

**Parameters:**
- `operation` - `fit` or `transform` (required)
- `X` - 2D array of features (required)
- `n_components` - Number of components (optional, uses variance_ratio if not set)
- `variance_ratio` - Cumulative variance to preserve (optional, default: 0.95)
- `model_id` - Model identifier (optional, default: "default")

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "n_samples": 6,
      "n_features_original": 2,
      "n_components": 1,
      "explained_variance_ratio": [0.96],
      "cumulative_variance_ratio": 0.96,
      "transformed_data": [[-0.83], [1.78], [-0.99], [-0.27], [-1.68], [-0.91]]
    },
    "model": "PCA"
  }
}
```

---

## 11. Image Processor

**Endpoint:** `POST /function/image-processor`

**Request:**
```bash
curl -X POST http://localhost:8080/function/image-processor \
  -H "Content-Type: application/json" \
  -d '{
    "image": "BASE64_ENCODED_IMAGE_DATA",
    "operations": [
      {"type": "resize", "width": 800, "height": 600},
      {"type": "filter", "name": "sharpen"},
      {"type": "brightness", "factor": 1.2},
      {"type": "rotate", "angle": 90}
    ],
    "output_format": "PNG"
  }'
```

**Parameters:**
- `image` - Base64 encoded image data (required)
- `operations` - Array of operations to apply (required)
- `output_format` - Output format: PNG, JPEG, etc. (optional, default: "PNG")

**Available Operations:**
- `resize`: `width`, `height`, `maintain_aspect` (default: true)
- `crop`: `x`, `y`, `width`, `height`
- `filter`: `name` (blur, sharpen, emboss, contour, detail, edge_enhance, smooth)
- `brightness`: `factor` (0.0 to 2.0)
- `contrast`: `factor` (0.0 to 2.0)
- `rotate`: `angle` (degrees)
- `flip`: `direction` (horizontal, vertical)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "image": "BASE64_ENCODED_OUTPUT_IMAGE",
    "statistics": {
      "original_size": [800, 600],
      "final_size": [400, 300],
      "operations_applied": 4
    },
    "operations": ["resize to (400, 300)", "filter: sharpen", "brightness: 1.2", "rotate: 90°"]
  }
}
```

---

## 12. Data Validator

**Endpoint:** `POST /function/data-validator`

**Request:**
```bash
curl -X POST http://localhost:8080/function/data-validator \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "email": "test@example.com",
      "age": 25,
      "phone": "1234567890",
      "website": "https://example.com"
    },
    "schema": {
      "email": {
        "required": true,
        "type": "string",
        "format": "email"
      },
      "age": {
        "required": true,
        "type": "integer",
        "min": 0,
        "max": 150
      },
      "phone": {
        "required": false,
        "type": "string",
        "format": "phone"
      },
      "website": {
        "required": false,
        "type": "string",
        "format": "url"
      }
    }
  }'
```

**Parameters:**
- `data` - Dictionary of data to validate (required)
- `schema` - Dictionary of validation rules per field (required)

**Schema Rule Options:**
- `required` - Field is required (boolean)
- `type` - Expected type: string, number, integer, float, boolean, list, dict
- `format` - Format validation: email, phone, url, date
- `min`, `max` - Numeric range validation
- `min_length`, `max_length` - String length validation
- `pattern` - Regex pattern validation
- `enum` - Allowed values list

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "validation": {
      "valid": true,
      "fields": {
        "email": {"valid": true, "errors": []},
        "age": {"valid": true, "errors": []}
      }
    },
    "statistics": {
      "total_fields": 4,
      "valid_fields": 4,
      "invalid_fields": 0,
      "total_errors": 0
    }
  }
}
```

---

## 13. Hash Generator

**Endpoint:** `POST /function/hash-generator`

**Request (Hash):**
```bash
curl -X POST http://localhost:8080/function/hash-generator \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "hash",
    "data": "Hello, World!",
    "algorithm": "sha256"
  }'
```

**Request (HMAC):**
```bash
curl -X POST http://localhost:8080/function/hash-generator \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "hmac",
    "data": "Hello, World!",
    "key": "my_secret_key",
    "algorithm": "sha256"
  }'
```

**Request (Batch):**
```bash
curl -X POST http://localhost:8080/function/hash-generator \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "batch",
    "items": ["item1", "item2", "item3"],
    "algorithm": "md5"
  }'
```

**Parameters:**
- `operation` - `hash`, `hmac`, `file_hash`, `verify_hash`, `verify_hmac`, `batch` (required)
- `data` - String data to hash (required for hash/hmac/verify)
- `key` - Secret key for HMAC (required for hmac/verify_hmac)
- `algorithm` - Hash algorithm: md5, sha1, sha256, sha512 (optional, default: "sha256")
- `items` - Array of strings for batch hashing (required for batch)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "hash": "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f",
    "algorithm": "sha256",
    "data_length": 13
  }
}
```

---

## 14. QR Code Generator

**Endpoint:** `POST /function/qr-code-generator`

**Request (Single):**
```bash
curl -X POST http://localhost:8080/function/qr-code-generator \
  -H "Content-Type: application/json" \
  -d '{
    "data": "https://example.com",
    "error_correction": "H",
    "box_size": 10,
    "border": 4,
    "fill_color": "black",
    "back_color": "white"
  }'
```

**Request (Batch):**
```bash
curl -X POST http://localhost:8080/function/qr-code-generator \
  -H "Content-Type: application/json" \
  -d '{
    "batch": [
      {"data": "https://example.com/page1", "error_correction": "M"},
      {"data": "https://example.com/page2", "error_correction": "H"}
    ]
  }'
```

**Parameters:**
- `data` - Text or URL to encode (required for single)
- `batch` - Array of items for batch generation (alternative to data)
- `error_correction` - Error correction level: L, M, Q, H (optional, default: "M")
- `box_size` - Size of each box in pixels (optional, default: 10)
- `border` - Border size in boxes (optional, default: 4)
- `fill_color` - Foreground color (optional, default: "black")
- `back_color` - Background color (optional, default: "white")
- `logo` - Base64 encoded logo to embed (optional)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "qr_code": "BASE64_ENCODED_PNG_IMAGE",
    "data_length": 19,
    "image_size": [290, 290],
    "error_correction": "H"
  }
}
```

---

## 15. JSON/XML Converter

**Endpoint:** `POST /function/json-xml-converter`

**Request (JSON to XML):**
```bash
curl -X POST http://localhost:8080/function/json-xml-converter \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "json_to_xml",
    "data": {
      "person": {
        "name": "John Doe",
        "age": 30,
        "hobbies": ["reading", "coding", "gaming"]
      }
    },
    "root_name": "data"
  }'
```

**Request (XML to JSON):**
```bash
curl -X POST http://localhost:8080/function/json-xml-converter \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "xml_to_json",
    "data": "<person><name>John Doe</name><age>30</age><city>New York</city></person>"
  }'
```

**Parameters:**
- `operation` - `json_to_xml`, `xml_to_json`, `dict_to_xml`, `xml_to_dict` (required)
- `data` - Data to convert (required)
- `root_name` - Root element name for XML output (optional, default: "root")

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": "<?xml version=\"1.0\" ?>\n<data>\n  <person>\n    <name>John Doe</name>\n    <age>30</age>\n  </person>\n</data>",
    "operation": "json_to_xml"
  }
}
```

---

## 16. Email Parser

**Endpoint:** `POST /function/email-parser`

**Request (Validate):**
```bash
curl -X POST http://localhost:8080/function/email-parser \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "validate",
    "email": "user@example.com"
  }'
```

**Request (Extract from text):**
```bash
curl -X POST http://localhost:8080/function/email-parser \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "extract",
    "text": "Contact us at support@example.com or sales@example.com for help"
  }'
```

**Request (Analyze):**
```bash
curl -X POST http://localhost:8080/function/email-parser \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "analyze",
    "email": "user+tag@gmail.com"
  }'
```

**Request (Batch Validate):**
```bash
curl -X POST http://localhost:8080/function/email-parser \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "batch_validate",
    "emails": ["valid@example.com", "invalid-email", "another@domain.org"]
  }'
```

**Parameters:**
- `operation` - `validate`, `parse`, `extract`, `analyze`, `batch_validate` (required)
- `email` - Email address (required for validate/analyze)
- `email_string` - Email with name (required for parse, e.g., "John Doe <john@example.com>")
- `text` - Text to extract emails from (required for extract)
- `emails` - Array of emails (required for batch_validate)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "email": "user+tag@gmail.com",
      "valid": true,
      "local_part": "user+tag",
      "domain": "gmail.com",
      "tld": "com",
      "is_disposable": false,
      "provider": "Google",
      "has_plus_sign": true
    }
  }
}
```

---

## 17. Data Encryption

**Endpoint:** `POST /function/data-encryption`

**Request (Generate Key):**
```bash
curl -X POST http://localhost:8080/function/data-encryption \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "generate_key",
    "key_id": "my_key"
  }'
```

**Request (Encrypt):**
```bash
curl -X POST http://localhost:8080/function/data-encryption \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "encrypt",
    "data": "Secret message to encrypt",
    "key_id": "my_key"
  }'
```

**Request (Decrypt):**
```bash
curl -X POST http://localhost:8080/function/data-encryption \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "decrypt",
    "data": "ENCRYPTED_DATA_FROM_ENCRYPT_RESPONSE",
    "key_id": "my_key"
  }'
```

**Parameters:**
- `operation` - `generate_key`, `encrypt`, `decrypt`, `hash`, `encrypt_dict`, `decrypt_dict` (required)
- `data` - String or dict data to encrypt/decrypt (required for encrypt/decrypt)
- `key_id` - Key identifier (optional, default: "default")
- `key` - Direct key (optional, overrides key_id)
- `password` - Password for key derivation (optional for generate_key)
- `algorithm` - Hash algorithm for hash operation (optional, default: "sha256")

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "encrypted_data": "Z0FCQUFBQUJHY...",
    "key_id": "my_key",
    "original_length": 25,
    "message": "Data encrypted successfully"
  }
}
```

---

## 18. CSV Processor

**Endpoint:** `POST /function/csv-processor`

**Request (Parse):**
```bash
curl -X POST http://localhost:8080/function/csv-processor \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "parse",
    "data": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago",
    "has_header": true,
    "delimiter": ","
  }'
```

**Request (Aggregate):**
```bash
curl -X POST http://localhost:8080/function/csv-processor \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "aggregate",
    "data": [
      {"category": "A", "value": 10},
      {"category": "B", "value": 20},
      {"category": "A", "value": 15}
    ],
    "group_by": "category",
    "aggregate_col": "value",
    "aggregate_op": "sum"
  }'
```

**Request (Statistics):**
```bash
curl -X POST http://localhost:8080/function/csv-processor \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "statistics",
    "data": [{"value": 10}, {"value": 20}, {"value": 30}, {"value": 40}],
    "column": "value"
  }'
```

**Parameters:**
- `operation` - `parse`, `generate`, `filter`, `aggregate`, `sort`, `statistics` (required)
- `data` - CSV string or array of objects (required)
- `has_header` - First row is header (optional, default: true)
- `delimiter` - CSV delimiter (optional, default: ",")
- `group_by` - Column to group by (required for aggregate)
- `aggregate_col` - Column to aggregate (required for aggregate)
- `aggregate_op` - sum, avg, count, min, max (optional, default: "sum")
- `sort_by` - Column to sort by (required for sort)
- `column` - Column for statistics (required for statistics)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "headers": ["name", "age", "city"],
      "data": [
        {"name": "John", "age": "30", "city": "New York"},
        {"name": "Jane", "age": "25", "city": "Los Angeles"}
      ],
      "row_count": 3,
      "column_count": 3
    }
  }
}
```

---

## 19. URL Shortener

**Endpoint:** `POST /function/url-shortener`

**Request (Shorten):**
```bash
curl -X POST http://localhost:8080/function/url-shortener \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "shorten",
    "url": "https://example.com/very/long/url/path/to/resource",
    "custom_code": "mylink"
  }'
```

**Request (Expand):**
```bash
curl -X POST http://localhost:8080/function/url-shortener \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "expand",
    "short_code": "mylink"
  }'
```

**Request (Batch Shorten):**
```bash
curl -X POST http://localhost:8080/function/url-shortener \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "batch_shorten",
    "urls": [
      "https://example.com/url1",
      "https://example.com/url2",
      "https://example.com/url3"
    ]
  }'
```

**Parameters:**
- `operation` - `shorten`, `expand`, `delete`, `batch_shorten`, `statistics` (required)
- `url` - URL to shorten (required for shorten)
- `short_code` - Short code (required for expand/delete)
- `custom_code` - Custom short code (optional for shorten)
- `urls` - Array of URLs (required for batch_shorten)

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "result": {
      "original_url": "https://example.com/very/long/url/path/to/resource",
      "short_code": "mylink",
      "shortened_url": "https://short.url/mylink",
      "existing": false
    }
  }
}
```

---

## 20. PDF Generator

**Endpoint:** `POST /function/pdf-generator`

**Request (Simple PDF):**
```bash
curl -X POST http://localhost:8080/function/pdf-generator \
  -H "Content-Type: application/json" \
  -d '{
    "type": "simple",
    "title": "My Document",
    "content": ["This is the first paragraph.", "This is the second paragraph.", "And this is the third paragraph."],
    "page_size": "letter"
  }'
```

**Request (Table PDF):**
```bash
curl -X POST http://localhost:8080/function/pdf-generator \
  -H "Content-Type: application/json" \
  -d '{
    "type": "table",
    "title": "Sales Report",
    "headers": ["Product", "Quantity", "Price"],
    "data": [
      ["Widget A", "10", "$100"],
      ["Widget B", "20", "$200"],
      ["Widget C", "15", "$150"]
    ],
    "page_size": "letter"
  }'
```

**Request (Report PDF):**
```bash
curl -X POST http://localhost:8080/function/pdf-generator \
  -H "Content-Type: application/json" \
  -d '{
    "type": "report",
    "title": "Quarterly Report",
    "sections": [
      {"heading": "Executive Summary", "content": "This is the executive summary of our quarterly performance."},
      {"heading": "Financial Results", "content": ["Revenue increased by 15%.", "Costs were reduced by 8%."], "page_break": true},
      {"heading": "Outlook", "content": "We expect continued growth in the next quarter."}
    ],
    "page_size": "A4"
  }'
```

**Parameters:**
- `type` - `simple`, `table`, `report` (required)
- `title` - Document title (optional)
- `content` - Text content or array of paragraphs (required for simple)
- `headers` - Column headers (required for table)
- `data` - Table rows as 2D array (required for table)
- `sections` - Array of sections with heading/content (required for report)
- `page_size` - `letter` or `A4` (optional, default: "letter")

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "pdf": "BASE64_ENCODED_PDF_DATA",
    "size_bytes": 4523,
    "page_size": "letter",
    "message": "PDF generated successfully"
  }
}
