# Part 1: Team split and interface contract — EDF Thrust-Vector Control Testbed

*Split out on 2026-09-23 from `team-split-and-control-group-kickoff.md` (written 2026-09-20). This part and [Part 2: Control group kickoff](part-2-control-group-kickoff.md) replace that file. For both groups. Written for the BOM of 17–19 Sep (Pixhawk 6C, DS3240 servos on a two-axis gimbal, 70 mm 6S EDF) and roughly three months to the expo. **Updated 2026-09-24:** one build, where the rocket is the testbed, bolted into a stand for bench work, plus an outdoor test (§1, §3, §4.1, §4.3, §4.6, §5, §6). **Updated 2026-09-30 for the switch to vanes:** the rocket is now steered by four exhaust vanes, one servo each, as in the four-vane BOM sent for procurement (`bom/Four_Vane_EDF_BOM_Current.docx`; its embedded vendor links define the parts). The gimbal-era version of this file is under the git tag `gimbal-baseline`. Axis names now follow the group's convention of 2026-09-27 (§4.1): roll is the twist about the long axis, and pitch and yaw are the two tilts. Where earlier versions said "yaw" for the twist, read roll.*

**In short:** the team uses split C. Group 1 builds and measures the rig and reports the numbers; group 2 turns those numbers into a model and a controller. There is one vehicle: the rocket. It bolts into a test stand for bench work and is flown outdoors, first in a tethered hover (committed) and then in a free hover (stretch goal). This part records who owns what, what crosses between the groups and when, and what is still to be agreed. The control group's own starting plan is in Part 2.

## Good to know beforehand

**What this assumes you know:** what the testbed is (an EDF whose exhaust is steered by four servo-driven vanes, on a body that tilts about a pivot) and roughly what a control loop is (measure → compare with a target → command an actuator). Everything else is defined where it appears.

| Term | Meaning here |
|---|---|
| Interface contract | A short written agreement between the two groups on exactly what crosses the boundary between their work (signals, units, sign conventions, timing, connectors), fixed early so each side can build before the other is finished |
| Plant | The thing being controlled: body + fan + vanes + sensors. The controller is everything else |
| Vanes | Four small plates in the fan's exhaust, each turned by its own servo. Turning a vane deflects part of the jet and pushes the tail sideways; together they give torque about all three axes (roll, pitch and yaw) |
| System identification | Measuring the plant experimentally (weighing, balancing, swing tests, step tests, thrust-stand runs) so the model uses real numbers instead of guesses |
| CG, CP | Centre of gravity: where the body's weight acts. Centre of pressure: where the net aerodynamic force acts |
| $d$, $L$, $J$ | Pivot-to-CG distance, pivot-to-thrust-line distance, and moment of inertia about the pivot (how hard the body is to swing): the body numbers the plant model cannot run without |
| Integration | The phase where separately built parts are joined and made to work together. It always takes longer than planned |

**Scope:** how the work is split, what crosses the boundary, and what is still open. Not covered: the mechanical design itself, and the control group's technical plan (Part 2).

---

## 1. Decision: split C

**Finalised; recorded 2026-09-23.**

| | Group 1: hardware | Group 2: control + actuation |
|---|---|---|
| Builds | The rocket (body, fixed fan mount, the four vanes with their pivots and linkages, landing legs) within the flight mass budget, and the test stand it bolts into (adjustable pivot): design, 3D printing, assembly; sensor placement and mounting | The plant model; the controllers; the Pixhawk and servo configuration, including flight modes, the radio kill switch and failsafes |
| Measures | The body and the fan: mass, CG, CP, $d$, $L$, $J$; thrust-stand runs | The actuators: servo step tests on a fan-free desk rig |
| Delivers | Identification results as numbers, each with units, a tolerance and a source, reported by a named liaison: `[name]` | A controller that runs on the stand, the PID-versus-LQR comparison for the paper, and a tested flight configuration for the outdoor test |

**Why this split.** The 2026-09-20 review found the first plan ("hardware first, control takes the output") workable as an ownership split but dangerous as a sequence: the control group would wait until the rig existed, then do all of its work in the last four weeks. Split C removes the wait, because what crosses between the groups is a defined artefact, numbers, rather than "the rig". The first numbers can come from CAD long before anything is printed, and until then the control group works in simulation (Part 2).

**One build (decided 2026-09-24).** The rocket and the testbed are the same vehicle: it bolts into a stand for bench work and comes off it to fly. Everything measured and tuned on the stand therefore applies to what flies, and the expo shows the real rocket running on its stand, with video of the outdoor tests. The mentor expects an outdoor test, so a tethered outdoor hover is committed; a free hover and landing is a stretch goal. The cost: a crash outdoors would damage the testbed and the expo display (risk 7, §3).

