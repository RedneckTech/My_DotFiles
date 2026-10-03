# Pricing & hardware reference (2026)

Planning bands — re-quote before purchase. Full cited report:
datacenter-business-report.md in the project dir.

## Colocation (US, Tier III)
- 1U: $35-150/mo; quarter rack $330-650; half rack $400-900.
- Full 42U cabinet, 3-5 kW: $900-2500/mo (secondary markets ~$900-1800).
- Shifting to per-kW: retail ~$150-235/kW/mo; wholesale ~$195/kW/mo.
- Power for 3-5 kW adds ~$300-1000/mo; a 36-month term cuts 10-20%.

## Office (500-750 sq ft) — usually the wrong answer
- Rent: $21-84/sq ft/yr (avg ~$33), so ~$1000-2200/mo + 15-30% NNN/CAM.
- Electrical: ~$400/sq ft server-room (vs ~$200 office). Single rack floors
  ~$15k; 2-4 racks ~$55k; 200A->400A/800A service upgrade $25k-120k; generator
  ~$90k; 400-800A switchgear $18-34k; heavy 3-phase panel $6-12k.

## Power
- US commercial electricity ~13.5-14.5c/kWh (national avg ~14.5c June 2026).
- A 250W dual-socket 2U server = ~180 kWh/mo = ~$25/mo.

## Transit / IP
- Hurricane Electric IP transit from ~$200/mo; 10G ~$1/Mbps committed, plus
  $200-600/mo per cross-connect.
- ARIN gives a new ISP an automatic /24 (up to /22 with a utilization plan),
  plus an ASN on request. 3X-Small RSP = $262.50/yr (2026) covers /24 + 1-3 ASNs
  + /40 IPv6 (/36 under a waiver expiring Dec 2026). The ASN requires multihoming
  (2 upstreams) confirmed within 30 days. Buying IPv4 on the transfer market is
  ~$30-40/IP (~$7.5-10k a /24) or ~$1,000/yr to lease — the ARIN allocation is
  the cheap path, not a purchase.
- Routing vs NAT for VPS guests: one static IP per ISP = NAT only (guests share
  a public IP, no per-guest rDNS/SSL); per-guest public IPs need a block. A
  private-NAT VPS tier works with 1 static/ISP today; public VPS waits for the
  ARIN /24 + ASN + BGP.

## Refurbished servers (Dell)
| Model | Gen | CPU | RAM | Role | Street price |
|---|---|---|---|---|---|
| R410/R710 | 11th | Xeon 5500/5600 | DDR3 | dead-end (tape/utility only) | ~$50-200 |
| R320 | 12th | E5-2400 v2 | DDR3 | management node (actual unit; report says R330) | ~$100-200 |
| R620 | 12th | E5-2600 v2 | DDR3 | compute | ~$100-250 |
| R630 | 13th | E5-2600 v3/v4 | DDR4 | compute | ~$600 |
| R730/R730xd | 13th | E5-2600 v3/v4 | DDR4 | workhorse compute/storage | $480-720 typical |
| R740/R740xd | 14th | Xeon Scalable | DDR4 | compute + NVMe | $380-1800 |
| M640 blade | 13th | Xeon Scalable | DDR4 | dense compute (VRTX, 4 max) | ~$310-450 bare / ~$850 config |

US refurbishers with 1-3 yr warranty: SaveMyServer, TechMikeNY, ServerMonkey.
Gray-market (Alibaba) only for spares you burn-in test yourself.

## Storage
- ZFS: <=3 nodes, local NVMe latency, periodic replication (minutes of rollback
  on failover). Production-ready in about an hour.
- Ceph: 3+ nodes, zero-data-loss failover, 3x raw capacity, dedicated
  10/25/40G network, enterprise NVMe/SSD with power-loss protection, ~1GB RAM
  per TB of OSD.

## Software stack (all $0 license)
Proxmox VE (AGPL) hypervisor + Ceph/ZFS | OPNsense (BSD-2) firewall |
MikroTik RouterOS (license bundled in hardware) | Zabbix (AGPL) + Prometheus +
Grafana + NetBox (Apache-2) | FOSSBilling (AGPL) / Paymenter (MIT) |
Proxmox Backup Server + Bareos (AGPL) -> LTO | optional Proxmox sub €79-120/node/yr.

