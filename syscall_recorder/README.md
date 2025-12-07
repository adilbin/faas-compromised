# About
We are using [traceloop](https://inspektor-gadget.io/docs/latest/gadgets/traceloop) from [inspektor-gadget](https://github.com/inspektor-gadget/inspektor-gadget) collection to record syscalls. 

This uses a [custom traceloop build](https://github.com/binbhutto/traceloop-modified) with more memory space to record more syscalls.


## Record syscalls using the following scripts.
Make sure run the scripts from root of the repository for the relative file paths to work properly.
```bash
# run this from root of the repo
$ ./syscall_recorder/record.sh
```

## How to check the version of the `gadget` installed
```bash
$ kubectl-gadget version 
``` 

## Trigger utility and compromised functions
For controlled experiments [record_with_func_invc.sh](./record_with_func_invc.sh) script can be executed. These are the ways to trigger functions. 
### Trigger utility functions
```bash
# Text summarizer utility function trigger
curl -X POST http://localhost:8080/function/text-summarizer \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial intelligence is transforming the technology landscape. Machine learning algorithms can now process vast amounts of data. Deep learning has revolutionized computer vision and natural language processing. Companies are investing heavily in AI research and development. The future of AI looks promising with many exciting applications ahead.",
    "num_sentences": 2,
    "method": "tfidf"
  }'

# Anomaly detection utility function trigger
curl -X POST http://localhost:8080/function/anomaly-detector \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1.2, 3.4], [2.1, 3.5], [100, 200]],
    "train": true,
    "contamination": 0.1
  }'

# Sentiment analyzier utility function trigger
curl -X POST http://localhost:8080/function/sentiment-analyzer \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product is amazing! I love it."
  }'

# Time series forecaster utility function trigger
curl -X POST http://localhost:8080/function/time-series-forecaster \
  -H "Content-Type: application/json" \
  -d '{
    "series": [10, 12, 15, 14, 18, 21, 23, 25],
    "forecast_steps": 5,
    "degree": 1
  }'

# K-means clustering utility function trigger
curl -X POST http://localhost:8080/function/kmeans-clustering \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
    "n_clusters": 2,
    "operation": "fit_predict"
  }'
```
### Trigger compromised functions (For now four type of compromised functions of same k-means variants are introduce.)
```bash
# K-means clustering compromised by information stealing function trigger 
curl -X POST http://localhost:8080/function/kmeans-clustering-info-type \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
    "n_clusters": 2,
    "operation": "fit_predict"
  }'

# K-means clustering compromised by malicious code execution function trigger 
curl -X POST http://localhost:8080/function/kmeans-clustering-code-type \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
    "n_clusters": 2,
    "operation": "fit_predict"
  }'

# K-means clustering compromised by malicious command execution function trigger 
curl -X POST http://localhost:8080/function/kmeans-clustering-command-type \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
    "n_clusters": 2,
    "operation": "fit_predict"
  }'

# K-means clustering compromised by malicious file operation function trigger 
curl -X POST http://localhost:8080/function/kmeans-clustering-fileop-type \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6]],
    "n_clusters": 2,
    "operation": "fit_predict"
  }'
```

## Some results after recording the syscalls in presence and absence of function calls.
```bash
# Syscalls for functions in idle state only system health checks are run (absense)
    9356 func_invc_absent/20251117_202203/logs_anomaly-detector-57f5b49565-jpkmw.log
    9816 func_invc_absent/20251117_202203/logs_image-classifier-7cdcc8c87-xlh5t.log
    9447 func_invc_absent/20251117_202203/logs_kmeans-clustering-6bd4d754cf-6nj5p.log
    9210 func_invc_absent/20251117_202203/logs_kmeans-clustering-code-type-6769648db9-5qv87.log
    9584 func_invc_absent/20251117_202203/logs_kmeans-clustering-command-type-6c47876955-2c97l.log
    9572 func_invc_absent/20251117_202203/logs_kmeans-clustering-fileop-type-69b75d769-kbx5z.log
    9559 func_invc_absent/20251117_202203/logs_kmeans-clustering-info-type-c49dcc8cf-rgq2t.log
   10628 func_invc_absent/20251117_202203/logs_sentiment-analyzer-65c4b88fb5-rtbsg.log
    9211 func_invc_absent/20251117_202203/logs_time-series-forecaster-58db55d69-gbjbv.log
   86383 total

# Systecalls for functions in presence of calls every 2 seconds (present)
    70003 func_invc_present/20251118_062728/logs_anomaly-detector-57f5b49565-jpkmw.log
   119739 func_invc_present/20251118_062728/logs_kmeans-clustering-6bd4d754cf-6nj5p.log
   114984 func_invc_present/20251118_062728/logs_kmeans-clustering-code-type-6769648db9-5qv87.log
   103304 func_invc_present/20251118_062728/logs_kmeans-clustering-command-type-6c47876955-2c97l.log
   115505 func_invc_present/20251118_062728/logs_kmeans-clustering-fileop-type-69b75d769-kbx5z.log
   120441 func_invc_present/20251118_062728/logs_kmeans-clustering-info-type-c49dcc8cf-rgq2t.log
   105776 func_invc_present/20251118_062728/logs_sentiment-analyzer-65c4b88fb5-rtbsg.log
    32458 func_invc_present/20251118_062728/logs_text-summarizer-64b857ff6f-ct46c.log
    37378 func_invc_present/20251118_062728/logs_time-series-forecaster-58db55d69-gbjbv.log
   819588 total

```