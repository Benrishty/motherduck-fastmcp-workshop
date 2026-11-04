# Exercise 3: Mask and observe

**Time:** 15 minutes

## The brief

Street addresses never reach the model, and every lookup records who asked.
Then make sure FastMCP Gateway stops storing what your tools return.

Each 311 request has the street address of the problem.
The DataSF terms forbid using this data to identify people, and a model does not need a house number to answer questions about a neighborhood.

## Rules

- `search_requests` and `get_request` return addresses only to the block: `994 HARRISON ST, SAN FRANCISCO, CA 94107, US` becomes `900 block of HARRISON ST`.
  An address with no house number, such as an intersection, stays as it is.
- `get_request` logs one line that includes the caller's email, read with `caller_email()` from `sf311.kit`.
  Locally there is no caller, so log `local`.

## Steps

1. Ask your coding agent:

   ```text
   Read exercises/03-mask-and-observe.md and make the changes. Run tests/test_ex3.py until it passes, and keep tests/test_ex2.py passing.
   ```

2. Commit and push, then wait for `Live`.

## Prove it

1. Ask your agent: `Show me three recent encampment reports, then get the details of the first one.`
   The addresses end at the block.
2. Open **Logs** and select the `get_request` row.
   The response payload shows the masked address.
   The actor is you.
3. Open the deployment's **Server logs** from the **Deployments** page.
   You see your log line with your email.
   That email came from the gateway, which verified your sign-in and set the header before your code ran.
4. In your server's **Settings**, open **General**, find **Data Controls**, and turn off **Log MCP Responses**.
   This setting applies to every tool on the server.
5. Ask for another request's details, then open the new `get_request` row in **Logs**.
   The row is there, but its response payload is not stored.

## The Exercise 3 challenge

This one is the design exercise.
Ask for it:

```text
Get my Exercise 3 room challenge. My handle is <your-handle>.
```

The question cannot be answered by the four tools from Exercise 2: which hour of the day had the most requests, how many are still open, the longest time any request took to close, which service has the widest gap between its fastest and slowest neighborhoods, which neighborhood files the most by phone.
Read the question, decide what tool would answer it in one call, and have your agent build it.
There is no required shape: name it, choose its arguments, and write the docstring so the model picks it.
Keep results small and read-only, keep addresses masked, and keep the earlier tests passing.
Push, wait for `Live`, reconnect with `/mcp`, and ask your agent to solve it.

## Stretch goals

- Ask your agent for `get_request` on an ID from another neighborhood, and check that the log line still shows your email.
- Turn **Log MCP Responses** back on, and decide which of your tools would need it off in a real deployment.

## If you fall behind

```bash
cp solutions/ex3/server.py server.py
git commit -am "Use the Exercise 3 solution" && git push
```