This matches the CDP's individual-responsibility section (`cdp-section-6-2-individual-responsibility.md`): the control group derives the model and fits it to measurements.

## 2. What the split gets right

- **Clear ownership.** Every part in the BOM has an obvious owner; nobody argues over who fixes a broken linkage or a diverging gain.
- **Skill matching.** CAD, printing, wiring and mounting are a different craft from state estimation and controller design. Letting people specialise makes both halves better.
- **Parallel work.** Printing the vane support frame and deriving the plant model can happen on the same day in different rooms, because each side knows which numbers the other needs (§5).
- **It mirrors the paper.** The audit reports and Section 4 of the proposal frame the contribution as "an open testbed" (hardware) plus "a controller comparison on it" (control).

## 3. Risks and how each is handled

The six usual ways a hardware/control split fails, from the 2026-09-20 review, where each stands now, and one risk added on 2026-09-24 by the decision to fly the same vehicle:

| # | Risk | Why it matters | Handled by | Status |
|---|---|---|---|---|
| 1 | **Serial dependency** | If control waits for the finished rig (week 7–8 at the earliest), four weeks remain for identification, tuning, comparison and the demo | Split C: numbers from CAD first; control works in simulation, then on a desk rig (§4.2) | Handled |
| 2 | **"Input" undefined** | Raw IMU samples or fused attitude? Servo angle or vane angle? The answers decide the controller's structure | The contract (§4.1) and the delivery schedule (§5) | Contract to be agreed 2026-09-23 |
| 3 | **Nobody owns the seam** | ESC setup, flight-controller configuration, servo PWM mapping, arming and the safety chain (E-stop → contactor → fuse) are neither "3D printing" nor "control" | An on-call integrator (§4.4) and a named owner for each seam item | Owners to be agreed 2026-09-23 (§6) |
| 4 | **The model needs both groups** | Mass properties and thrust come from hardware; fitting comes from control. Neither group can build the model alone | Split C as recorded in §1: group 1 measures, group 2 models | Handled |
| 5 | **Knowledge silos** | A jittering servo may be a linkage, a BEC brownout, a PWM range or a gain; if only one group can diagnose each, every problem takes a meeting | Regular joint meetings; joint test days in weeks 9–12 (§4.3) | Handled |
| 6 | **Roll (the twist)** | The fan's reaction torque drives roll continuously. The two-axis gimbal could not counter it; the four vanes can. But roll and the two tilts share the same four vanes, so whatever travel the roll trim takes is lost to pitch and yaw. On the stand the pivot joint can lock roll; in flight nothing does, and a tether doesn't stop spin | Actuator: the vanes (decided 2026-09-28). Measure the fan's torque (§5, week 6) and size the vanes so the roll trim leaves travel for the tilts (§6, item 4). Stand: roll locked at the joint for the first tilt tests | Actuator decided; roll authority to check before the vane geometry freezes |
| 7 | **One vehicle, two jobs** | A crash in an outdoor test damages the only rocket, which is also the testbed and the expo display | The test ladder and its gates (§4.6); stand results logged before any flight; spares (reprintable parts, including spare vanes; check which electronics spares the four-vane BOM includes); no flying in week 12 | Planned (§4.6, §5) |

## 4. The contract and the working agreements

### 4.1 Interface contract

**Status: to be agreed on 2026-09-23. Updated 2026-09-30:** the "Frames and signs" row holds the convention the group adopted on 2026-09-27; the other rows are still open. One page; both groups agree it; it changes only by agreement. Fill in the last column. Where a value isn't known yet, write "TBD by [date], [owner]" instead of leaving the cell blank, so every gap has an owner.

