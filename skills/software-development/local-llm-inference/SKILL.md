---
name: local-llm-inference
description: Use when setting up local LLM inference with llama.cpp.
---

# Local LLM inference (llama.cpp)

Standing up llama.cpp on this user's own hardware, from first hardware inspection through GPU backend, model choice, and perf tuning. User prefers max speed (ROCm/HIP over a quicker no-install path) and avoids Docker/Go when a prebuilt binary or a from-source build will do.

## Procedure

### 1. Inspect hardware FIRST — never answer from memory
Run these together; every choice downstream depends on the result:

```bash
lscpu | grep -E "Model name|CPU\(s\)|Core|Socket"   # cores/threads, AVX-512 in Flags
free -h                                               # RAM
lspci | grep -iE "vga|3d|display"                     # GPU vendor (may show bare PCI id)
vulkaninfo --summary 2>/dev/null | grep -iE "deviceName|driverName"   # REAL GPU name + arch
cat /sys/class/drm/card*/device/mem_info_vram_total   # VRAM bytes
ls /dev/kfd 2>/dev/null || echo no-kfd                 # ROCm/HIP possible when /dev/kfd exists
df -h / .                                             # free space for models + build
```

lspci often reports an AMD card as `Device 7550` with no friendly name — `vulkaninfo --summary` resolves it (e.g. `AMD Radeon RX 9070 XT (RADV GFX1201)`). The GFX#### token is the ROCm arch name you need.

### 2. Pick the GPU backend
- NVIDIA → CUDA (`GGML_CUDA=ON`).
- AMD → ROCm/HIP (`GGML_HIP=ON`) for max speed; Vulkan (`GGML_VULKAN=ON`) works with zero install against the already-loaded RADV driver but is ~85-90% of peak. The user wants ROCm.
- AMD GPU arch name: gfx1100 = RX 7000, gfx1201 = RX 9070 XT (RDNA4). RDNA4 requires ROCm 6.4+.

### 3. Install the backend
- NVIDIA: CUDA toolkit apt repo.
- AMD: see `references/rocm-amd-install.md` (includes the apt-pinning fix).

### 4. Build llama.cpp
```bash
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
export PATH=/opt/rocm/bin:$PATH   # so hipconfig resolves
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -G Ninja -DGGML_HIP=ON -DGPU_TARGETS=gfx1201 \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ \
  && cmake --build build -- -j 16
```
Pin the host compiler to gcc/g++ — otherwise a Homebrew clang on PATH (e.g. /home/linuxbrew/.linuxbrew/bin/clang) gets picked; AMD clang (via `HIPCXX`) handles device code automatically. This llama.cpp uses `-DGPU_TARGETS=<arch>`, not the old `-DAMDGPU_TARGETS`. Success = "HIP and hipBLAS found" in the configure output.

### 5. Pick the model by VRAM budget (Q4_K_M GGUFs)
| class | Q4_K_M size | fits in |
|---|---|---|
| 8B | ~5 GB | any modern GPU |
| 14B | ~9 GB | 16 GB (fully offloaded) |
| 32B | ~19 GB | 16 GB partial / 24 GB full |
| 70B | ~40 GB | multi-GPU or CPU-heavy |

Fully-offloaded model runs at full GPU speed; anything larger spills to CPU and drops multi-x. "Coding + sysadmin" → 14B coder model (e.g. Qwen2.5-Coder) is the speed/quality sweet spot. GGUFs from the model author's official HF repo (e.g. `Qwen/Qwen2.5-Coder-14B-Instruct-GGUF`).

### 6. Verify + tune
```bash
./build/bin/llama-bench -m model.gguf          # tok/s, confirm VRAM offload
./build/bin/llama-server -m model.gguf --n-gpu-layers 99
```
Perf levers: `--n-gpu-layers 99` (full offload), `--flash-attn on`, `--cache-type-k q8_0 --cache-type-v q8_0` (KV cache quant, bigger context in VRAM), `--ctx-size`. Serve with a frontend (Open WebUI) if the user wants a UI.

