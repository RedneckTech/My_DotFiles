# Obsolete Z80-era parts — alternatives & sources

Vintage-computing ICs that distributors no longer stock, with their
pin-compatible second sources and where to find them. All are NOS
(new-old-stock) or pulls; expect $3-20 each and verify authenticity.

## Floppy disk controller (DIP-40)

- **WD37C65** (Western Digital) — the common RC2014-era FDC. Obsolete.
- Pin-compatible alternatives (also obsolete, easier to find):
  - NEC **uPD765A / uPD765AC** — the original; WD37C65 is pin-compatible.
  - Intel **8272 / 8272A** — licensed second source of uPD765A.
  - **WD37C65B / WD37C65C** — later revisions; C adds 1 Mb/s data rate.
- Sources: eBay, UTSource, LittleDiode, surplus houses.
- Note: the RC2014 "Flock" project (github.com/skiselev/flock) uses this
  exact part — a known-good design reference.

## Z80 SIO/2 serial controller (DIP-40)

- Current part: **Z84C4206PEG** (6 MHz, RoHS) or Z84C4208PEG (8 MHz).
- Any Z84C42xx speed grade (4/6/8/10 MHz) works — the board clocks the
  SIO from the system clock.
- Sources: Mouser (692-Z84C4206PEG), UTSource, eBay, LittleDiode.
  Digi-Key lists Z84C4206PEG-ND but marks it "Obsolete" (not orderable).

## Z80 CTC counter/timer (DIP-28)

- Part numbers: **Z84C3006PEC**, Z84C3010PEC (10 MHz), Z8430 (NMOS).
- Any Z84C30 speed grade works.
- Sources: Jameco (stocks Z84C30), eBay, UTSource,
  arcadepartsandrepair.com (Z8430B1).

## 82C55A parallel peripheral interface (PLCC-44)

- Part numbers: **D71055C** (NEC), 82C55A (Intel/Intersil/OKI), MSM82C55A.
- Sources: eBay, UTSource, surplus. Still relatively common as NOS.
- Make sure to get PLCC-44, not the DIP-40 variant.

## Sourcing channels (vintage NOS)

- eBay — broadest, but highest counterfeit risk; check date code + logo.
- UTSource — large NOS inventory, ships from China.
- LittleDiode — UK surplus specialist.
- Jameco — still stocks some Z80-family parts.
- arcadepartsandrepair.com — arcade/retro parts, good for Z80 CTC.
