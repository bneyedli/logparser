PROJECT_NAME=logparser
COMMIT_HASH=$(shell git rev-parse --short HEAD)
IMAGE_TAG=$(COMMIT_HASH)
IMAGE_NAME=$(PROJECT_NAME):$(IMAGE_TAG)
WORK_DIR=$(PWD)
CONTAINER_LOG_DIR=/mnt/logs
HOST_LOG_DIR=$(WORK_DIR)/logs
CONTAINER_LOG_FILE=access.log
LISTEN_IP=0.0.0.0
LISTEN_PORT=3000
SOURCE_CONTAINER_TAG=3.9-slim-buster

$(HOST_LOG_DIR):
	@mkdir -p

build:
	@echo "Building container: $(IMAGE_NAME) Listen port: $(LISTEN_PORT) Log file: $(CONTAINER_LOG_DIR)/$(CONTAINER_LOG_FILE)"
	@docker build . --build-arg SOURCE_CONTAINER_TAG=$(SOURCE_CONTAINER_TAG) --build-arg LOG_DIR=$(CONTAINER_LOG_DIR)/$(CONTAINER_LOG_FILE) --build-arg LISTEN_PORT=$(LISTEN_PORT) -t $(IMAGE_NAME)
run: $(HOST_LOG_DIR)
	@echo "Running container: $(IMAGE_NAME) Listen IP: $(LISTEN_IP) Log source: $(HOST_LOG_DIR)"
	@docker run -it --mount type=bind,source="$(HOST_LOG_DIR)",target=$(CONTAINER_LOG_DIR) \
		--env "LISTEN_IP=$(LISTEN_IP)" \
		--env "LISTEN_PORT=$(LISTEN_PORT)" \
		--env "LOG_FILE=$(CONTAINER_LOG_DIR)/$(CONTAINER_LOG_FILE)" \
		--expose $(LISTEN_PORT) $(IMAGE_NAME)

inspect:
	@docker inspect $(IMAGE_NAME) | jq .