### 7. Serve + diagnose a hung request
Serve an OpenAI-compatible endpoint (this user's setup: `~/bin/llm` control script wrapping `~/ai/start-llm.sh`, model alias `qwen-coder` on `127.0.0.1:8080`, server log at `~/.local/state/llama-server/server.log`):

```bash
llm -s                                  # start (background, waits for /health ready)
curl -s 127.0.0.1:8080/health           # -> {"status":"ok"}
curl -s 127.0.0.1:8080/slots            # per-slot state (bare JSON array, one object per slot)
```

"Is it actually generating, or is it stuck?" is answered by `/slots`, not by watching the client (a coding agent will keep retrying and then just hang waiting):

- A slot with `n_prompt_tokens` > 0 but `n_prompt_tokens_processed == 0` and `is_processing == false`, unchanged across two samples ~20s apart → the request is WEDGED (prompt accepted, evaluation never dispatched). Not slow, not idle — restart the server; the in-flight request is lost.
- `/metrics` returns 501 "not supported" unless the server was launched with `--metrics`.

On a **running** server, confirm GPU offload is really active (not silently fallen back to CPU):

```bash
ls -l /proc/PID/fd | grep -E 'kfd|renderD128'   # /dev/kfd + /dev/dri/renderD128 open = offloaded
rocm-smi --showuse            # GPU busy %
rocm-smi --showmeminfo vram   # VRAM in use (model + KV cache ~= full when fully offloaded)
```

`ggml_cuda_init: failed to initialize ROCm` in the log = the server came up CPU-only (prompt drops from ~2200 t/s to ~25 t/s). This is the operational face of the render-group pitfall below — restart through `sg render`.

Restart WITH GPU requires `render` active in the *launching* shell; `llm -s` from a plain shell can't activate the group:

```bash
llm -k && sg render -c "$HOME/bin/llm -s"
```

Caveat: the running server may have been started manually (e.g. `sg render -c "$HOME/ai/start-llm.sh"`) rather than via `llm -s` — its output then goes to a pipe, not `server.log`. Check `ps` ancestry (`pstree -sp PID` / `ps --ppid`) before trusting the log path.

## Pitfalls
- **`ps %CPU` is a lifetime average, not current activity.** A stable nonzero `%CPU` (e.g. 10%) with a frozen `TIME` column means the process is actually idle — the % is total-CPU÷elapsed-time. To tell whether something (an agent CLI, a daemon) is actively computing, sample the `TIME` column 3× ~1s apart and watch it advance, or `top -H -p PID` for per-thread CPU. Don't conclude "busy" from a nonzero pcpu alone.
- **ROCm on Ubuntu 24.04 fails with "unmet dependencies: rocm-hip-runtime depends rocminfo (= 1.0.0.x) but 5.7.1 … is to be installed"** — Ubuntu universe ships its own ROCm 5.7 packages under the same names, and apt prefers their higher version numbers (rocm-cmake 6.0.0 vs AMD's 0.14.0). Fix by pinning AMD's origin above Ubuntu (`Pin-Priority: 1001`), not by forcing specific package versions. See the reference.
- **Don't run `amdgpu-install` / dkms when the kernel driver is already loaded.** If `vulkaninfo` shows the GPU and `/dev/kfd` exists, install ROCm *userspace only* (repo + `rocm-hip-sdk`). Skip the kernel-driver step entirely.
- **sudo interactivity.** This is a CLI session; a sudo prompt in a non-interactive tool call fails with "incorrect password attempts". Write the root-requiring steps into a script file, tell the user to run it in their own terminal, and proceed with the non-root work (git clone, model download) in parallel rather than stalling.
- **render group not set → GPU invisibly missing.** After install, `rocminfo` prints only the CPU ("Unable to open /dev/kfd … Permission denied") because the user isn't in the `render` group — it looks like a broken install but is just permissions. `sudo usermod -aG render,video $USER` + re-login. Verify with `sg render -c id` or `grep -E '^(render|video):' /etc/group`, NOT `groups` (a shell started before the change keeps stale memberships). Until re-login, wrap GPU commands as `sg render -c "…"`.
- **llama-cli flag drift.** `-cnv` / `-no-cnv` are removed — conversation mode is auto-detected from the GGUF chat template. Use `-st`/`--single-turn` for a one-shot; when a flag errors as invalid, run `llama-cli --help | grep -i <term>` instead of assuming the old name.
