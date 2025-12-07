## The syslog file contents overview
```bash
╭─adilbb@p11 ~/PhD/repos/faas-compromised/data ‹main› 
╰─$ wc -l func_invc_absent/*/*csv
   9563 func_invc_absent/20251122_234455/100_logs_anomaly-detector-57f5b49565-xkxv7_syscalls.csv
   9314 func_invc_absent/20251122_234455/101_logs_sentiment-analyzer-65c4b88fb5-wzsdm_syscalls.csv
   9317 func_invc_absent/20251122_234455/102_logs_text-summarizer-7794c696d8-cgg2w_syscalls.csv
   9200 func_invc_absent/20251122_234455/103_logs_time-series-forecaster-58db55d69-n58zr_syscalls.csv
   8933 func_invc_absent/20251122_234455/104_logs_kmeans-clustering-6bd4d754cf-9qzv9_syscalls.csv
   8893 func_invc_absent/20251122_234455/105_logs_kmeans-clustering-code-type-6769648db9-clcs7_syscalls.csv
   8359 func_invc_absent/20251122_234455/106_logs_kmeans-clustering-command-type-6c47876955-5pmlm_syscalls.csv
   9065 func_invc_absent/20251122_234455/107_logs_kmeans-clustering-fileop-type-69b75d769-qkq2d_syscalls.csv
   9287 func_invc_absent/20251122_234455/108_logs_kmeans-clustering-info-type-c49dcc8cf-48pmg_syscalls.csv
  81931 total
╭─adilbb@p11 ~/PhD/repos/faas-compromised/data ‹main› 
╰─$ wc -l func_invc_present/*/*csv
   70201 func_invc_present/20251123_012402/100_logs_anomaly-detector-57f5b49565-xkxv7_syscalls.csv
   43228 func_invc_present/20251123_012402/101_logs_sentiment-analyzer-65c4b88fb5-wzsdm_syscalls.csv
   31805 func_invc_present/20251123_012402/102_logs_text-summarizer-7794c696d8-cgg2w_syscalls.csv
   36456 func_invc_present/20251123_012402/103_logs_time-series-forecaster-58db55d69-n58zr_syscalls.csv
  125200 func_invc_present/20251123_012402/104_logs_kmeans-clustering-6bd4d754cf-9qzv9_syscalls.csv
   94312 func_invc_present/20251123_012402/105_logs_kmeans-clustering-code-type-6769648db9-clcs7_syscalls.csv
  142038 func_invc_present/20251123_012402/106_logs_kmeans-clustering-command-type-6c47876955-5pmlm_syscalls.csv
  123625 func_invc_present/20251123_012402/107_logs_kmeans-clustering-fileop-type-69b75d769-qkq2d_syscalls.csv
  119055 func_invc_present/20251123_012402/108_logs_kmeans-clustering-info-type-c49dcc8cf-48pmg_syscalls.csv
  785920 total
╭─adilbb@p11 ~/PhD/repos/faas-compromised/data ‹main› 
╰─$ wc -l */*/*csv                
    9563 func_invc_absent/20251122_234455/100_logs_anomaly-detector-57f5b49565-xkxv7_syscalls.csv
    9314 func_invc_absent/20251122_234455/101_logs_sentiment-analyzer-65c4b88fb5-wzsdm_syscalls.csv
    9317 func_invc_absent/20251122_234455/102_logs_text-summarizer-7794c696d8-cgg2w_syscalls.csv
    9200 func_invc_absent/20251122_234455/103_logs_time-series-forecaster-58db55d69-n58zr_syscalls.csv
    8933 func_invc_absent/20251122_234455/104_logs_kmeans-clustering-6bd4d754cf-9qzv9_syscalls.csv
    8893 func_invc_absent/20251122_234455/105_logs_kmeans-clustering-code-type-6769648db9-clcs7_syscalls.csv
    8359 func_invc_absent/20251122_234455/106_logs_kmeans-clustering-command-type-6c47876955-5pmlm_syscalls.csv
    9065 func_invc_absent/20251122_234455/107_logs_kmeans-clustering-fileop-type-69b75d769-qkq2d_syscalls.csv
    9287 func_invc_absent/20251122_234455/108_logs_kmeans-clustering-info-type-c49dcc8cf-48pmg_syscalls.csv
   70201 func_invc_present/20251123_012402/100_logs_anomaly-detector-57f5b49565-xkxv7_syscalls.csv
   43228 func_invc_present/20251123_012402/101_logs_sentiment-analyzer-65c4b88fb5-wzsdm_syscalls.csv
   31805 func_invc_present/20251123_012402/102_logs_text-summarizer-7794c696d8-cgg2w_syscalls.csv
   36456 func_invc_present/20251123_012402/103_logs_time-series-forecaster-58db55d69-n58zr_syscalls.csv
  125200 func_invc_present/20251123_012402/104_logs_kmeans-clustering-6bd4d754cf-9qzv9_syscalls.csv
   94312 func_invc_present/20251123_012402/105_logs_kmeans-clustering-code-type-6769648db9-clcs7_syscalls.csv
  142038 func_invc_present/20251123_012402/106_logs_kmeans-clustering-command-type-6c47876955-5pmlm_syscalls.csv
  123625 func_invc_present/20251123_012402/107_logs_kmeans-clustering-fileop-type-69b75d769-qkq2d_syscalls.csv
  119055 func_invc_present/20251123_012402/108_logs_kmeans-clustering-info-type-c49dcc8cf-48pmg_syscalls.csv
  867851 total
```