| Section | What it fixes | Example entry (a guide, not a decision) | Agreed entry |
|---|---|---|---|
| Frames and signs | Body axes; which way is +pitch; where the IMU points; which vane is on which output; each vane's positive deflection direction | "Vane on SERVO1 sits on the +z side; +PWM turns its trailing edge toward +y" | **Adopted 2026-09-27: the rocket engineers' convention.** $x$ along the long axis, out of the nose; $z$ along the Pixhawk's arrow, with the board flat across the body; $y$ completes a right-handed set. Roll about $x$ (the twist), pitch about $y$, yaw about $z$; every positive direction by the right-hand rule. Attitude is measured from a pad frame with $x$ vertical, so upright is 0, 0, 0. ArduPilot translation, applied in one place only: roll = −ArduPilot yaw (roll rate = −gyro $z$), pitch = ArduPilot pitch, yaw = ArduPilot roll. **Still open:** which vane is on which output and each vane's positive direction (see "Actuator mapping"); confirm that the group also took the axis letters (its draft used $y$ for the long axis) |
| Actuator mapping | For each of the four vanes: PWM range ↔ servo angle ↔ vane angle; neutral (trim); mechanical limits; linkage ratio. Which output drives which vane | "SingleCopter order: SERVO1–4 = the vanes on the +z, +y, −z and −y sides; SERVO5 = ESC. 1500 µs = 0°; ±400 µs = ±15° servo = ±10° vane through a 1.5 : 1 lever; hard stops at ±15° vane" | |
| Sensing | Which signals exist; rate, resolution, latency, format | "Pixhawk IMU logged at 1 kHz raw (INS_LOG_BAT_MASK), EKF attitude at 400 Hz; bench temperatures on the Arduino at 10 Hz to CSV" | |
| Propulsion | Throttle PWM ↔ thrust curve; spool-up time constant; current at the test throttle | Filled in week 6 from thrust-stand measurements; placeholders until then | |
| Geometry and mass | Body architecture; total mass against the flight mass budget; CG and CP positions; the stand's pivot positions; $d$, $L$ and $J$ about the two tilt axes (pitch and yaw), and $J$ about roll; the vane geometry (span, chord, hinge position, distance from the fan exit, radius from the fan axis) | Numbers with tolerances and a source (CAD or measured); updated whenever the print changes. "Flight mass at most 1.5 kg including the battery (planning figure; checked against the thrust stand in week 6)" | |
| Safety and arming | E-stop behaviour, arming sequence, failsafe on signal loss, who may press what, on the stand and in flight | "Stand: E-stop opens the contactor coil; tether always on before arming. Flight: motor emergency stop on its own transmitter switch; RC failsafe → motor off" | |
| Flight configuration | Radio channels and switches; flight modes; frame class and output assignment; GPS (stretch goal) | "Mode switch: Stabilize / AltHold; kill switch on its own channel; SingleCopter frame (`FRAME_CLASS` 8), vanes on SERVO1–4, ESC on SERVO5" | |
| Logs and data | File format, naming, storage location, who analyses | "ArduPilot .bin + Arduino CSV, `YYYYMMDD_testNN_*`, shared drive folder /logs" | |

### 4.2 An independent path for the control group

**Status: under way.** Procurement has started. Until the parts arrive, the control group works on things that need neither the EDF nor printed parts:

1. **Plant model** from first principles and datasheet numbers, updated as group 1's numbers arrive.
2. **Simulation** of the model with the candidate controllers.
3. **SITL** (software-in-the-loop): the real ArduPilot firmware running on a laptop against a simulated vehicle, to learn its parameters, outputs and logs before the Pixhawk arrives.
4. **Desk rig**, once the servos and the Pixhawk arrive: the Pixhawk and a vane servo on a hinged plank, closing the loop from IMU to servo weeks before the fan runs; then all four servos, to check the output mapping and each vane's direction.

Details and first steps: Part 2.

### 4.3 Protected integration time

**Status: agreed.** Weeks 9–12 are joint work: both groups, one rig, one test log, and no new features. If integration finishes early, the spare time goes to the controller comparison.

**Proposed 2026-09-24, to agree:** with the outdoor test added, split the four weeks. Weeks 9–10: the stand (the comparison, then roll checks with the roll lock removed). Week 11: outdoors (tethered hover; free hover only if the tethered hover passes). Week 12: no flying; repairs and expo preparation.

### 4.4 Integrator

**Status: agreed.** There is no standing integrator role. The groups meet regularly and discussion is open, so most cross-group questions get settled there. When an issue needs a single owner across both groups ("is this a linkage problem or a gain problem?"), `[name]` from the control group takes it.

Named owners for the individual seam items (§3, risk 3) are still to be agreed (§6).

### 4.5 What "done" means for each handoff

**Status: draft, to be agreed on 2026-09-23.**

A **number** in §5 counts as delivered when it has units, a tolerance and a source (CAD estimate or measurement), and is written into the §4.1 table.

The **rig** counts as ready when every box is ticked:

- [ ] Rig assembled
- [ ] All four vane servos respond to PWM over the full range, with each vane's angle and direction measured against the contract
- [ ] IMU axes verified by tilting the body by hand
- [ ] Thrust-stand curve logged
- [ ] E-stop tested
- [ ] A 30-second open-loop run at 30 % throttle, with logs

