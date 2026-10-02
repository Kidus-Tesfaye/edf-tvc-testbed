# EDF thrust-vector control testbed

Student group project (HCT, UAE): **active stabilisation of a vertical thrust vector** on one
vehicle. It is an EDF "rocket": an electric ducted fan whose exhaust is steered by **four exhaust
vanes, each driven by its own servo**, with a Pixhawk 6C flight controller running ArduPilot.
("TVC" in the repo name stands for thrust-vector control: steering a vehicle by redirecting its
thrust.) The same rocket is used in two ways:

- bolted into a **test stand** that lets it tilt about an adjustable pivot (the testbed, used for
  identification, tuning and the controller comparison);
- flown **outdoors**, first in a tethered hover (committed), then in a free hover and landing
  (stretch goal).

Target: a working demo at the expo in roughly three months (from mid-September 2026), with the
rocket running live on its stand and video of the outdoor tests. A student-conference paper is
secondary.

Starting-point design: BB Projects, "SpaceX inspired EDF rocket"
(https://bbprojects.technology/blogs/projects/spacex-inspired-edf-rocket), which also flew four
exhaust vanes on ArduPilot.

**Change of actuator (2026-09-28).** Until 28 September 2026 the rocket was to be steered by a
servo-driven two-axis gimbal that tilted the whole fan. The team switched to vanes for the expo
and may return to the gimbal afterwards. The gimbal-era state of the repo is kept under the git
tag `gimbal-baseline`; `git show gimbal-baseline:<path>` prints any file as it was.

**Axis names.** The docs use the group's convention, adopted 2026-09-27 (Part 1 §4.1): *roll* is
the twist about the rocket's long axis, and *pitch* and *yaw* are the two tilts. ArduPilot names
them differently: our roll is ArduPilot's yaw with the opposite sign, our yaw is ArduPilot's
roll, and pitch is pitch.

## Layout

```
edf-tvc-testbed/
├── README.md                     ← this file
├── docs/                         ← written deliverables (markdown)
│   ├── gap-statement-review-2026-09-17.md              solid-motor gap audit (S1–S35)
│   ├── gap-statement-review-2026-09-17-edf-variant.md  EDF re-run (adds S36–S46); hover-linked citations
│   ├── part-1-team-split-and-interface-contract.md     split C decision, interface contract (partly filled in), deliveries by week
│   └── part-2-control-group-kickoff.md                 control group: plant model, controllers, SITL setup, browser tools
├── bom/                          ← bill of materials (to be reorganised with the BOM; see "BOM files")
│   ├── Four_Vane_EDF_BOM_Current.docx                  current: the four-vane BOM sent for procurement (reference copy)
│   ├── Gimbal_Testbed_BOM.docx                         gimbal era: single one-page table, prices verified (2026-09-20)
│   ├── original.docx                                   gimbal era: the BOM as received (2026-09-18)
│   ├── build_bom.py                                    gimbal era: regenerates the gimbal BOM files from unpacked/
│   ├── unpacked/                                       gimbal era: original.docx unzipped (runs merged), build input
│   ├── extracted_rows.{json,md}                        gimbal era: the 37 rows + links as first read out of the docx
│   ├── check_pages.ps1                                 Word COM: page count, table span, link count, PDF export
│   └── pdf2png.ps1                                     WinRT: render a PDF page to PNG for visual checks
└── tools/
    └── gap-statement-review.skill                      packaged copy of the audit skill (also installed in ~/.claude/skills)
```

## Status (2026-09-30)

| Thread | State |
|---|---|
| Actuator | Decided 2026-09-28: four exhaust vanes, one servo each, replacing the two-axis gimbal. The vanes reach roll as well as pitch and yaw, so no separate roll actuator is needed. They use ArduPilot's stock SingleCopter output mapping. The vane geometry is still to be designed (Part 1 §5, week 3), and their roll authority has to be checked against the fan's torque (Part 1 §6, item 4). |
| BOM | The four-vane BOM has been sent for procurement (reported 2026-09-30). `bom/Four_Vane_EDF_BOM_Current.docx` is a reference copy: its **embedded vendor links** are the source of truth for what is bought, not its row text. It supersedes the gimbal BOM (AED 6,065.22). Not in it yet: a radio transmitter and receiver and landing legs; for the stretch goal, GPS and a telemetry radio. |
| Gap statement | Solid-motor version defensible only after narrowing; EDF version **not** defensible as written — rewritten statement in the EDF report (§"Rewritten statement"). |
| Team split | Finalised 2026-09-23: split C. Group 1 measures and reports numbers (first delivery: body architecture, mass, CG, CP, $d$, $L$, $J$); the control group builds the model and the controllers. Recorded in `docs/part-1-team-split-and-interface-contract.md`. The contract's "Frames and signs" row holds the 2026-09-27 convention; the rest of the contract table and the "done" checklist are still to be agreed. Control-group plan in `docs/part-2-control-group-kickoff.md`. |
| Scope | Decided 2026-09-24: one build (the rocket is the testbed, bolted into a stand) and an outdoor test, which the mentor expects. A tethered outdoor hover is committed; a free hover and landing is a stretch goal. Consequences recorded in Part 1 (§1, §3 risk 7, §4.6 test ladder, §5, §6 items 3–5 and 8–10) and Part 2 (§1.1, §3, §4, §8, §9). |

## Open decisions

- On the Part 1 §6 agenda:
  - the vane design: geometry, linkage and travel (group 1, week 3), with enough roll authority
    left for the fan's reaction torque (item 4);
  - the adjustable pivot (at the CG for flight-representative tuning, CG above it for the demo);
  - the flight mass budget (about 1.5 kg including the battery);
  - owners for the ESC, the wiring and the safety chain;
  - the group-1 liaison.

  Settled: the rig layout (one build, 2026-09-24), the axis convention (2026-09-27) and the
  actuator (four vanes, 2026-09-28).
- Add the flight parts to the BOM: radio transmitter and receiver, landing legs; GPS and a
  telemetry radio for the stretch goal.
- Outdoor test: site, date (week 11 proposed), and written confirmation from HCT and, where
  required, the GCAA. The team expects no difficulty. However, GCAA Safety Decision 2026-03
  (27 March 2026) suspended recreational drone flights, and on 2026-09-23 there was no
  confirmation that the suspension had been lifted.
- Before the EDF gap statement goes into a paper: check whether EPFL (Linsen 2022) or
  QuadRocket (Santos 2026) have since released code.

## BOM files

The four-vane BOM is kept as a Word document outside this tooling. The copy in `bom/` is for
reference; its embedded vendor links say what is bought. Everything else in `bom/` belongs to the
gimbal era and will be reorganised along with the BOM.

To rebuild the gimbal-era files:

```bash
python bom/build_bom.py 14 504
```

Arguments are font size in half-points (14 = 7 pt) and page margin in twips (504 = 0.35 in).
Output goes to `%TEMP%\bom_out\` (a short path — the build failed on long paths), then copy the
three `.docx` files back into `bom/`. Check the one-page fit with
`powershell -File bom/check_pages.ps1 <absolute path to docx>`.

Python dependencies used by the tooling: `defusedxml`, `lxml`, `pypdf`, `pyyaml`.
