# Hugging Face MCP server auth

Endpoint: `https://huggingface.co/mcp`. Unauthenticated requests work only for
public content and are rate-limited — always authenticate.

## Preferred: Bearer token (no OAuth app)

The server's README documents a plain header auth:

```yaml
mcp_servers:
  hugging_face:
    url: https://huggingface.co/mcp
    headers:
      Authorization: "Bearer ${MCP_HUGGING_FACE_API_KEY}"
```

Create the token at https://huggingface.co/settings/tokens (read scope is
enough). `hermes mcp add hugging_face --url https://huggingface.co/mcp --auth
header` saves it to `.env` as `MCP_HUGGING_FACE_API_KEY` and writes the
placeholder header. Verify a token:
`curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer <token>" https://huggingface.co/api/whoami-v2`
→ 200 = valid.

## OAuth app (only when Bearer is not offered)

Register at https://huggingface.co/settings/applications/new:

- **Public app (no client secret)** — PKCE auth with client_id only, the right
  shape for a native CLI/MCP client.
- **Redirect URIs**: `http://localhost/callback` and `http://127.0.0.1/callback`.
  HF accepts any port on loopback hosts, so the port-less form suffices for a
  client listening on an ephemeral port.
- **Scopes** (least privilege for read access to models/datasets/papers/Less):
  `openid profile read-repos gated-repos`. `gated-repos` is the one that lets
  it read gated models (Llama, Mistral, …) you already have access to. Skip
  write/inference scopes.

HF advertises dynamic client registration, but if that flow fails, pin the
pre-registered app under the server's `oauth:` block (`oauth.client_id`), then
`hermes mcp login hugging_face`.