Until every box is ticked, the control group stays on the desk rig.

### 4.6 Test ladder and flight gates

**Status: proposed 2026-09-24, to agree.** The rocket climbs one rung at a time. Each rung has a written pass/fail gate that must be met before the next:

| Rung | What it proves | Gate to the next rung |
|---|---|---|
| 1. Simulation and SITL | Model, controllers and flight configuration work in software | Stable in simulated step and push tests; kill switch and failsafe behave in SITL |
| 2. Desk rig (servos, no fan) | Signs, servo lag, first closed loop | Balances the plank; signs verified |
| 3. Rocket on the stand (fan on, shielded) | Attitude control under real thrust; the PID-versus-LQR comparison | Bench pass criteria met (Part 2 §7) |
| 4. Tethered outdoor hover | Flight: tilting and drifting for real, but the rocket can't fly away | Stable tethered hover and clean landings (numbers to agree) |
| 5. Free outdoor hover and landing (stretch goal) | The real thing | Rung 4 passed; permission covers free flight |

**Ready for the outdoor test:** every box before rung 4.

- [ ] Stand results for the comparison logged and backed up
- [ ] Flight mass within the budget; thrust-stand data show enough margin to hover and steer
- [ ] The vanes hold roll on the stand with the roll lock removed (no wind-up), with travel left over for pitch and yaw
- [ ] Landing legs fitted
- [ ] Radio kill switch and RC failsafe tested on the stand (transmitter off → motor stops)
- [ ] Pre-flight checklist run: tether, site, keep-out zone, wind and temperature limits
- [ ] Written confirmation from HCT (and the GCAA where required) for the site and date

## 5. Deliveries between the groups, by week

Week numbers count from the week of 21 September 2026.

| Week | From group 1 to group 2 | Why then |
|---|---|---|
| 1 | Contract agreed (§4.1); roll-actuator and CG decisions (§6). The actuator was settled on 2026-09-28: four vanes | Everything downstream depends on them |
| 2 | **First delivery, from CAD:** suggested body architecture; total mass $m$ against the flight mass budget; CG and CP positions; $d$, $L$ and $J$ about the two tilt axes, and $J$ about roll; the stand's pivot positions | The plant model's numbers; the weight limit shapes every part |
| 3 | The vane design: span, chord, hinge position, distance from the fan exit, linkage ratio and travel limits for each vane. The servos, Pixhawk, UBEC and wiring go to the desk rig as soon as they arrive | Servo identification and the first closed loop. The vanes sit in the exhaust, so they are designed before the body freezes |
| 6 | Thrust-stand data, with the vanes fitted: thrust vs throttle, spool-up time, current, temperature, the fan's reaction torque, and the torque the vanes produce | Replaces the model's guessed thrust and spool-up time; checks the flight mass budget, and whether the vanes' roll authority covers the fan's torque with travel to spare (§6, item 4) |
| 8 | Measured mass properties of the assembled body (CG by balancing it, $J$ by a swing test); rig passes the §4.5 checklist | CAD numbers are estimates; the model is fitted to measured ones. Start of integration |
| 9–10 | Joint stand tests, two days per week, integrator on call | The controller comparison; roll checks with the roll lock removed |
| 11 | Outdoor tests, once the §4.6 checklist is complete: tethered hover; free hover only if it passes | The outdoor test |
| 12 | No flying: repairs, spares, expo preparation | A crash can't take out the expo display |

The weeks 9–12 split is the 2026-09-24 proposal in §4.3, still to agree.

**Why CP and also $d$, $L$, $J$.** On the tethered pivot the body barely moves through the air, so aerodynamic forces, and with them the CP, hardly enter the bench model. The CP is recorded anyway: the body design already produces it, and it matters if the body ever flies free. The model itself runs on $d$, $L$ and $J$.

**From group 2 to group 1, by week 3:** the controller's actuator requirements (the servo rate, range and resolution it needs), so the linkage ratio isn't chosen blind; the sensor-placement request: IMU near the CG (in the flight-representative stand position the pivot is there too), rigidly mounted, away from the fan's vibration path; the vane travel and rate the controller needs, and the roll torque the vanes must deliver on top of the tilt demands; and where the radio receiver (and, for the stretch goal, the GPS) must sit.

## 6. Still open: agenda for 2026-09-23 (updated 2026-09-24 and 2026-09-30)

