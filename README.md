# EDF gimbal testbed

Student group project (HCT, UAE): **active stabilisation of a vertical thrust vector** on one
vehicle. It is an EDF "rocket": an electric ducted fan in a servo-driven two-axis gimbal, with a
Pixhawk 6C flight controller. The same rocket is used in two ways:

- bolted into a **test stand** that lets it tilt about an adjustable pivot (the testbed, used for
  identification, tuning and the controller comparison);
- flown **outdoors**, first in a tethered hover (committed), then in a free hover and landing
  (stretch goal).

Target: a working demo at the expo in roughly three months (from mid-September 2026), with the
rocket running live on its stand and video of the outdoor tests. A student-conference paper is
secondary.

Starting-point design: BB Projects, "SpaceX inspired EDF rocket"
(https://bbprojects.technology/blogs/projects/spacex-inspired-edf-rocket).

## Layout

```
edf-gimbal-testbed/
├── README.md                     ← this file
├── docs/                         ← written deliverables (markdown)
│   ├── gap-statement-review-2026-09-17.md              solid-motor gap audit (S1–S35)
│   ├── gap-statement-review-2026-09-17-edf-variant.md  EDF re-run (adds S36–S46); hover-linked citations
│   ├── part-1-team-split-and-interface-contract.md     split C decision, interface contract (to fill in), deliveries by week
│   └── part-2-control-group-kickoff.md                 control group: plant model, controllers, SITL setup, browser tools
├── bom/                          ← bill of materials and the tooling that produced it
│   ├── original.docx                                   the BOM as received (2026-09-18)
│   ├── …-fixed.docx                                    single one-page table, prices verified, total recomputed
│   ├── …-buy-now.docx                                  rows needed for the bench prototype
│   ├── …-can-wait.docx                                 rows only needed for a flight-ready vehicle (split made before the 2026-09-24 decision to fly)
│   ├── build_bom.py                                    regenerates the three files from unpacked/
│   ├── unpacked/                                       original.docx unzipped (runs merged) — build input
│   ├── extracted_rows.{json,md}                        the 37 rows + links as first read out of the docx
│   ├── check_pages.ps1                                 Word COM: page count, table span, link count, PDF export
│   └── pdf2png.ps1                                     WinRT: render a PDF page to PNG for visual checks
└── tools/
    └── gap-statement-review.skill                      packaged copy of the audit skill (also installed in ~/.claude/skills)
```

## Status (2026-09-24)

| Thread | State |
|---|---|
| Gap statement | Solid-motor version defensible only after narrowing; EDF version **not** defensible as written — rewritten statement in the EDF report (§"Rewritten statement"). |
| BOM | Fixed: 37 rows, grand total AED 6,065.22. Buy-now 34 rows (AED 6,013.22); can-wait 1 row (#6, AED 52.00). Rows 22, 29, 31, 36 are starred (`*`) in buy-now = "unsure, treat as buy-now". Flight parts not yet in it: radio transmitter + receiver, landing legs, a yaw actuator; GPS and a telemetry radio for the stretch goal (unpriced). |
| Team split | Finalised 2026-09-23: split C. Group 1 measures and reports numbers (first delivery: body architecture, mass, CG, CP, $d$, $L$, $J$); the control group builds the model and the controllers. Recorded in `docs/part-1-team-split-and-interface-contract.md`; the contract table and "done" checklist are to be filled in on 2026-09-23. Control-group plan in `docs/part-2-control-group-kickoff.md`. |
| Scope | Decided 2026-09-24: one build (the rocket is the testbed, bolted into a stand) and an outdoor test, which the mentor expects. A tethered outdoor hover is committed; a free hover and landing is a stretch goal. Consequences recorded in Part 1 (§1, §3 risk 7, §4.6 test ladder, §5, §6 items 3–5 and 8–10) and Part 2 (§1.1, §3, §4, §8, §9). |

## Open decisions

- BOM #10 UBEC unit price: Hobbywing ≈ AED 92 vs CHICIRIS AED 111.76 (sheet still says 105).
- Starred rows: suggestion is unstar #31, treat #36 as buy-now; #22 and #29 are the team's call.
- On the Part 1 §6 agenda (updated 2026-09-24):
  - the yaw actuator for flight (exhaust tabs or four vanes; decide before the mechanical design
    freezes);
  - the adjustable pivot (at the CG for flight-representative tuning, CG above it for the demo);
  - the flight mass budget (about 1.5 kg including the battery);
  - owners for the ESC, the wiring and the safety chain;
  - the group-1 liaison.

  Settled 2026-09-24: the rig layout (one build) and the two EDFs (the second set is a spare).
- Price the flight parts and add them to the BOM (rebuild with `build_bom.py`).
- Outdoor test: site, date (week 11 proposed), and written confirmation from HCT and, where
  required, the GCAA. The team expects no difficulty. However, GCAA Safety Decision 2026-03
  (27 March 2026) suspended recreational drone flights, and on 2026-09-23 there was no
  confirmation that the suspension had been lifted.
- Before the EDF gap statement goes into a paper: check whether EPFL (Linsen 2022) or
  QuadRocket (Santos 2026) have since released code.

## Rebuilding the BOM files

```bash
python bom/build_bom.py 14 504
```

Arguments are font size in half-points (14 = 7 pt) and page margin in twips (504 = 0.35 in).
Output goes to `%TEMP%\bom_out\` (a short path — the build failed on long paths), then copy the
three `.docx` files back into `bom/`. Check the one-page fit with
`powershell -File bom/check_pages.ps1 <absolute path to docx>`.

Python dependencies used by the tooling: `defusedxml`, `lxml`, `pypdf`, `pyyaml`.

## R4 CAD deliverables

The R4 four-vane EDF vehicle and tethered testbed CAD package is available in
[`CAD/`](CAD/README.md). It contains the editable Fusion 360 `.f3d` models,
assembly and individual-part STEP exports, STL meshes, CAD views, and saved
validation results and logs. The package deliberately excludes print plans,
engineering reports, RFQ files, design decision/progress notes, proposals,
and generation scripts.

**Status:** engineering CAD handover; not fabrication or flight approval. Open
clearance and hardware verification items are identified in [`CAD/README.md`](CAD/README.md).
