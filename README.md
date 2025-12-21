# How to prepare the environment
Run the [system_bootstrap.bash](./system_bootstrap.bash) script to install all the required libraries and softwares. The script is dabian compatible and tested for Ubuntu 24.04 LTS.
# Important
```bash
# how to start the port forwarding for the openfaas UI
$ kubectl port-forward -n openfaas svc/gateway 8080:8080 
# default username for the openfaas UI is admin and the password can be retrieved using
$ echo $(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
```
## Some important links for scientific compromised functions repositories
1. https://github.com/datadog/malicious-software-packages-dataset
1. https://dasfreak.github.io/Backstabbers-Knife-Collection/
1. https://github.com/lxyeternal/pypi_malregistry
1. https://github.com/advisories?query=type:reviewed+ecosystem:pip
1. This list of attacks can be used in combination with various AI functions to build the detection method.
    1. https://sites.google.com/view/pypiempircal

# Known bug
https://github.com/inspektor-gadget/inspektor-gadget/issues/4878




## Buffer text
============================================================
EXPERIMENT: Window Size = 250 syscalls
============================================================
Train samples: 1986, Test samples: 810
Sequence length (max tokens): 3250
Model parameters: 8,718,210

Training...
Epoch 1/6: 100%|██████████| 63/63 [1:01:11<00:00, 58.27s/it, loss=0.0126, acc=0.8263]
Epoch 2/6: 100%|██████████| 63/63 [1:01:08<00:00, 58.23s/it, loss=0.0010, acc=0.9894]
Epoch 3/6: 100%|██████████| 63/63 [1:01:07<00:00, 58.22s/it, loss=0.0005, acc=0.9945]
Epoch 4/6: 100%|██████████| 63/63 [1:01:10<00:00, 58.26s/it, loss=0.0003, acc=0.9960]
Epoch 5/6: 100%|██████████| 63/63 [1:01:08<00:00, 58.23s/it, loss=0.0003, acc=0.9965]
Epoch 6/6: 100%|██████████| 63/63 [1:01:08<00:00, 58.22s/it, loss=0.0002, acc=0.9990]
Training time: 22014.62s

Evaluating...
Test time: 87.28s

Classification Report:
              precision    recall  f1-score   support

      benign       0.91      0.82      0.86       489
   malicious       0.76      0.88      0.82       321

    accuracy                           0.84       810
   macro avg       0.84      0.85      0.84       810
weighted avg       0.85      0.84      0.84       810

Confusion Matrix:
                 Pred: benign  Pred: malicious
True: benign              400               89
True: malicious            38              283

Detection Rate: 0.8816
False Positive Rate: 0.1820
F1-score (weighted): 0.8447

============================================================
...
Sequence length (max tokens): 6500
Model parameters: 8,926,210

Training...