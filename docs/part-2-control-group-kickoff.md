# Part 2: Control group kickoff — EDF Thrust-Vector Control Testbed

*Split out on 2026-09-23 from `team-split-and-control-group-kickoff.md` (§6 and §8, trimmed and updated for split C). For the control group. Who delivers what, and when, is in [Part 1](part-1-team-split-and-interface-contract.md). **Updated 2026-09-24** for one build that is also flown outdoors: §1.1, §2, §3, §4, §7, §8, §9. **Updated 2026-09-30** for the switch from the two-axis gimbal to four exhaust vanes, one servo each: §1 (the actuator term), §1.1, new §1.2, §3, §4, §5, §6, §9. The gimbal-era version is under the git tag `gimbal-baseline`. Axis names follow the group's convention (Part 1 §4.1): roll is the twist about the long axis, which ArduPilot calls yaw.*

**Where to start.** Procurement is under way, so the first weeks happen in simulation:

| When | Do |
|---|---|
| This week | Install the simulator (§4, route A); decide where the controller runs (§3) |
| Weeks 1–2 | Write the plant model (§1) with placeholder numbers; swap in group 1's numbers when they arrive |
| Weeks 2–3 | Controllers in simulation (§2); WSL2 set up (§4, route B); log scripts and test records (§7); pre-arm checklist (§8) |
| By week 3 | Send group 1 the actuator requirements and the sensor-placement request (Part 1 §5) |
| When the servos and Pixhawk arrive | Desk rig (§6) |
| By week 6 | Flight configuration rehearsed in SITL: flight modes, radio kill switch, failsafe, the four vane outputs (§4, §8) |
| Weeks 9–11 | Stand tests, then the outdoor test (Part 1 §4.6) |

## Good to know beforehand

**What this assumes you know:** Part 1 §1, and roughly what a control loop and a PID controller are. The equations in §1 use basic calculus; the text around them can be followed without it.

| Term | Meaning here |
|---|---|
| Plant model | Equations predicting how the body tilts when the vanes move; the controller is designed against them |
| Lift slope $a$ | How much sideways force a vane makes per radian of deflection, as a coefficient: force $= q\,S\,a\,\delta$ for small angles |
| Mixing | Turning "this much torque about roll, pitch and yaw" into four vane commands (§1.2). ArduPilot's mixer does it |
| State-space form | The same equations written as $\dot{x} = \mathbf{A}x + \mathbf{B}u$: state variables $x$, and how the input $u$ changes them |
| LQR | Linear-quadratic regulator: a feedback gain computed from the state-space model, trading angle error against servo effort |
| SITL | Software-in-the-loop: the real ArduPilot firmware running on a laptop against a simulated vehicle |
| Desk rig | A vane servo and the Pixhawk on a hinged, weighted plank, then all four servos: real hardware, no fan |

---

## 1. The plant model (weeks 1–2)

Treat the body as rigid, pivoting about a fixed point. The fan's thrust $T$ runs along the body's long axis. The vanes sit in the fan's exhaust, a distance $L_v$ from the pivot. Turning a vane by an angle $\delta$ deflects part of the jet, and the jet pushes back on the vane with a sideways force. For small angles that force is

$$f = q\,S\,a\,\delta, \qquad q = \frac{T}{2A}$$

where $q$ is the jet's dynamic pressure (obtained from the thrust, with $A$ the fan's exit area), $S$ is one vane's area, and $a$ is its lift slope.

To tilt the body about one axis, the two vanes on opposite sides of the jet turn so that both push the tail the same way (§1.2 gives the full mixing). Together they make a side force $k\,\delta$ with $k = 2\,q\,S\,a$, and a torque about the pivot of $k\,L_v\,\delta$. For one tilt axis (angle $\theta$ from vertical), with the CG a distance $d$ above the pivot:

$$J\,\ddot{\theta} = k\,L_v\,\delta \;+\; m\,g\,d\,\sin\theta \;-\; c\,\dot{\theta} \;+\; \tau_{\text{dist}}$$

The gravity term is positive because the CG is above the pivot: that is what makes the body an inverted pendulum. $c$ is damping at the pivot and $\tau_{\text{dist}}$ any disturbance torque. Linearised about $\theta = 0,\ \delta = 0$:

