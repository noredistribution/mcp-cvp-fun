# MCP Server Demo with Arista CloudVision

> [!WARNING]
> Please note that this is not officially supported by Arista.
>
> You might not want to do this in your production environment as it is not using a local LLM.
>
> The free plan of Claude might cause anxiety!

Kudos to [@burnyd](https://github.com/burnyd) for the inspiriation and for writing this blog post: [https://danielhertzberg.net/posts/mcp-servers/](https://danielhertzberg.net/posts/mcp-servers/)

Expanding on that, I've added a few more API calls to be able to ask Claude to get connectivity monitor data, and create tags for Studios and dashboards, but obviously any API call can be added very easy with the `@mcp.tool()` decorator.

To learn more about MCP please visit [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction).

## Example usage

1\. Create a .env file like the following.

```bash
CVPTOKEN="Insert CloudVision Service account token here"
CVP="www.arista.io"
```

2\. Download [Claude Desktop](https://claude.ai/download)

3\. In Claude's developer settings update the claude_desktop_config.json and tell it to run your script like below:

```json
{
  "mcpServers": {
    "CVP MCP Server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "/home/ansible/mcp-cvp-fun/mcp_server_rest.py"
      ]
    }
  }
}
```

4\. Reload Claude and start prompting

![creattag](./media/createtag.png)

## How to generate service account tokens

Service accounts can be created from the Settings page where a service token can be generated as seen below:

![serviceaccount1](./media/serviceaccount1.png)
![serviceaccount2](./media/serviceaccount2.png)
![serviceaccount3](./media/serviceaccount3.png)
