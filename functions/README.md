# About
This guide is for creating custom functions using faas-cli tool and deply in openfaas platform. We are using openfaas CE version, which has some limitations. Due to one of those limitation we need to hame the OCI images of the functions publicly available. Here we are using GHCR to publicly host these images publicly and use them during building, pushing, and deploying phases. 

## Important
The commands below assume that Docker config is configured for accessing the GHCR with a PAT token. After creating the function using the `faas-cli new` command, we replace the image URI with a valid GHCR URI. It's also important that the image is publicly accessible. It can be done through github UI. I haven't explored any CLI ways. Thus the first time `faas-cli up` command will fail in its default form as after the pushing the image to GHCR it won't be publicly accessible. But after pushing the image first time, the second attempt will work just fine.

## Some important command sequences
### How to set up faas-cli and basic usage
```bash
$ faas-cli login -u admin --password ssbkqU3MZZQg
$ faas-cli list
$ faas-cli logs curl
$ faas-cli remove curl
# only to pull the templates, doesn't need to run every time.
$ faas-cli template pull
```
### How to create custom function and deploy them
```bash
# after this make function template can be modified to obtain a desired function. Here a random integer generator funciton is taken for example. This creates the necessary files and stack.yaml, for custom naming of yaml file use the second command.
$ faas-cli new randints --lang python3-http-debian
$ faas-cli new randints --lang python3-http-debian --yaml randints.yaml
# It's also importatnt that we add the packages in requirement file, otherwise build will fail in subsequent steps.
$ faas-cli build -f randints.yaml
$ faas-cli deploy -f randints.yaml
$ faas-cli publish -f randints.yaml
# up does all the build, deploy, and publish work.
$ faas-cli up -f randints.yaml
```
### How to get info about a function and invoke using CLI
```bash
$ faas-cli describe randints
# after invoking press ctrl+d to send the request and expect a response.
$ faas-cli invoke randints
```

## Mock a server
This is required for executing compromised functions. Most of the compromised functions try to communicate to a remote server. For security reasons its better to mock a local server and communicate with it. This is one of the way to do it using nginx.
```bash
docker run -d -p 80:80 --name mock-server nginx:alpine sh -c \
  'echo "server { listen 80 default_server; server_name _; location / { return 200 \"OK\\\n\"; add_header Content-Type text/plain; } }" > /etc/nginx/conf.d/default.conf && nginx -g "daemon off;"'

```

### How to locally run a function
This helpful for quick debugging and faster development. It's important to note that if the yaml if file other than stack.yaml, the `-f` must be used.
```bash
$ faas-cli local-run randints -f ./randints.yaml
```

### Some tips
1. Some functions using libraries for machine learning tasks like numpy and scikit-learn, python3-http gives error. In this case use fo python3-http-debian solved the error.