$$J\,\ddot{\theta} = b\,\delta + m\,g\,d\,\theta - c\,\dot{\theta}, \qquad b = k\,L_v = \frac{T\,S\,a\,L_v}{A}$$

This is the same shape as the gimbal version: only the actuator term has changed, from $T L \delta$ to $b\,\delta$. Three things about $b$ matter for the controller:

- **It is proportional to thrust**, through $q$, as the gimbal's $T L$ was. Gains tuned at one throttle are too lively at higher thrust and sluggish at lower. ArduPilot's SingleCopter mixer divides its flap commands by thrust (never by less than half) for this reason; a custom controller must do the same.
- **It saturates.** A vane is a short, stubby plate. Its force stops growing somewhere around 25–30° of deflection. Model a hard limit on $\delta$ and keep commands well inside it.
- **Roll shares the travel.** Each vane also carries part of the roll command (§1.1, §1.2), so the tilt axes get whatever travel roll leaves.

Add the two actuator lags that student models usually leave out: the servo, with time constant $\tau_s$ and a rate limit, and the fan's spool-up, with time constant $\tau_T$. Here $\delta$ is the vane's angle; the servo turns it through a linkage:

$$\dot{\delta} = \frac{\delta_{\text{cmd}} - \delta}{\tau_s}, \quad |\dot{\delta}| \le \dot{\delta}_{\max} \qquad\qquad \dot{T} = \frac{T_{\text{cmd}} - T}{\tau_T}$$

With state $x = [\theta,\ \dot\theta,\ \delta]^T$, input $u = \delta_{\text{cmd}}$ and output $\theta$ (from the IMU):

$$\dot{x} = \mathbf{A} x + \mathbf{B} u, \qquad \mathbf{A} = \begin{bmatrix} 0 & 1 & 0 \\ \dfrac{m g d}{J} & -\dfrac{c}{J} & \dfrac{b}{J} \\ 0 & 0 & -\dfrac{1}{\tau_s} \end{bmatrix}, \quad \mathbf{B} = \begin{bmatrix} 0 \\ 0 \\ \dfrac{1}{\tau_s} \end{bmatrix}$$

