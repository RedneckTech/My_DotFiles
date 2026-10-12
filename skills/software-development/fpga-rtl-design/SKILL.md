---
name: fpga-rtl-design
description: "Use when designing or simulating FPGA/SystemVerilog RTL."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fpga, systemverilog, verilog, rtl, simulation, iverilog, verilator, pipeline]
    related_skills: [systematic-debugging, test-driven-development, project-planning]
---

# FPGA / SystemVerilog RTL Design & Verification

## When to Use
- Writing or debugging synthesizable RTL (CPU cores, pipelines, ALUs, register files).
- Setting up simulation (iverilog) or lint (verilator) for a Verilog/SystemVerilog design.
- Building a testbench or assembler for a custom ISA.

## Toolchain
- Simulate: `iverilog -g2012 -o out.vvp <rtl files> <tb files>` then `vvp out.vvp`.
- Lint: `verilator --lint-only -Wall --timing <rtl files>` (warnings exit non-zero; treat as errors).
- Install: `sudo apt-get install iverilog verilator`.
- Prefer SystemVerilog (`logic`, `always_ff`, `always_comb`) — iverilog 12 and Verilator both accept it.

## Pipeline design rules (each is a real bug class)
- **Write-first register file.** Forward the write data to same-cycle reads:
  `rd = (we && ra==wa) ? wd : rf[ra]`. A synchronous-write + async-read RF
  returns the STALE value to a read in the same cycle the write lands, silently
  corrupting back-to-back register dependencies (e.g. `ORI R2,5; MOV R4,R2`).
- **Define flag bit order once, use it everywhere.** Packing `{c,z,n,v}` puts c
  at the MSB; if the branch logic reads c at bit 0, every conditional branch
  silently mispredicts. Use `{v,n,z,c}` (LSB=c) or document the order and grep
  every consumer (branch condition, carry-in, status register).
- **Compare/test ops must not write back.** Set reg_write=0 for CMP/CMPI. A
  compare that writes its difference clobbers the operand register (e.g.
  `CMP R11,R4` overwrites R11 with 0).
- **Read each instruction field from the correct bit range per format.** A
  funct in [3:0] for an R-type may sit in [11:8] for a system/control format;
  reading the wrong range makes the op silently decode as NOP.

## iverilog quirks
- No `break` inside `repeat`/`for` loops — use a `while` loop with a flag.
- Variable bit-selects (`a[16-shamt]`) in `always_comb` are not supported;
  iverilog silently includes all bits, so shift carry-out is wrong. Verify shift
  flags in Verilator or restructure to avoid variable selects.

## Verification workflow
- Testbench: run a small program, check register/memory values with a `check`
  task; inspect internals via hierarchical access (`dut.u_rf.rf[1]`). Run until
  a `halted` signal or a cycle timeout.
- For a custom ISA, write a minimal two-pass assembler (labels + encode) EARLY —
  hand-encoding test programs is error-prone. Emit byte-per-line hex for
  `$readmemh`.
- Debug a failing pipeline by adding a per-cycle `$display` trace of PC,
  instruction, ALU inputs/result, and writeback — the trace pinpoints the exact
  stage where a value goes stale.

## References
- references/pipeline-hazards.md — concrete hazard-handling patterns (forwarding, load-use stall, branch flush, flag forwarding).
