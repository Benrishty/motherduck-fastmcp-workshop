# Give your agents the tools it needs with FastMCP

A hands-on workshop from Prefect at MotherDuck Data Outpost, November 4, 2026.

You build an MCP server over a week of San Francisco 311 data with [FastMCP](https://gofastmcp.com), and run it on FastMCP Gateway.
Your coding agent writes the code.
You decide what the tools are, check what they return, and watch every call your agent makes.

By the end you have a hosted MCP server that:

- answers questions about the data in a few tool calls,
- runs behind authentication with no auth code,
- never sends a street address to the model,
- records every call, and
- can stop and ask you a question in the middle of a tool call.

## Before the workshop

Do these steps ahead of time if you can.
They take about ten minutes, and the room wifi will thank you.

1. Have a GitHub account.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
3. Install [Claude Code](https://code.claude.com/docs/en/quickstart), the recommended client.
   Cursor and Claude Desktop work for most of the workshop.
   Elicitation in Exercise 4 is only verified in Claude Code.
4. Fork this repo, clone your fork, and run `uv sync`.
5. Sign in once at [horizon.prefect.io](https://horizon.prefect.io) and create an organization.
   The free Personal plan has everything this workshop uses.

## Exercises

| # | Exercise | Time | You finish with |
| --- | --- | --- | --- |
| 1 | [Deploy and connect](exercises/01-deploy-and-connect.md) | 20 min | Your server live at its own URL, and your room challenge. |
| 2 | [Build tools for your agent](exercises/02-build-tools.md) | 20 min | Tools that answer the Exercise 2 room challenge, and your handle on the room screen. |
| 3 | [Mask and observe](exercises/03-mask-and-observe.md) | 20 min | Masked addresses, a caller in every log line, payload logging turned off, and a tool of your own design for the Exercise 3 challenge. |
| 4 | [Ask with elicitation](exercises/04-ask-with-elicitation.md) | 15 min | A tool that asks which neighborhood you mean, and the Exercise 4 challenge. |

Each exercise is a brief for your coding agent, plus a check you do yourself in FastMCP Gateway.
The tests in `tests/` decide when an exercise is done. You never write tests.
If you fall behind, each exercise shows how to copy its solution from `solutions/` and keep going.

## How the repo is laid out

| Path | What it is |
| --- | --- |
| `server.py` | Your MCP server. FastMCP Gateway runs it with the entrypoint `server.py:mcp`. |
| `sf311/data.py` | Loads the 311 snapshot. See [data/README.md](data/README.md) for the columns and license. |
| `sf311/kit.py` | Helpers for running on FastMCP Gateway: the verified caller, and asking the user a question. |
| `AGENTS.md` | Rules for your coding agent. Claude Code reads it through `CLAUDE.md`. |
| `exercises/` | The four briefs. |
| `tests/` | The acceptance tests for each exercise. |
| `solutions/` | A finished server for each exercise. |

To run the tests for one exercise:

```bash
uv run pytest tests/test_ex2.py
```

## Connect another client

FastMCP Gateway writes the configuration for you.
Open your server, select **Connect**, and pick your client.

| Client | Your server | Room server |
| --- | --- | --- |
| Claude Code | `claude mcp add --scope local --transport http sf-311 <your URL>`, then `/mcp` to sign in. | `claude mcp add --scope local --transport http room https://motherduck-control-center.fastmcp.app/mcp` |
| Cursor | Use the `cursor://` link in the **Connect** dialog. | Add `{"mcpServers": {"room": {"url": "https://motherduck-control-center.fastmcp.app/mcp"}}}` to `~/.cursor/mcp.json`. |
| Claude Desktop | Select **Add to Claude Desktop** in the **Connect** dialog, and open the downloaded `.mcpb` file. Desktop asks you to allow each tool call; choose **Always allow** for your server. | In **Settings**, then **Developer**, then **Edit Config**, add the room server with `"url"` and `"transport": "http"`, then restart Claude Desktop. |

The room server needs no sign-in.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Your fork is missing from the repository picker. | The FastMCP Gateway GitHub app has no access to it. | In GitHub, open **Settings**, then **Applications**, configure the FastMCP Gateway app, and add your fork. |
| The build fails at the entrypoint step. | The entrypoint setting is wrong. | Set it to `server.py:mcp` in the server's settings, then redeploy. |
| The build fails while installing dependencies. | A dependency was added that does not install. | Check the build log. Remove the dependency; this workshop needs only `fastmcp`. |
| Claude Code says the server needs authentication, or calls return `401`. | You have not signed in for this server. | Type `/mcp`, select `sf-311`, and sign in. |
| A call returns `404`. | The URL is wrong, or the first build is not `Live` yet. | Copy the URL from the **Deployments** page and wait for `Live`. |
| New tools do not appear after a push. | The client cached the old tool list, or the new build is not live yet. | Wait for `Live`, then reconnect with `/mcp`. |
| Tests pass locally, but the deployed tool fails. | The code depends on something only on your laptop. | Open **Server logs** on the **Deployments** page for the error. |
| No form appears in Exercise 4. | Claude Desktop declines forms automatically, and Cursor may too; or the tool calls `ctx.elicit()`. | Claude Desktop works around it on its own by passing `boundary`. Otherwise use Claude Code, or tell the agent to pass `boundary`. Run `tests/test_ex4.py`, which catches `ctx.elicit()`. |
| The first call after a deploy is slow. | The new deployment is starting. | Wait a few seconds and try again. |

## After the workshop

Everything here works on your own time.
The room server stays up for a while after the event; without it, skip the room challenge steps.

## Credits

Data: [DataSF 311 Cases](https://data.sf.gov/d/vw6y-z8j6), City and County of San Francisco, under the Open Data Commons PDDL.
