# Verified Digi-Key MPNs — vintage-computing connectors & passives

Known-good Manufacturer Part Numbers that actually resolve on Digi-Key for
RC2014 / SC126 / Z80-era boards. Use these instead of guessing; each was
verified against the catalog. Where a series has a numbering trap, the
correct digit is called out.

## Connectors

- RC2014 2x40 card socket (right-angle female): Samtec `SSW-140-02-T-D-RA`
  (80-pos receptacle, tin). Gold variant `SSW-140-02-G-D-RA` may not be
  stocked — tin is the safe default.
- IDE-40 (2x20, 2.54mm): Amphenol `67996-120HLF`.
- IDE-44 (2x22, 2.00mm): Molex `0878314420`. Series digit trap: 87831 =
  through-hole vertical, 87832 = SMT, 87833 = right-angle. A "straight"
  footprint needs 87831, not 87832.
- 34-pin floppy IDC (2x17, 2.54mm): Samtec `EJH-117-01-L-D-TH`. Option
  trap: `-01` = standard (mates IDSD), `-02` = extended (mates HCSD).
- DE9 male right-angle: NorComp `171-009-113R911`.
- 2.54mm single-row headers: Samtec `TSW-1xx-07-G-S` (xx = pin count).

## Switches / LED

- DIP-6 switch: CTS `206-6`.
- DIP-8 switch: CTS `206-8`.
- 3mm LED (green, T-1): Lite-On `LTL-4231N`. Any 3mm LED works; color is
  the user's call.

## Oscillators (half-size DIP-8, 5V, pinout 1=E/D 4=GND 5=OUT 8=VCC)

- 16.000 MHz: ECS `ECS-100A-160`.
- 1.8432 MHz: CTS `MXO45HST-2C-1M843200` (Digi-Key
  `110-MXO45HST-2C-1M843200-ND`). The datasheet alias `MXO45HST-1.8432`
  does NOT match the catalog.

## Passives

- 1/4W axial resistors: Stackpole `CF14JT` series (e.g. `CF14JT10K0`,
  `CF14JT4K70`, `CF14JT2K20`, `CF14JT100K`, `CF14JT270R`).
- 100nF 50V radial ceramic: Vishay `K104K15X7RF5TH5`.
- Bussed SIP resistor networks (9-pin = 8 resistors + common): Bourns
  `4609X-101-103LF` (10K), `4609X-101-472LF` (4.7K). Note: 4608X is 8-pin
  (7 resistors), 4609X is 9-pin (8 resistors) — match the pad count.
