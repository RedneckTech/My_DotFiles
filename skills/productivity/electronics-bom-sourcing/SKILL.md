---
name: electronics-bom-sourcing
description: Use when reviewing a hardware BOM or sourcing parts.
version: 1.0.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [electronics, bom, parts, sourcing, digikey, hardware]
    category: productivity
---

# Electronics BOM Review & Parts Sourcing

Turn a hardware project's BOM (and schematic) into a complete, orderable
parts list, and find sources/replacements for anything a distributor no
longer carries.

## When to Use

- A hardware project has a BOM (xlsx/csv) that needs reviewing or
  completing before ordering parts.
- The user needs a distributor-uploadable parts list (Digi-Key, Mouser).
- A part is obsolete/backordered and needs a replacement or source.

## Procedure

1. **Read the BOM.** BOMs are usually .xlsx or .csv. Use the `xlsx` skill's
   `xlsx_read.py --json --sheet <name>` to dump rows; the sheet is often
   named just `sheet`. Columns are typically ID / Name / Designator /
   Footprint / Quantity.
2. **Cross-check against the schematic.** Extract schematic PDFs with
   `pdftotext -layout <file>.pdf -` and scan for components the BOM omits
   (sockets, shunts, mating connectors) and for topology the BOM doesn't
   state (resistor-network bussed vs isolated). This is where BOMs are
   usually wrong or incomplete.
3. **Consolidate quantities** across boards when a project has multiple
   PCBs (e.g. two mezzanine boards sharing 74HCT138). Sum by part, keep
   designators in the reference column.
4. **Build the distributor CSV** (see Digi-Key format below).
5. **Flag obsolete parts and find replacements** — see
   `references/obsolete-z80-era-parts.md` for the common vintage-computing
   parts and their pin-compatible alternatives and sources.

## Digi-Key BOM upload format

Digi-Key's BOM Manager matches primarily on **Manufacturer Part Number**,
so accurate MPNs matter more than Digi-Key part numbers. Use this header
row (order is flexible; the tool maps columns):

    Quantity,Manufacturer Part Number,Digi-Key Part Number,Customer Reference,Description

- Leave `Digi-Key Part Number` blank when unknown — the MPN match will
  resolve it.
- Put designators in `Customer Reference` (e.g. `U2 U1 (JM003)`).
- For obsolete parts, leave the Digi-Key PN blank and put `OBSOLETE ...
  see REPLACEMENTS` in the Description so the upload flags it for manual
  handling rather than silently dropping it.
- Generic passives (resistors, caps, headers) can carry a representative
  MPN (e.g. Stackpole CF14 series for 1/4W axial, Bourns 4600X for SIP
  networks, Samtec TSW for 2.54mm headers) — the user can substitute any
  equivalent brand.

## Pitfalls

- **BOMs omit IC sockets and jumper shunts.** Every DIP/PLCC IC needs a
  socket, and every jumper header needs a shunt — neither is a "component"
  so neither appears in the BOM. Add them explicitly to the parts list.
- **Resistor networks: verify bussed vs isolated AND pin count.** A
  "SIP-8" / "RPACK-SIP-PTH-8" footprint name is ambiguous three ways: the
  number can mean pins OR resistors. "SIP-8" = 8 pins (7 resistors +
  common, bussed) or 4 resistors (isolated); "RPACK-SIP-PTH-8" = 8
  resistors = 9 pins. Bussed (common) networks have one common pin + N
  taps; isolated have 2 pins per resistor. Pull-ups on a data bus are
  bussed. The definitive check is the pad count and net names in the PCB
  file (see "Verify footprint/topology from the PCB file"), not the
  footprint name.
- **Oscillator footprint: full-size vs half-size DIP can.** "OSC-08" is
  ambiguous — it can be the full-size 8-pin DIP can (~20.8mm body) or the
  half-size (12.9mm). Don't assume from the name; measure the pad/body
  geometry in the PCB file (see "Verify footprint/topology from the PCB
  file"). Both share the same 4-pin pinout (1=E/D, 4=GND, 5=OUT, 8=VCC)
  at 2.54mm pitch / 7.62mm row spacing, so the pinout is not the risk —
  the body size is.
- **Obsolete parts have pin-compatible second sources.** Before declaring a
  part unobtainable, check for a licensed/pin-compatible alternative (e.g.
  WD37C65 ← uPD765A/8272). See the references file.
- **Watch for remarked/counterfeit NOS.** Vintage ICs (8272 especially) are
  commonly relabeled; advise checking date code and logo.
- **MPNs must match the distributor's catalog exactly — aliases and
  series-numbering guesses fail.** A datasheet alias (CTS "MXO45HST-1.8432"
  vs the catalog "MXO45HST-2C-1M843200") or a wrong series digit (Molex
  87831 through-hole vs 87832 SMT vs 87833 right-angle; Samtec EJH "-01"
  standard vs "-02" extended) yields an "Exact match not found" black bar
  even though the part exists. After writing the CSV, verify every
  non-obsolete MPN actually resolves on the distributor (browser upload or
  a `site:digikey.com` search) before handing it over — never trust memory
  or datasheet shorthand. See `references/verified-connector-parts.md` for
  known-good MPNs.

## Verify footprint/topology from the PCB file

When the BOM or schematic leaves a footprint ambiguous (resistor-network
topology/pin count, oscillator body size), read the PCB file's pad netlist
instead of guessing. EasyEDA JSON (the `.json` PCB export) stores each
component as a `LIB~...` string in the `shape` array; each `LIB~` string
contains `PAD~` sub-elements carrying the net name and coordinates. Count
the pads and read the net names:

- Resistor network: one pad on a power rail (+5V/GND) = the common pin;
  the rest are taps. N taps + 1 common = N-resistor bussed network. A
  common on GND is a pull-DOWN, on +5V a pull-UP.
- Oscillator: measure pad spacing to get body size (half-size ≈ 12.9mm,
  full-size ≈ 20.8mm); the 4 active pins are 1=E/D, 4=GND, 5=OUT, 8=VCC.

Parse with `json.load`, filter `shape` for `LIB~` entries containing the
designator or footprint name, then read the `PAD~` sub-strings.

## Digi-Key BOM upload (browser)

The BOM Manager works in guest mode (no login needed to upload and see
match results). Upload the CSV to the `#myListFileInput` file input, then
on the mapping step: Digi-Key auto-detects Quantity and Manufacturer Part
Number but leaves DigiKey Part Number / Customer Reference / Note as
"Skip" — set those three manually before Continue. Results classify each
line as "In Stock" (orderable), "Obsolete" (matched but not orderable —
source elsewhere), or "Exact match not found" (bad/placeholder MPN —
click "View Options" to pick the real part, or the part is truly
obsolete).

## References

- `references/obsolete-z80-era-parts.md` — vintage-computing ICs, their
  pin-compatible alternatives, and where to source them.
- `references/verified-connector-parts.md` — known-good Digi-Key MPNs for
  common vintage-computing connectors, oscillators, and passives.
