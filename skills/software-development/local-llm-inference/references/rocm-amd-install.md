# ROCm install on Ubuntu 24.04 (AMD GPU)

Full recipe, userspace-only (kernel amdgpu driver presumed already loaded: `vulkaninfo` shows the card, `/dev/kfd` exists).

## Repo + key
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/rocm.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/latest noble main" | sudo tee /etc/apt/sources.list.d/rocm.list
```

## The pin (REQUIRED — install fails without it)
Ubuntu `universe` ships ROCm 5.7 packages with the same names (`rocminfo`, `rocm-cmake`, `hipcc`). apt compares version numbers and picks Ubuntu's "higher" 5.7/6.0.0 over AMD's `1.0.0.*70204` / `0.14.0.*70204`, so AMD's exact-version deps can't resolve. Pin AMD's origin above Ubuntu's; priority 1001 also permits the numerical downgrades:

```bash
sudo tee /etc/apt/preferences.d/rocm.pref >/dev/null <<'EOF'
Package: *
Pin: origin repo.radeon.com
Pin-Priority: 1001
EOF
```

## Install
```bash
sudo apt update
sudo apt install -y rocm-hip-sdk cmake ninja-build
```

`rocm-hip-sdk` is the canonical metapackage (pulls hipcc, rocBLAS, rocm-cmake, rocminfo). Don't install the full `rocm` metapackage — it drags in rccl/miopen/etc. you don't need for llama.cpp.

## Verify
```bash
/opt/rocm/bin/rocminfo | grep -i gfx   # should list the GPU arch (e.g. gfx1201)
```

## Post-install: render group (REQUIRED or the GPU is silent)
`rocminfo` and every GPU app need read-write on `/dev/kfd` + `/dev/dri/renderD*`, owned by the `render` group. A fresh user isn't in it, so `rocminfo` prints "Unable to open /dev/kfd read-write: Permission denied" and reports no GPU — looks like a failed install but is just group membership.

```bash
sudo usermod -aG render,video $USER   # then log out and back in
```

Verify it took (a shell started before the usermod keeps STALE memberships, so `groups` lies):
```bash
sg render -c id                     # should list render in the group set
grep -E '^(render|video):' /etc/group   # authoritative membership
```
Until you re-login, run GPU commands via `sg render -c "…"`.

## Version note
Check the current release before hardcoding: `curl -sS https://repo.radeon.com/rocm/apt/latest/dists/noble/main/binary-amd64/Packages.gz | zcat | grep -A2 'Package: rocblas'`. RDNA4 (gfx1201) needs ROCm 6.4+; the `latest` repo is usually fine.
