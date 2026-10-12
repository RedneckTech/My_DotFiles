# Pipeline hazard-handling patterns

Concrete, known-good patterns for a 5-stage in-order pipeline (IF/ID/EX/MEM/WB).
These are the shapes that work; adapt widths/names to the design.

## Write-first register file (fixes WB-write vs ID-read same-cycle)
```systemverilog
assign rd1 = (ra1 == 0) ? 0 : ((we && ra1 == wa) ? wd : rf[ra1]);
assign rd2 = (ra2 == 0) ? 0 : ((we && ra2 == wa) ? wd : rf[ra2]);
assign rd3 = (ra3 == 0) ? 0 : ((we && ra3 == wa) ? wd : rf[ra3]);
```
R0 is hardwired zero; the write is guarded by `we && wa != 0`.

## Forwarding mux (EX/MEM and MEM/WB -> EX)
```systemverilog
assign fwd_rs1 = (exmem_regwrite && !exmem_memread && exmem_rd==idex_ra1 && idex_ra1!=0) ? exmem_aluresult :
                 (memwb_regwrite && memwb_rd==idex_ra1 && idex_ra1!=0) ? wb_data : idex_rs1;
```
- `!exmem_memread` prevents forwarding a load's ADDRESS (exmem_aluresult is the
  address for a load, not the data). The load-use stall covers the load case.
- Forward to every consumer of the register: ALU a/b inputs, the load/store
  address pair, and the store data (a 3rd read port).

## Load-use stall (load result needed by the very next instruction)
```systemverilog
assign stall = idex_memread && idex_rd != 0 &&
               (idex_rd == ra1 || idex_rd == ra2 || idex_rd == ra3);
```
On stall: hold PC and IF/ID, bubble ID/EX (clear control signals only — data
fields may stay stale, they are ignored).

## Branch/jump flush (resolved in EX)
```systemverilog
assign flush = idex_jump || (idex_branch && branch_taken);
// PC: if (flush) pc <= idex_target; else pc <= pc + 2;
// IF/ID: ifid_instr <= flush ? NOP : imem_data;
// ID/EX: on rst || stall || flush, clear control signals (bubble).
```

## Flag forwarding (branch needs flags from the most recent flag-setter)
```systemverilog
always_comb begin
    if (exmem_flagwe) cur_flags = exmem_flags;
    else if (memwb_flagwe) cur_flags = memwb_flags;
    else cur_flags = sr_flags;
end
```
Carry-in for ADDC/SUBC and the branch condition both read `cur_flags`, not the
raw status register, so a flag-setting instruction immediately before a branch
or an add-with-carry is seen correctly.

## Flag bit order
Pack as `{v, n, z, c}` so bit 0 = carry, 1 = zero, 2 = negative, 3 = overflow.
Then branch conditions read `cur_flags[0]`=C, `[1]`=Z, `[2]`=N, `[3]`=V, and
carry-in is `cur_flags[0]`. Keep this order identical in the ALU output, the
pipeline registers, and the status register.
