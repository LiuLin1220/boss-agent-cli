"""MCP stdio 协议回归测试。"""

import json
import subprocess
import sys


def test_tools_list_is_registered_over_stdio() -> None:
	messages = [
		{
			"jsonrpc": "2.0",
			"id": 1,
			"method": "initialize",
			"params": {
				"protocolVersion": "2024-11-05",
				"capabilities": {},
				"clientInfo": {"name": "pytest", "version": "1.0"},
			},
		},
		{"jsonrpc": "2.0", "method": "notifications/initialized"},
		{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
	]
	request_stream = "".join(json.dumps(message, separators=(",", ":")) + "\n" for message in messages)

	result = subprocess.run(
		[sys.executable, "-m", "boss_agent_cli.mcp_server"],
		input=request_stream,
		capture_output=True,
		text=True,
		encoding="utf-8",
		timeout=10,
	)

	assert result.returncode == 0, result.stderr
	responses = {response["id"]: response for line in result.stdout.splitlines() if (response := json.loads(line))}
	assert responses[1]["result"]["serverInfo"]["name"] == "boss-agent-cli"

	list_response = responses[2]
	assert "error" not in list_response, list_response
	tools = list_response["result"]["tools"]
	assert tools
	assert "boss_status" in {tool["name"] for tool in tools}
