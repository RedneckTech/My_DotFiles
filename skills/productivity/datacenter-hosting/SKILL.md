---
name: datacenter-hosting
description: "Use when working on the datacenter-hosting business."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [datacenter, hosting, colocation, refurbished-servers, infrastructure]
    category: productivity
    related_skills: [project-planning, grounded-citations]
---

# Datacenter / Hosting (small provider)

## When to use
Any work on the user's small datacenter / hosting business: refurbished server
selection, the open-source software stack, MikroTik + OPNsense network design,
colocation vs self-hosting, power/cooling, pricing, or the phased build-out.

## Standing context (read first)
Project dir: /media/jpfeiff/MassStorge/DevZone/DataCenter. Project files:
datacenter-business-report.md (cited research), market_report.md,
hardware_list.txt (inventory), network-plan.md (topology + VLAN/IP map). Start
from the report; don't re-derive what it already answers.

The user is building a dedicated-server + VPS provider on self-owned refurbished
hardware, colocated (they have outgrown home power). Open-source software is a
hard filter.

Hardware owned (authoritative inventory = hardware_list.txt — trust it over
this report, which drifts; e.g. the report says "R330" but the actual unit is
a Dell R320): 42U rack; MikroTik CRS354-48G (48x1G + 4x10G + 2x40G, ToR/core);
Dell R320 (mgmt), R630, R620, R410, R710 (LTO host), IBM X3850 X5 (DDR3);
Supermicro SYS-6016GT-TF 1U + lab-only Tesla S1070/S2070 1U GPU nodes; Wiwynn
Lyra SV315 10-SFF SSD NAS; 1U 4x Raspberry Pi 4 8GB. Planned: Dell VRTX (4x
M640 blades) -> MX7000 upgrade, R730xd (12x3.5" + 2x2.5" rear) + MD1400 DAS
shelf, LTO-7 library (on the R710), Supermicro 2U 4-node (Ceph seed),
SSG-1029P-NMR36L (customer fast-NVMe bulk tier).

Decisions already made (do not relitigate unless the user reopens them):
- Bootstrap on ALL owned hardware, then phase out oldest-first (R410, then
  IBM 4U); keep the R710 as the LTO tape controller.
- Colocate the full cabinet now (~$900-2500/mo). A 500-750 sq ft office is
  phase 4, gated on the building actually having the electrical service.
- Blades: start on the Dell VRTX (4 blades/5U), upgrade path is the MX7000
  (8 sleds/7U) in phase 3 — not the M1000e.
- Bulk HDD storage: R730xd (12x3.5" LFF + 2x2.5" rear) + MD1400 DAS shelf
  (dumb 12G SAS shelf, external HBA in the R730, ZFS-managed) — not an iSCSI
  array like the MD3800i.
- Stack: Proxmox VE + ZFS now, Ceph on the 4-node Supermicro later; OPNsense
  (not pfSense) firewall; MikroTik CCR for the BGP edge; Zabbix + NetBox +
  Grafana; FOSSBilling or Paymenter; Proxmox Backup Server + Bareos to LTO.
- Switch roles (network-plan.md has the full topology + VLAN/IP map): owned
  CRS354-48G = management/OOB; CRS354-48P = CM4 Docker access (PoE, data
  plane); CRS520 = 100G spine (Ceph + R730 + uplink to leaf); CRS518 = 25G leaf
  (VPS/compute). Speed tiers: 100G storage, 25G VPS/compute, 10G VRTX (hard
  ceiling), 1G management. VPS starts as private NAT (10.0.3.0/24) behind ISP
  statics; public per-guest IPs wait for the ARIN /24 + ASN.

## Editing hardware_list.txt
The inventory is a plain .txt file, not markdown — keep it plain text. When the
user asks to "add missing hardware + avg prices": build a per-server component
BOM (CPU, RAM, drives, NIC, HBA) with avg-market prices and a subtotal, then a
rough totals block, then an "items to confirm" section. Flag model discrepancies
(e.g. VRTX vs M1000e, R320 vs R330) for the user to resolve — never silently
"fix" a model number. Mark every price as avg-market / re-quote before purchase.

## Domain rules (pitfalls — generalizable, not incident narration)
- Power is the business. Cost a server by watts-per-compute over its lifetime,
  not purchase price. Budget ~$25/mo/server at ~14c/kWh.
- Dell 11th gen (R410/R710, Xeon 5500/5600, DDR3) is a power-inefficient
  dead-end; 13th gen (R330/R630, DDR4) is the production floor; 14th gen
  (R640/R740) is the sweet spot. Never build sellable capacity on 11th-gen.
- Colo vs office: server-room electrical buildout (~$15k for one rack, ~$55k
  for 2-4, $25k-120k for a service upgrade, ~$90k for a generator) dwarfs
  office rent, and a 500-750 sq ft office usually lacks the power feed.
  Colocate until 2-3+ racks of contracted density.
- Ceph needs 3+ nodes (4-5 to self-heal), a dedicated fast storage network,
  and 3x raw capacity (size=3/min_size=2). ZFS + replication wins for <=3
  nodes. Do not adopt Ceph before zero-data-loss failover is a real requirement.
- MikroTik CRS-series is an L2/L3 switch, not a full-table BGP router — the
  transit/BGP edge needs a CCR-series router (e.g. CCR2004-16G-2S+PC x2), even
  though CRS units run RouterOS. CRS can run BGP (RouterOS L6) but L3HW offload
  caps ~240K IPv4 routes vs a ~900K full table; excess falls back to slow CPU
  routing. RAM (not CPU) bounds BGP table size.
- CCR2004 naming: "PC" suffix = passive cooling (fanless), NOT PCIe. The PCIe
  card router is a separate model, CCR2004-1G-2XS-PCIe (~$199, 1G + 2x 25G
  SFP28) — meant to bolt 25G routing onto a server (single PSU via slot, needs
  a host), not a standalone edge.
- A blade enclosure (VRTX/MX7000) draws idle power even empty — do not rack it
  until enough blades (and paying customers) justify the baseline watts.
- Dell VRTX is a 10G-only platform: M640 blades use a dual-10G NDC (Broadcom
  57810S) and Fabric A accepts only 1G/10G I/O modules (R1-2210 = 4x 10G SFP+
  max). No 25G/40G/100G path exists — not even 100G->4x25G breakout, since the
  VRTX has no 25G port to receive the links. Max uplink = 4x 10G LACP. >10G to
  blades requires the MX7000 (native 25G/100G fabric).
- LTO-7 = 6TB native / 15TB compressed, 300 MB/s. Drives ship 6Gb SAS
  (half-height) or 8Gb FC (full-height); 12Gb SAS is LTO-8's interface and a
  12G SAS HBA is backward-compatible. Confirm SAS vs FC before buying the HBA.
- DPUs/SmartNICs (NVIDIA BlueField, Intel IPU) don't pay off below ~50-100 nodes
  or without a high-offload workload (NVMe-oF, heavy OVS/VXLAN, 50G+ crypto,
  bare-metal tenant isolation). A plain ConnectX-4/5 NIC already offloads
  RDMA/RoCE/VXLAN/checksum. Never buy a NIC that costs more than the refurb
  server it goes in.

## References
- references/pricing-and-hardware.md — 2026 pricing bands and hardware
  generation guide for quoting and spec decisions.