## Servers & enclosures (non-Dell, 2026 avg)
- Supermicro SYS-2029TP-HC1R (2U 4-node TwinPro, 24x2.5", Ceph seed): ~$800
  bare ($799 refurb); fully configured with Gold CPUs + RAM + SSD $10-20k.
- Supermicro SSG-1029P-NMR36L (1U 32x NF1/M.2 NVMe all-flash): ~$5,300-7,200
  bare/new. Customer fast-NVMe bulk tier, NOT HDD bulk.
- Dell PowerEdge VRTX (5U, 4 blades, 25x2.5"): ~$660-995 bare enclosure.
- Dell PowerEdge MX7000 (7U, 8 sleds): ~$2,000-2,500 refurb bare (VRTX
  upgrade; the only path to 25G/100G blades, via MX9116n fabric).
- Supermicro 6U 28-node MicroCloud: ~$2,000-3,000 est (re-quote).
- Gigabyte 4U 10x GPU: ~$6,000 configured (2x Gold 6150, 512GB) + 10 GPUs.
- Supermicro X10SLH-N6-ST031 (1U, 6x10GbE, E3-1270 v3, 32GB): ~$230 refurb
  (the OPNsense/pfSense HA-pair boxes).

## Components (2026 avg, used/refurb unless noted)
- Intel Xeon E5-2680 v4 (14c): ~$30/ea. Xeon Gold 6138 (20c): ~$100/ea.
- 32GB DDR4-2400/2666 ECC RDIMM: ~$150-295 (avg ~$180). DDR4 ECC rose 60-80%
  from early 2025 to Q1 2026; DDR5 rose more, so DDR4 is still the value play.
- 32GB DDR3 LRDIMM (IBM E7 / older Dell): ~$50-65.
- 10TB enterprise SATA HDD (Seagate Exos / WD Ultrastar): ~$270 refurb,
  $300-380 new.
- Enterprise SSD 1.92TB SATA: ~$260-330; 1.92TB NVMe U.2 (PM9A3): ~$330.
- 2TB U.2 NVMe: ~$200 used / ~$280 new. U.2->PCIe adapter card: ~$35-50.
- Mellanox ConnectX-4 100GbE dual-port (MCX456A-ECAT): ~$300-400 used.
- Mellanox ConnectX-4 Lx 25GbE dual-port (MCX4121A): ~$35-175 (avg ~$100).
- LSI 9300-8e 12G SAS HBA (external, for DAS shelf / LTO): ~$43-199 (avg ~$80).
- LTO-7 cartridge (6TB native / 15TB comp): ~$68-90/ea.
- Raspberry Pi CM4 8GB: ~$70-90. Compute Blade carrier (Uptime Ind.): ~$65-85;
  20 fit 1U, PoE-powered. Raspberry Pi 4 8GB: ~$150-170 retail.

## MikroTik networking (2026, list/street)
- CCR2004-16G-2S+PC (BGP edge): $465 list, $385-467 street — only 2x 10G SFP+
  (16x 1G), so it runs out of 10G ports when transit goes 10G.
- CCR2004-1G-12S+2XS (12x10G + 2x25G): ~$595 — the 10G-transit edge pick.
- CCR2116-12G-4S+ (4x SFP+): ~$995.
- CRS354-48G-4S+2Q+RM: owned ToR/core (48x1G + 4x10G + 2x40G).
- CRS354-48P-4S+2Q+RM (PoE version): ~$814-999 (avg ~$850).
- CRS520-4XS-16XQ-RM (16x100G + 4x25G): $2,195 list, ~$2,040 street.
- CRS518-16XS-2XQ-RM (16x25G + 2x100G): ~$1,136-1,695 (avg ~$1,300).
- CRS812 DDQ (400G agg): $1,295 list, ~$1,080 street.
- CRS804 DDQ (4x400G): $1,295 list, ~$1,195 street.
- Transceivers (3rd-party/compatible): QSFP+ 40G SR4 $20-60; QSFP28 100G SR4
  $35-80; SFP28 25G $25-50; SFP+ 10G $15-30; DAC cables $15-30.
