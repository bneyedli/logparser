# Logparser
Simple python service to process and output apache log analysis in json

# Minimum Requirements
* Local directory with apache style logs (examples have not been included)
* Docker
* Developed with python [poetry](https://python-poetry.org/), [pre-commit](https://pre-commit.com) and local [hooks](https://github.com/bneyedli/pre-commit-hook)

## Usage -- standalone
```
./src/logparser/parser.py -h                                                                                                                                                                                                                                                                                  ✔  1.05 L  1s ─╯
usage: parser.py [-h] [--logfile LOGFILE] [--ip IP] [--port PORT]

Process and evaluate access logs.

options:
  -h, --help         show this help message and exit
  --logfile LOGFILE  Absolute path to logs
  --ip IP            Host IP to listen on, default *all*
  --port PORT        Host Port to listen on, default 3000
```
Example: Process log ./logs/foo.log listen on all available interfaces on port 9090
```
./src/logparser/parser.py --logfile ./logs/foo.log --ip 0.0.0.0 --port 9090
```
## Usage -- Docker
Build and run container all in one
```
make build run CONTAINER_LOG_FILE=access_log_20190520-125058.log LISTEN_IP=0.0.0.0 LISTEN_PORT=9119   
```
Run existing container
```
make run CONTAINER_LOG_FILE=access_log_20190520-125058.log LISTEN_IP=0.0.0.0 LISTEN_PORT=2000  
```
