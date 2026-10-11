# 07 — Local LLM (llama.cpp + ROCm)

Self-hosted local inference on the RX 9070 XT. A Qwen2.5-Coder 14B model runs
on the GPU via ROCm, served by llama.cpp, and is wired into OpenCode as a
third provider alongside Zen and Go.

## Hardware / backend

- GPU: AMD **Radeon RX 9070 XT** (RDNA4, `gfx1201`), 16 GB VRAM.
- ROCm **7.2.4** (`/opt/rocm-7.2.4`, symlink `/opt/rocm` → `/etc/alternatives/rocm`);
  HIP runtime + hipBLAS/rocBLAS, HIP clang 22. Userspace only — the kernel
  `amdgpu` driver was already loaded, no `amdgpu-install`/dkms.
- Requires the `render` group (and `video`) on the user account to open
  `/dev/kfd`. `jpfeiff` is a member via `sudo usermod -aG render,video jpfeiff`.

## ROCm install (Ubuntu 24.04 / noble)

AMD's apt repo, pinned above Ubuntu's `universe` (which ships stale ROCm 5.7
packages under the same names and would otherwise win version resolution):

```bash
# key + source
curl -fsSL https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/rocm.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/latest noble main" \
  | sudo tee /etc/apt/sources.list.d/rocm.list
# pin (priority 1001 forces AMD's versions over universe's, permits downgrades)
# -> /etc/apt/preferences.d/rocm.pref  (Package: *, Pin: origin repo.radeon.com, Pin-Priority: 1001)
sudo apt update && sudo apt install -y rocm-hip-sdk cmake ninja-build
```

The pin is the one non-obvious step: without it, Ubuntu's `rocminfo` 5.7.1 /
`rocm-cmake` 6.0.0 / `hipcc` 5.7.1 clash with ROCm 7.2.4's exact-version deps.

## llama.cpp

- Source: `~/llama.cpp` (`git clone --depth 1 https://github.com/ggml-org/llama.cpp.git`,
  ggml 0.24.0).
- Built with `GGML_HIP=ON`, `GPU_TARGETS=gfx1201`, Release, FlashAttention enabled:

```bash
export PATH=/opt/rocm/bin:$PATH
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S ~/llama.cpp -B ~/llama.cpp/build -G Ninja \
    -DGGML_HIP=ON -DGPU_TARGETS=gfx1201 -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++
cmake --build ~/llama.cpp/build -- -j 16
```

Binaries land in `~/llama.cpp/build/bin/` (`llama-server`, `llama-cli`,
`llama-bench`).

## Model

- `~/models/qwen2.5-coder-14b-instruct-q4_k_m.gguf` (8.99 GB, Q4_K_M,
  14.77 B params) — Qwen's official GGUF from Hugging Face.

## Scripts (NOT in the dotfiles repo — plain files)

- `~/ai/start-llm.sh` — launches `llama-server` with the tuned flags below.
  Has a hard guard: exits with a clear error if the `render` group isn't
  active in the calling shell (prevents silent CPU-only fallback).
- `~/bin/llm` — start/stop wrapper: `llm -s` / `llm -k` (background + pidfile
  + health-check wait). Logs to `~/.local/state/llama-server/server.log`.

Tuning baked into `start-llm.sh`:

| Flag | Value | Why |
|------|-------|-----|
| `-ngl` | `99` | all layers in VRAM |
| `-fa` | `on` | flash attention |
| `-c` | `65536` | 64K context (see note below) |
| `--cache-type-k/v` | `q8_0` | quantized KV cache, fits more in VRAM |
| `--host --port` | `127.0.0.1:8080` | `LLM_HOST`/`LLM_PORT` override |
| `--alias` | `qwen-coder` | model id exposed via `/v1/models` |

Measured (llama-bench, 14B Q4_K_M, all layers GPU): **~2229 t/s** prompt
processing, **~55 t/s** generation.

### Context size note

OpenCode's build agent sends a ~26K-token prompt (all 11 MCP tool definitions
+ the superpowers plugin), which overflows a 16K server context. 64K works but
pushes VRAM to ~99% at idle (8.4 GB model + q8_0 KV). If it OOMs on long
sessions, drop `-c` to `32768`, or quantize the KV cache harder (`q4_0`).

## OpenCode integration

`llamacpp` provider in `opencode.jsonc` (`npm: @ai-sdk/openai-compatible`,
`baseURL: http://127.0.0.1:8080/v1`), model id `qwen-coder`. Selected in the
TUI (`Ctrl+X M`) or `opencode run ... --model llamacpp/qwen-coder`. See
[02-opencode.md](./02-opencode.md).

## Gotchas (recap)

1. apt pin — otherwise ROCm won't install (version clash with universe).
2. `render` group — otherwise ROCm silently falls back to CPU (25 → 2229 t/s).
3. A shell that predates the `usermod` keeps the old groups until re-login.
