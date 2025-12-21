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
    9563 func_invc_absent/processed_data/001_AF_logs_anomaly-detector-57f5b49565-xkxv7_syscalls.csv
    8851 func_invc_absent/processed_data/002_AF_logs_decisiontree-classifier-77bff97c75-9l4wz_syscalls.csv
    8933 func_invc_absent/processed_data/003_AF_logs_kmeans-clustering-6bd4d754cf-9qzv9_syscalls.csv
    8850 func_invc_absent/processed_data/004_AF_logs_linear-regression-6f8dcf8c4f-x2xhb_syscalls.csv
    9221 func_invc_absent/processed_data/005_AF_logs_naivebayes-classifier-74db446485-m8xln_syscalls.csv
    8955 func_invc_absent/processed_data/006_AF_logs_pcadimensionality-reduction-77d84d8dfc-gsntj_syscalls.csv
    9314 func_invc_absent/processed_data/007_AF_logs_sentiment-analyzer-65c4b88fb5-wzsdm_syscalls.csv
    9317 func_invc_absent/processed_data/008_AF_logs_text-summarizer-7794c696d8-cgg2w_syscalls.csv
    9200 func_invc_absent/processed_data/009_AF_logs_time-series-forecaster-58db55d69-n58zr_syscalls.csv
    8792 func_invc_absent/processed_data/010_AF_logs_topic-modeling-6db6688f99-ggdch_syscalls.csv
    9337 func_invc_absent/processed_data/011_NF_logs_noai-csv-processor-58fbfc9f99-qxsfg_syscalls.csv
    9083 func_invc_absent/processed_data/012_NF_logs_noai-data-encrypter-7ff77dcb85-g5vj7_syscalls.csv
    8660 func_invc_absent/processed_data/013_NF_logs_noai-data-validator-654c4c7f49-m4bvc_syscalls.csv
    8657 func_invc_absent/processed_data/014_NF_logs_noai-email-parser-59968f499-x96p4_syscalls.csv
    8231 func_invc_absent/processed_data/015_NF_logs_noai-hash-generator-cb8b5cccf-lpmfz_syscalls.csv
    9009 func_invc_absent/processed_data/016_NF_logs_noai-image-generator-77d9f79f5f-8kfcb_syscalls.csv
    8452 func_invc_absent/processed_data/017_NF_logs_noai-jsonxml-converter-6b8b55b97c-gx4sj_syscalls.csv
    9168 func_invc_absent/processed_data/018_NF_logs_noai-pdf-generator-7bb87c4949-dmcbv_syscalls.csv
    8812 func_invc_absent/processed_data/019_NF_logs_noai-qrcode-generator-6f864dfcf-cdjxg_syscalls.csv
    9081 func_invc_absent/processed_data/020_NF_logs_noai-url-shortner-7df55cf949-r8zjz_syscalls.csv
    8750 func_invc_absent/processed_data/021_CF_logs_decisiontree-classifier-fileop-type-ccfb85f7c-wmjgk_syscalls.csv
   10545 func_invc_absent/processed_data/022_CF_logs_decisiontree-classifier-info-type-7cb8dd8455-pw9gp_syscalls.csv
    8893 func_invc_absent/processed_data/023_CF_logs_kmeans-clustering-code-type-6769648db9-clcs7_syscalls.csv
    8359 func_invc_absent/processed_data/024_CF_logs_kmeans-clustering-command-type-6c47876955-5pmlm_syscalls.csv
    9065 func_invc_absent/processed_data/025_CF_logs_kmeans-clustering-fileop-type-69b75d769-qkq2d_syscalls.csv
    9287 func_invc_absent/processed_data/026_CF_logs_kmeans-clustering-info-type-c49dcc8cf-48pmg_syscalls.csv
    9104 func_invc_absent/processed_data/027_CF_logs_time-series-forecaster-code-type-86bf484679-5xrpn_syscalls.csv
    9571 func_invc_absent/processed_data/028_CF_logs_time-series-forecaster-command-type-7fc84cfccc-5qbdn_syscalls.csv
    8530 func_invc_absent/processed_data/029_CF_logs_time-series-forecaster-fileop-type-7b99894dc-g2wmr_syscalls.csv
    8940 func_invc_absent/processed_data/030_CF_logs_time-series-forecaster-info-type-5cb6b94c85-mgtt2_syscalls.csv
  270530 total

