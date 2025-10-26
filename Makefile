run-agent-console:
	uv run python src/agent.py console

run-agent-dev:
	uv run python src/agent.py dev

get-files:
	uv run python src/agent.py download-files