1. **Fill in the contract** (§4.1).
2. **Agree the "done" definitions** (§4.5) and the flight gates (§4.6).
3. **Rig layout. Settled 2026-09-24: one build.** The rocket carries the vanes and the Pixhawk, bolts into a stand that provides the pivot, and is flown outdoors.
4. **Roll (the twist). Settled 2026-09-28: four exhaust vanes.** On 2026-09-24 two options were listed for flight, because nothing locks roll in the air and a tether doesn't stop spin: a servo-driven pair of exhaust tabs, which kept the gimbal but needed a custom output mapping, or four exhaust vanes, which replace the gimbal and use ArduPilot's stock SingleCopter mapping that BB Projects flew. The team chose the vanes, and may return to the gimbal after the expo (git tag `gimbal-baseline`). On the stand, roll can still be locked at the pivot (for example with a universal joint) for the first tilt tests.

   **Still open: roll authority.** The fan's net reaction torque, after its stator vanes, is estimated at 0.05–0.25 N·m at hover for the 80 mm fan (order of magnitude only). That is enough to spin a free rocket up to a turn per second in well under a second. All four vanes turned the same way make roll torque, but the same four vanes also make pitch and yaw, so each vane's travel is shared. A first estimate, for vanes of the size that fits the jet (about 20 mm of span between the motor hub and the duct wall, 30 mm chord, centred about 30 mm from the fan axis), gives roughly 0.02–0.04 N·m of roll torque at ±10° and about 0.1 N·m near the useful limit of such stubby plates (25–30°). That is below or at the low end of the disturbance, with little travel left for the tilts. Both the torque and the vanes' authority scale with thrust, so the ratio is the same at every throttle. Therefore:
   - measure the fan's torque before the vane geometry freezes. The thrust stand has it in week 6 (§5); a bare fan clamped so it can turn, pressing an arm on a scale, gives it sooner;
   - if the torque is large, cancel its steady part with fixed anti-swirl vanes at the exit (an extra stator) and keep the moving vanes for control. Longer chords and more travel are the other levers;
   - ArduPilot calls this axis yaw, so its yaw gains (`ATC_RAT_YAW_*`), which the gimbal plan zeroed, must be active in flight. On the stand with roll locked, zero them.

   These vane sizes are a first estimate from the jet's geometry, not the team's design. **Two EDFs: settled 2026-09-24.** With one build, a second EDF would only be a spare. Two identical units can't make a counter-rotating pair, which needs one mirror-image rotor.
5. **CG relative to the pivot:** above the pivot, the body is an inverted pendulum, unstable without control, which is the real problem and the honest demo. Below, it hangs stably on its own, and a visitor can't tell whether the loop is closed. The recommendation is above, with the tether as the safety net. **Updated 2026-09-24:** because the same rocket will fly, make the pivot position adjustable. With the pivot at the CG, the stand has the same tilt equations as free flight (gravity has no lever arm), so gains tuned there carry over. With the CG above the pivot, it is the inverted pendulum: the demo, and a harder test.
6. **Owners for the seam items:** ESC configuration; Pixhawk and servo wiring; the safety chain (E-stop → contactor → fuse). The arming sequence, failsafe settings, pre-arm checklist, radio kill switch and flight modes already sit with the control group, since it commands the actuators.
7. **Name the group-1 liaison** who reports the numbers (§1).
8. **Flight mass budget (added 2026-09-24):** about 1.5 kg including the battery. It was set when the fan was 70 mm (about 22 N, the weight of 2.2 kg), keeping a margin of about 1.5 times the weight for steering. The 80 mm fan now planned is taken to give about 31 N (3.2 kgf; the planning figure used since 2026-09-24, to be confirmed on the thrust stand), so 1.5 kg leaves a margin of about 2.1; at the same 1.5 margin the limit would be about 2.1 kg. Update the figure here if the team changes it. Split the budget across the parts in week 2, now including four vane servos and their linkages; the thrust stand confirms it in week 6.
9. **Flight parts missing from the BOM (added 2026-09-24):** a radio transmitter and receiver (the in-flight kill switch) and landing legs; for the stretch goal, a GPS module and a telemetry radio. Price them and add them to the BOM. (The separate roll actuator listed here before is no longer needed: the vanes cover roll.)
10. **Outdoor test (added 2026-09-24):** site, date (week 11 proposed), and written confirmation from HCT and, where required, the GCAA. The team expects no difficulty. However, GCAA Safety Decision 2026-03 (27 March 2026) suspended recreational drone flights, and on 2026-09-23 there was no confirmation that the suspension had been lifted, so ask in week 2.