# Systecalls for functions in presence of calls every 2 seconds (present)
    70201 func_invc_present/processed_data/001_AF_logs_anomaly-detector-57f5b49565-xkxv7_syscalls.csv
    33140 func_invc_present/processed_data/002_AF_logs_decisiontree-classifier-77bff97c75-9l4wz_syscalls.csv
   125200 func_invc_present/processed_data/003_AF_logs_kmeans-clustering-6bd4d754cf-9qzv9_syscalls.csv
    33822 func_invc_present/processed_data/004_AF_logs_linear-regression-6f8dcf8c4f-x2xhb_syscalls.csv
    34533 func_invc_present/processed_data/005_AF_logs_naivebayes-classifier-74db446485-m8xln_syscalls.csv
    33879 func_invc_present/processed_data/006_AF_logs_pcadimensionality-reduction-77d84d8dfc-gsntj_syscalls.csv
    43228 func_invc_present/processed_data/007_AF_logs_sentiment-analyzer-65c4b88fb5-wzsdm_syscalls.csv
    31805 func_invc_present/processed_data/008_AF_logs_text-summarizer-7794c696d8-cgg2w_syscalls.csv
    36456 func_invc_present/processed_data/009_AF_logs_time-series-forecaster-58db55d69-n58zr_syscalls.csv
    33674 func_invc_present/processed_data/010_AF_logs_topic-modeling-6db6688f99-ggdch_syscalls.csv
    34274 func_invc_present/processed_data/011_NF_logs_noai-csv-processor-58fbfc9f99-qxsfg_syscalls.csv
    32351 func_invc_present/processed_data/012_NF_logs_noai-data-encrypter-7ff77dcb85-g5vj7_syscalls.csv
    33131 func_invc_present/processed_data/013_NF_logs_noai-data-validator-654c4c7f49-m4bvc_syscalls.csv
    33040 func_invc_present/processed_data/014_NF_logs_noai-email-parser-59968f499-x96p4_syscalls.csv
    32988 func_invc_present/processed_data/015_NF_logs_noai-hash-generator-cb8b5cccf-lpmfz_syscalls.csv
    34323 func_invc_present/processed_data/016_NF_logs_noai-image-generator-77d9f79f5f-8kfcb_syscalls.csv
    32909 func_invc_present/processed_data/017_NF_logs_noai-jsonxml-converter-6b8b55b97c-gx4sj_syscalls.csv
    33586 func_invc_present/processed_data/018_NF_logs_noai-pdf-generator-7bb87c4949-dmcbv_syscalls.csv
    34100 func_invc_present/processed_data/019_NF_logs_noai-qrcode-generator-6f864dfcf-cdjxg_syscalls.csv
    32903 func_invc_present/processed_data/020_NF_logs_noai-url-shortner-7df55cf949-r8zjz_syscalls.csv
    70655 func_invc_present/processed_data/021_CF_logs_decisiontree-classifier-fileop-type-ccfb85f7c-wmjgk_syscalls.csv
    40058 func_invc_present/processed_data/022_CF_logs_decisiontree-classifier-info-type-7cb8dd8455-pw9gp_syscalls.csv
    94312 func_invc_present/processed_data/023_CF_logs_kmeans-clustering-code-type-6769648db9-clcs7_syscalls.csv
   142038 func_invc_present/processed_data/024_CF_logs_kmeans-clustering-command-type-6c47876955-5pmlm_syscalls.csv
   123625 func_invc_present/processed_data/025_CF_logs_kmeans-clustering-fileop-type-69b75d769-qkq2d_syscalls.csv
   119055 func_invc_present/processed_data/026_CF_logs_kmeans-clustering-info-type-c49dcc8cf-48pmg_syscalls.csv
    45484 func_invc_present/processed_data/027_CF_logs_time-series-forecaster-code-type-86bf484679-5xrpn_syscalls.csv
   118068 func_invc_present/processed_data/028_CF_logs_time-series-forecaster-command-type-7fc84cfccc-5qbdn_syscalls.csv
    75312 func_invc_present/processed_data/029_CF_logs_time-series-forecaster-fileop-type-7b99894dc-g2wmr_syscalls.csv
    41615 func_invc_present/processed_data/030_CF_logs_time-series-forecaster-info-type-5cb6b94c85-mgtt2_syscalls.csv
  1679765 total

```