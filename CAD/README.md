# R4 EDF TVC CAD deliverables

This directory contains the **R4 four-vane EDF vehicle and testbed CAD handover** for the HCT EDF thrust-vector-control project. The source files were supplied by the mechanical design team on 8 November 2026; the underlying R4 export dates may be earlier. The folder layout preserves the original CAD export subfolders (without the former `r4 design/` wrapper).

## Directory layout

| Directory | Contents | Files |
| --- | --- | ---: |
| [`cad/`](cad/) | Editable Fusion 360 vehicle/testbed archives (`.f3d`) and assembly STEP exports (`.step`) | 5 |
| [`parts/step/`](parts/step/) | Independent component STEP exports in manufacturing orientation | 17 |
| [`parts/stl/`](parts/stl/) | 3D-printable STL mesh exports | 18 |
| [`views/`](views/) | Assembly, exploded, component, and testbed PNG views | 39 |
| [`checks/`](checks/) | Machine-readable CAD validation results | 11 |
| [`logs/`](logs/) | Saved engineering process and validation logs | 52 |

**Not included:** print plans, engineering reports, RFQ/drawing request packages, the prior `DECISIONS.md` and `PROGRESS.md`, project proposals, and local generation scripts.

## Primary editable models and assembly files

- [`cad/EDF_PETG_Vehicle_R4_MIN.f3d`](cad/EDF_PETG_Vehicle_R4_MIN.f3d) — native Fusion 360 vehicle design; preserve as the primary editable model.
- [`cad/EDF_R4_TestBed.f3d`](cad/EDF_R4_TestBed.f3d) — native Fusion 360 testbed design.
- [`cad/EDF_PETG_Vehicle_R4_MIN_assembly.step`](cad/EDF_PETG_Vehicle_R4_MIN_assembly.step) — neutral-pose vehicle and tether assembly exchange file.
- [`cad/R4_R4-FLIGHT.step`](cad/R4_R4-FLIGHT.step) — flight group exchange geometry.
- [`cad/R4_R4-TETHER-KIT.step`](cad/R4_R4-TETHER-KIT.step) — removable tether kit exchange geometry.

To continue design work, import the `.f3d` files into Autodesk Fusion. The STEP files are useful for CAD interoperability, but may not preserve parametric construction history, components' full constraints, or motion joints. The original team should check external references, assembly joints, materials, and parameter rebuilds after import.

## Fabrication exports

See [`parts/step/`](parts/step/) for modifiable part geometry and [`parts/stl/`](parts/stl/) for slicer-ready meshes. Several parts retain an `R3-` prefix because the original R4 package reuses their geometry. The `TB-FL-01_testbed_foot_locator.stl` file has no matching independent STEP in this package. Print materials, orientations, fit tolerances, and settings must be verified separately; no print plan is supplied here.

## Verification status and safety

**Design handover — not a flight-readiness or fabrication approval.** The original source's validation summary identified **C-17 (fixed-vane option clearance) as failed** and **C-22 (some lead lengths) as unresolved pending physical measurement**. Keep these items open until rechecked using actual hardware and manufacturing tolerances. The electrical protection scheme also requires a separate safety review; do not treat these CAD models as evidence that wiring or flight testing is safe.

Machine-readable check outputs are in [`checks/`](checks/), with supplementary run records in [`logs/`](logs/). Open the Fusion files and independently verify clearances, mass/CG, fit, and part-level manufacturability before relying on the design.
