# Claude-Code MCP Controller - Essential Commands

.PHONY: help setup run-supervisor run-server test clean format lint ngrok kill

help: ## Show available commands
	@echo "Essential Commands:"
	@echo "  make setup         - Complete project setup"
	@echo "  make run-supervisor - Start supervisor"
	@echo "  make run-server    - Start MCP server"
	@echo "  make ngrok         - Start ngrok tunnel for ChatGPT"
	@echo "  make test          - Test the system"
	@echo "  make kill          - Kill running processes"
	@echo "  make format        - Format code"
	@echo "  make lint          - Lint code"
	@echo "  make clean         - Clean up files"

setup: ## Complete project setup
	@echo "Setting up project..."
	python3 -m venv .venv --without-pip || python3 -m venv .venv --clear
	.venv/bin/python -m ensurepip --upgrade --default-pip || \
		curl https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Setup complete! Run 'make run-supervisor' and 'make run-server'"

run-supervisor: ## Start the supervisor server
	.venv/bin/python -m supervisor.main

run-server: ## Start the MCP server
	.venv/bin/python start_mcp_server.py

ngrok: ## Start ngrok tunnel for ChatGPT
	ngrok http $(shell python3 -c "from config import config; print(config.NGROK_PORT)")

test: ## Test the system (basic health check)
	@echo "Testing supervisor health..."
	@curl -f http://localhost:8080/health 2>/dev/null && echo "✅ Supervisor is healthy" || echo "❌ Supervisor not running (start with 'make run-supervisor')"

kill: ## Kill running processes
	@echo "🛑 Killing running processes..."
	@pkill -f "python.*supervisor" || true
	@pkill -f "python.*start_mcp_server" || true
	@pkill -f "ngrok" || true
	@echo "✅ Processes killed"

format: ## Format code
	.venv/bin/python -m black .

lint: ## Lint code
	.venv/bin/python -m mypy .

clean: ## Clean up files
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .venv/