(Bold $\mathbf{A}$ is the state matrix; plain $A$ is still the fan's exit area.) Model the two tilt axes, pitch and yaw, separately first (they decouple at small angles), then add roll (§1.1).

| Symbol | Meaning | Use now | Replace with |
|---|---|---|---|
| $m$, $d$, $L_v$, $J$ | Mass; pivot-to-CG; pivot-to-vanes; inertia about the pivot | Group 1's first delivery, from CAD (week 2) | Measured on the assembled body (week 8) |
| $T$ | Thrust at the test throttle | 80 mm fan (BOM row 1): about 31 N maximum, the planning figure used since 2026-09-24. Hover needs $T = mg$, about 15 N at 1.5 kg | Thrust stand (week 6) |
| $A$, $S$, $a$ | Fan exit area; one vane's area; vane lift slope | $A \approx 45\ \text{cm}^2$ for an 80 mm fan; $S$ from group 1's vane design (week 3); $a \approx 1$–$2$ per radian for a stubby flat plate | Fit $b$ directly: vane torque on the thrust stand (week 6), then logged responses |
| $\tau_T$ | Fan spool-up time constant | 0.2–0.4 s | Thrust stand (week 6) |
| $\tau_s$, $\dot\delta_{\max}$ | Servo lag and rate limit, at the vane | The vane servo in the four-vane BOM (take the figure from its linked listing): about 0.09 s per 60° at 7.4 V with no load, so about $670^\circ/\text{s}$ at the servo and about $440^\circ/\text{s}$ at the vane through a 1.5 : 1 linkage | Desk-rig step tests (§6) |
| $c$ | Damping at the pivot | A small guess; check how much it matters | Fitted to logged responses |

**Deliverable:** a one-page model note (equations, and this table with sources) and an implementation in MATLAB/Simulink or Python.

### 1.1 From the stand to free flight (added 2026-09-24)

The same rocket will fly, and the stand's pivot will be adjustable (Part 1 §6, item 5), so the tilt model comes in three versions. The pivot now moves, so measure the lever arm from the CG instead: $L_{\text{CG}}$ is the CG-to-vanes distance. With the pivot a distance $d$ below the CG, §1's $L_v$ becomes $L_{\text{CG}} - d$, and §1's $J$ becomes $J_{\text{CG}} + m d^2$ (the parallel-axis theorem).

| Configuration | Tilt equation (one axis, linearised) | Use |
|---|---|---|
| Stand, CG a distance $d$ above the pivot | $(J_{\text{CG}} + m d^2)\,\ddot\theta = k\,(L_{\text{CG}} - d)\,\delta + m g d\,\theta - c\,\dot\theta$ | The inverted-pendulum demo; a harder test |
| Stand, pivot at the CG ($d = 0$) | $J_{\text{CG}}\,\ddot\theta = k L_{\text{CG}}\,\delta - c\,\dot\theta$ | Tuning that carries over to flight |
| Free flight | $J_{\text{CG}}\,\ddot\theta = k L_{\text{CG}}\,\delta$ | The outdoor tests |

With the pivot at the CG, gravity has no lever arm, exactly as in flight; only the pivot friction $c$ differs. Gains tuned on the inverted configuration were tuned for a harder plant, so re-check them with the pivot at the CG before flying.

Flight adds two things the stand locks out:

- **Sideways motion.** A tilted thrust pushes the rocket sideways. At hover ($T \approx mg$), $\ddot x \approx g\,\varphi$, where $\varphi$ is the thrust's tilt from vertical. With vanes that is essentially the body's tilt: the thrust stays along the body axis. The vanes' own side force is small, and at first it pushes the other way, because to lean the nose one way they push the tail the other. Holding position needs an outer loop around the attitude loop: the pilot for the tethered hover, and ArduPilot's GPS position modes for the free-hover stretch goal.
- **Roll (the twist).** $J_x\,\dot p = \tau_{\text{fan}} + 4\,q\,S\,a\,r\,\delta_r$, where $p$ is the roll rate, $J_x$ the inertia about the long axis, $r$ the vanes' mean distance from the fan axis, and $\delta_r$ the part of each vane's deflection given to roll (all four turned the same rotational way, §1.2). The fan's steady torque needs a steady trim deflection, and that travel is then not available for pitch and yaw (Part 1 §6, item 4). A simple rate loop is enough, and it isn't part of the PID-versus-LQR comparison. In ArduPilot this is the yaw axis with the sign reversed ($p = -\omega_{z,\text{AP}}$, the gyro's $z$ reading), run by the stock yaw rate loop (`ATC_RAT_YAW_*`).

### 1.2 How four vanes share three axes (added 2026-09-30)

Number the vanes in ArduPilot's SingleCopter order, which is also the order of outputs SERVO1–4: vane 1 on the $+z$ side of the jet (the Pixhawk arrow's side), vane 2 on $+y$, vane 3 on $-z$, vane 4 on $-y$. Count each vane's deflection $\delta_i$ as positive when it pushes the body the $+$roll way round. Then:

- **Roll:** all four the same way. Torque $4\,q\,S\,a\,r\,\delta_r$; the side forces cancel.
- **Pitch** (about $y$): vanes 2 and 4, which sit on the $\pm y$ sides and push along $z$, turn opposite ways in this count, so both push the tail the same way along $z$. Their roll torques cancel.
- **Yaw** (about $z$): vanes 1 and 3, in the same way, push the tail along $y$.

So the four commands are

$$\delta_1 = \delta_r + \delta_\psi, \qquad \delta_3 = \delta_r - \delta_\psi, \qquad \delta_2 = \delta_r + \delta_\theta, \qquad \delta_4 = \delta_r - \delta_\theta$$

where $\delta_\theta$ and $\delta_\psi$ are the pitch and yaw demands, and the overall signs of the tilt terms depend on where the vanes sit relative to the pivot. Fix them in the contract (Part 1 §4.1) and check them on the desk rig. This is exactly what ArduPilot's SingleCopter mixer does: ArduPilot's roll (our yaw) moves the front and back flaps, ArduPilot's pitch moves the right and left flaps, and ArduPilot's yaw (our roll) moves all four. The mixer is therefore stock. The work is getting each vane's direction right.

**The catch is shared travel.** Every vane carries roll plus one tilt, so with a travel limit $\delta_{\max}$ each vane needs $|\delta_r| + |\delta_\theta| \le \delta_{\max}$ (or $|\delta_\psi|$ for vanes 1 and 3). A large roll trim leaves little room to steer. When a vane saturates, ArduPilot's mixer has to give something up. Watch for vane commands at their limits in the logs.

## 2. Controllers in simulation (weeks 2–3)

Build the ladder you will later compare on hardware:

1. **PID on attitude:** the baseline, and what stock ArduPilot runs. Tune it by hand and note what limits it (usually the servo rate limit).
2. **LQR:** a state-feedback gain $u = -Kx$ from a cost on angle error and servo effort. It needs $\dot\theta$ (the gyro gives it) and $\delta$ (servo feedback or the model).
3. *Optional:* **LQR with integral action**, for a steady bias such as thrust misalignment; or a **gain-scheduled** LQR across throttle, since $T$ changes the plant.

Run all three through the tests you will repeat on hardware: a step in the reference, a push (impulse torque), a throttle change. Record settling time, overshoot and peak servo rate. That table, repeated on the stand in weeks 9–10, is the comparison the paper promises. If time allows, run it in both stand positions; the runs with the pivot at the CG are the ones that speak to flight (§1.1).

## 3. Where the controller runs (decide this week)

| Path | Strength | Weakness | Use it for |
|---|---|---|---|
| **Stock ArduPilot** (SingleCopter frame, PID gains as parameters) | Closes the loop in days; logging, failsafes and arming built in. SingleCopter's four flaps are the four vanes, so its stock mixer fits (§1.2) | PID only. ArduPilot's yaw loop is our roll: zero its gains while roll is locked on the stand, and have them active in flight | First closed loop on hardware; the safe demo; the outdoor test |
| **ArduPilot custom controller** (`CC_TYPE`, switchable in flight) | Your controller inside the firmware, stock PID as the fallback, everything logged | Needs ArduPilot's build tools and C++ (§4, route B) | The LQR comparison |
| **Off-board** (a laptop or the Arduino computes $u$ and sends servo commands) | Quickest to write and change | 10–50 ms of latency and jitter against a servo lag of a few tens of ms: risky for an inverted pendulum | Identification runs and open-loop sweeps, not the closed loop |
| **Arduino as flight controller** (IMU → Mega → four servos) | Total control, simple | You write the estimator, mixing, logging, safety and arming yourselves. The four-vane BOM has no separate IMU for the Mega (the gimbal BOM's BNO085 row is gone), so this path needs one added | Only if the ArduPilot build proves too steep by week 4 |

**Recommendation:** stock ArduPilot first, the custom controller second as the research path, and the Arduino for bench identification. Outdoors, fly on ArduPilot only: its failsafes, arming checks and logs are what a flight needs. The off-board and Arduino paths stay on the bench.

## 4. Getting started with SITL

SITL runs the real ArduPilot firmware on your laptop against a simulated vehicle. Mission Planner, ArduPilot's ground-control program, connects to it as it would to a Pixhawk on USB: same parameters, arming checks, outputs and logs. SITL's `singlecopter` is a free-flying vehicle with one fan and four flaps. Since the switch to vanes, that is the rocket's own actuator layout, so the output mapping, mixer signs and failsafes you learn on it are the ones you will fly. It still won't teach you the rig's physics: its mass, inertia and flap sizes are defaults, and it has no pivot. Learn the software on it; don't tune the rig's gains on it. Now that the rocket will fly, SITL is also the place to rehearse the outdoor test: flight modes, the radio kill switch, the failsafe (`SIM_RC_FAIL` simulates losing the transmitter), and, for the stretch goal, GPS position modes. Its vehicle still isn't your rocket, so the rule about gains stands.

### Route A: Mission Planner's simulator (Windows; start here, nothing to build)

1. Install [Mission Planner](https://ardupilot.org/planner/docs/mission-planner-installation.html).
2. **Simulation** tab: type `singlecopter` in the **Model** box (it accepts any SITL model name) and tick **Wipe** to start from default parameters.
3. Click the copter (multirotor) icon and choose **Stable**. Mission Planner downloads the simulator, starts it and connects.
4. **Config → Full Parameter List:** check that `FRAME_CLASS` is `8` (SingleCopter); if not, set it and restart.
5. First exercises:
   - **Outputs:** SERVO1–4 drive the four flaps (Motor 1–4) and SERVO5 the fan (Motor 5). These are the rocket's four vane outputs. Give a roll, a pitch and a yaw stick input in turn (ArduPilot's names), and note which outputs move and which way; compare with §1.2.
   - **Fly:** **Actions** tab → select **Guided** → **Set Mode** → **Arm/Disarm**; then right-click the map → **Takeoff** within 15 s, or it disarms. Watch `ch1out`–`ch5out` on the **Status** tab.
   - **Gains:** change an attitude gain (`ATC_RAT_RLL_P`, `ATC_RAT_PIT_P`, …) and watch the effect.
   - **Logs:** **DataFlash Logs → Download DataFlash Log Via Mavlink**, then open the log in the UAV Log Viewer (§5).

### Route B: WSL2 and `sim_vehicle.py` (by week 2, for the custom controller)

The custom controller is compiled into the firmware with ArduPilot's own tools, which run on Linux; WSL2 runs Ubuntu inside Windows. Once, in PowerShell as administrator, then restart and open **Ubuntu** from the Start menu:

```powershell
wsl --install
```

In the Ubuntu terminal:

```bash
sudo apt-get update
sudo apt-get install git
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
cd ArduCopter
sim_vehicle.py -v ArduCopter -f singlecopter -w --console --map   # -w: fresh parameters; the first build is slow
```

- Clone into the Ubuntu home folder, not under `/mnt/c/`: builds are much faster there.
- Under WSL2, `sim_vehicle.py` sends MAVLink to Windows on UDP port 14550, so connect Mission Planner with **UDP**, port **14550**. Windows 11 shows the map and console windows as is; Windows 10 needs an X server.
- The custom-controller interface is on by default in SITL. ArduPilot's example, typed in the console: `param set CC_TYPE 2`, `param set CC_AXIS_MASK 7`, `param set RC6_OPTION 109`; RC channel 6 then switches between the stock and the custom controller. The example controller is "tested only lightly": fine in SITL, careful on hardware.
- On macOS or Linux, skip `wsl --install`, follow ArduPilot's setup page for your system, and use the MAVProxy console or QGroundControl instead of Mission Planner.

References (ArduPilot): [SITL on Windows (WSL)](https://ardupilot.org/dev/docs/sitl-on-windows-wsl.html), [Linux setup](https://ardupilot.org/dev/docs/building-setup-linux.html), [Mission Planner simulation](https://ardupilot.org/planner/docs/mission-planner-simulation.html), [Adding a custom controller](https://ardupilot.org/dev/docs/copter-adding-custom-controller.html).

## 5. Browser tools until the parts arrive

Row numbers below are those of the four-vane BOM (`bom/Four_Vane_EDF_BOM_Current.docx`).

- **Pixhawk 6C (BOM row 8): SITL (§4).** Nothing emulates it in a browser for this vehicle yet; ArduPilot's browser build of SITL, merged in September 2026, covers planes only.
- **Logs: [UAV Log Viewer](https://plot.ardupilot.org) and [ArduPilot WebTools](https://firmware.ardupilot.org/Tools/WebTools/)** (PID Review, Filter Review). They run in the browser, and the log stays on your computer. Practise on SITL logs.
- **Arduino Mega (row 32), vane servos (row 16): [Wokwi](https://wokwi.com).** It simulates an Arduino Mega, servos, an MPU6050 IMU and a logic analyser. Practise the bench-identification code: timed servo steps, PWM pulse widths on the logic analyser, CSV logging over serial. Limits: the servo is ideal (no lag, backlash or torque limit). The four-vane BOM has no separate IMU for the Arduino, so the MPU6050 is practice only.
- **Model and controllers (§1–§2): [MATLAB Online](https://matlab.mathworks.com) with Simulink, through HCT's licence** (sign in from the [HCT access page](https://www.mathworks.com/academia/tah-portal/higher-college-of-technology-40589700.html)), **or [Google Colab](https://colab.research.google.com)**: run `!pip install control` in a cell, and `control.lqr` works with no further setup.
- **ESC and EDF (rows 1–2):** nothing useful to simulate; the thrust curve comes from group 1's thrust stand.

## 6. The desk rig (when the servos and the Pixhawk arrive)

Bolt the Pixhawk and one vane servo to a plank, hinge it with a weight above the hinge so it wants to fall, and link the servo to it through a lever so it can push it back. No fan. It gives you:

- **Servo characterisation:** log step commands; fit $\tau_s$ and the rate limit; measure deadband and backlash through the linkage. These replace the datasheet values in §1. Repeat for each of the four servos: they are four actuators, not one.
- **Sign and axis check:** tilt the rig by hand; the servo must push the right way. A reversed sign is one of the most common causes of a first-run crash.
- **Mixer and vane-direction check, all four servos:** tape a card "vane" to each servo horn and label it with its output (SERVO1–4). Tilt and twist the Pixhawk by hand and check against §1.2: a tilt moves the pair that should push it back, and a twist moves all four the same rotational way. With four vanes there are four chances to get a direction wrong.
- **First closed loop:** stock ArduPilot balancing the plank. It is a small, safe inverted pendulum, and a demonstration in its own right if the fan rig slips.

## 7. Logs and test records (week 3)

- Scripts that put ArduPilot `.bin` logs (pymavlink or MATLAB's UAV Toolbox) and the Arduino CSVs on one time base, with standard plots: attitude against reference, servo command, throttle, current, temperature. Build them on SITL logs now.
- A test record for every run: date, rig configuration, starting battery voltage, controller and gains, what was commanded, what happened, tether state, log file names. This is the dataset the model is fitted from. Outdoor runs add: site, wind, air temperature, GPS status, tether length, and the permission reference.
- The expo experiment matrix (controllers × tests × metrics), with pass criteria written before the first run, and the gates of Part 1 §4.6.

## 8. Safety

The control group commands the actuators, so it owns the arming sequence, the failsafe settings, the pre-arm checklist and the E-stop test. Write the checklist in week 2, run it on the desk rig, and reuse it on the fan rig.

**For the outdoor test (added 2026-09-24),** the control group also owns the flight configuration:
- a radio kill switch: a motor emergency stop on its own transmitter switch;
- the RC failsafe action: decide between stopping the motor and landing, then test it;
- a geofence for the free-hover stretch goal;
- a pre-flight checklist: the pre-arm checklist plus site, tether, keep-out distance, wind and temperature.

Test the kill switch and the failsafe on the stand before the rocket leaves it.

## 9. What the simulations won't show

- **Linkage play:** backlash makes a deadband the LQR will hunt in, and there are now four linkages. Measure each on the desk rig.
- **Vanes in the jet:** a vane's force depends on the jet's speed, so it weakens at low throttle; it stops growing near stall; and the vanes cost some thrust as drag. Measure thrust and vane torque on the thrust stand with the vanes fitted.
- **Battery voltage:** the same throttle gives less thrust at 21 V than at 25 V, so the plant drifts during a session. Log the voltage.
- **Fan torques:** the reaction torque disturbs roll, and a pitch rate makes a yaw torque through the spinning rotor (both in the group's names). Small, but not zero.
- **IMU vibration:** what limited the nearest comparable student project (Maribor). Check the vibration metrics before trusting attitude.
- **Latency:** about 5–10 ms from IMU to servo command inside ArduPilot, plus the servo's own lag. Fine at 400 Hz; fatal for an off-board loop over a slow link.
- **The tether:** slack, it's invisible; taut, it's a spring in the plant. Note its state in every test record.
- **Wind (outdoors):** gusts push on the body, and the centre of pressure starts to matter.
- **Heat (outdoors):** sun and air temperature heat the LiPo and the ESC. Test early in the day and log temperatures.
- **Ground effect:** in the last few tens of centimetres before touchdown, the fan's thrust changes.
- **Compass:** heading matters once roll is controlled (ArduPilot: yaw), and the fan's high-current leads disturb the magnetometer. Twist them and route them away from the Pixhawk.
- **SITL's vehicle:** the same four-flap layout as your rocket, but with default mass, inertia and flap sizes, and no pivot (§4).
