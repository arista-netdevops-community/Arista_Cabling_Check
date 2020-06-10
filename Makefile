DOCKER_NAME ?= arista_check
DOCKER_TAG ?= latest
PORT ?= 8181
CONTAINER_NAME ?= arista_check
DATA ?= visuapp/static/data
HOME_DIR = $(shell pwd)

.PHONY: help
help: ## Display help message
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build docker image
	docker build -t$(DOCKER_NAME):$(DOCKER_TAG) .

.PHONY: run
run: ## run docker image in foreground
	docker run --rm -p $(PORT):80/tcp $(DOCKER_NAME):$(DOCKER_TAG)

.PHONY: daemon
daemon: ## run docker image in background
	docker run -d --rm -p $(PORT):80/tcp -v $(HOME_DIR)/$(DATA):/projects/visuapp/static/data --name $(CONTAINER_NAME) $(DOCKER_NAME):$(DOCKER_TAG)

.PHONY: stop
stop: ## stop docker image
	docker stop $(CONTAINER_NAME)

.PHONY: connect
connect: ## connect to docker image for debug purpose
	docker exec -it $(CONTAINER_NAME) bash