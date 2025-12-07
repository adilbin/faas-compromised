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