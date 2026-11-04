# Exercise 1: Deploy and connect

**Time:** 20 minutes

Deploy this repo as it is, then connect your agent to it.
You write no code in this exercise.
The goal is to get the slow, one-time steps done first: signing in, giving FastMCP Gateway access to your fork, and the first build.

## Steps

1. Fork this repo to your GitHub account, then clone your fork:

   ```bash
   git clone https://github.com/<you>/motherduck-fastmcp-workshop
   cd motherduck-fastmcp-workshop
   uv sync
   ```

2. Sign in at [horizon.prefect.io](https://horizon.prefect.io).
   On first sign-in, create an organization.
   The free Personal plan has everything this workshop uses.

3. Select **New server**, then connect GitHub.
   When GitHub asks which repositories the FastMCP Gateway app can access, include your fork.
   If your fork is missing from the repository picker later, this access is the reason.

4. Pick your fork, then configure the server:

   | Setting | Value |
   | --- | --- |
   | Name | Anything unique. It becomes your URL: `https://<name>.fastmcp.app/mcp`. |
   | Entrypoint | `server.py:mcp` |
   | Dependency file | `pyproject.toml` |
   | FastMCP Gateway authentication | Leave it on. |

5. Wait for the first build.
   The **Deployments** page shows each step.
   When the status reads `Live`, copy the URL at the top of the page.

6. Connect Claude Code to your server and to the room server:

   ```bash
   claude mcp add --scope local --transport http sf-311 https://<name>.fastmcp.app/mcp
   claude mcp add --scope local --transport http room https://motherduck-control-center.fastmcp.app/mcp
   ```

   Start Claude Code in the repo folder and type `/mcp`.
   Select `sf-311` and sign in to FastMCP Gateway in the browser window that opens.
   The room server needs no sign-in.
   For Cursor or Claude Desktop, see [Connect another client](../README.md#connect-another-client).

7. Ask your agent:

   ```text
   What does the sf-311 server know about?
   ```

   It calls `dataset_info` and describes one week of San Francisco 311 requests.

8. Pick a handle: letters, digits, and dashes, 2 to 20 characters.
   Then ask:

   ```text
   Get my room challenge. My handle is <your-handle>.
   ```

   It returns the Exercise 2 challenge. Keep the question; you answer it in Exercise 2, and each later exercise has its own.

## Prove it

Open your server in FastMCP Gateway and select **Logs**.
You see a `tools/call` row for `dataset_info`.
Open it: the actor is you, because the gateway checked your sign-in before your code ran.

## If you get stuck

See [Troubleshooting](../README.md#troubleshooting).
The most common problems in this exercise are GitHub app access to the fork and the entrypoint setting.
