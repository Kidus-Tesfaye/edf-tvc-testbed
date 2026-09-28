# Part 2: Control group kickoff — Two-Axis Gimballed EDF Control Testbed

*Split out on 2026-09-23 from `team-split-and-control-group-kickoff.md` (§6 and §8, trimmed and updated for split C). For the control group. Who delivers what, and when, is in [Part 1](part-1-team-split-and-interface-contract.md). **Updated 2026-09-24** for one build that is also flown outdoors: §1.1, §2, §3, §4, §7, §8, §9.*

**Where to start.** Procurement is under way, so the first weeks happen in simulation:

| When | Do |
|---|---|
| This week | Install the simulator (§4, route A); decide where the controller runs (§3) |
| Weeks 1–2 | Write the plant model (§1) with placeholder numbers; swap in group 1's numbers when they arrive |
| Weeks 2–3 | Controllers in simulation (§2); WSL2 set up (§4, route B); log scripts and test records (§7); pre-arm checklist (§8) |
| By week 3 | Send group 1 the actuator requirements and the sensor-placement request (Part 1 §5) |
| When the servos and Pixhawk arrive | Desk rig (§6) |
| By week 6 | Flight configuration rehearsed in SITL: flight modes, radio kill switch, failsafe, yaw output (§4, §8) |
| Weeks 9–11 | Stand tests, then the outdoor test (Part 1 §4.6) |

## Good to know beforehand

**What this assumes you know:** Part 1 §1, and roughly what a control loop and a PID controller are. The equations in §1 use basic calculus; the text around them can be followed without it.

| Term | Meaning here |
|---|---|
| Plant model | Equations predicting how the body tilts when the gimbal moves; the controller is designed against them |
| State-space form | The same equations written as $\dot{x} = Ax + Bu$: state variables $x$, and how the input $u$ changes them |
| LQR | Linear-quadratic regulator: a feedback gain computed from the state-space model, trading angle error against servo effort |
| SITL | Software-in-the-loop: the real ArduPilot firmware running on a laptop against a simulated vehicle |
| Desk rig | The two servos and the Pixhawk on a hinged, weighted plank: real hardware, no fan |

---

## 1. The plant model (weeks 1–2)

Treat the body as rigid, pivoting about a fixed point, with the fan's thrust $T$ applied at distance $L$ from the pivot and steered through gimbal angle $\delta$. For one axis (pitch angle $\theta$, positive nose-up), with the CG a distance $d$ above the pivot:

$$J\,\ddot{\theta} = T\,L\,\sin\delta \;+\; m\,g\,d\,\sin\theta \;-\; c\,\dot{\theta} \;+\; \tau_{\text{dist}}$$

The gravity term is positive because the CG is above the pivot: that is what makes the body an inverted pendulum. $c$ is damping at the pivot and $\tau_{\text{dist}}$ any disturbance torque. Linearised about $\theta = 0,\ \delta = 0$:

$$J\,\ddot{\theta} = T\,L\,\delta + m\,g\,d\,\theta - c\,\dot{\theta}$$

Add the two actuator lags that student models usually leave out: the servo, with time constant $\tau_s$ and a rate limit, and the fan's spool-up, with time constant $\tau_T$:

$$\dot{\delta} = \frac{\delta_{\text{cmd}} - \delta}{\tau_s}, \quad |\dot{\delta}| \le \dot{\delta}_{\max} \qquad\qquad \dot{T} = \frac{T_{\text{cmd}} - T}{\tau_T}$$

With state $x = [\theta,\ \dot\theta,\ \delta]^T$, input $u = \delta_{\text{cmd}}$ and output $\theta$ (from the IMU):

$$\dot{x} = A x + B u, \qquad A = \begin{bmatrix} 0 & 1 & 0 \\ \dfrac{m g d}{J} & -\dfrac{c}{J} & \dfrac{T L}{J} \\ 0 & 0 & -\dfrac{1}{\tau_s} \end{bmatrix}, \quad B = \begin{bmatrix} 0 \\ 0 \\ \dfrac{1}{\tau_s} \end{bmatrix}$$

Model pitch and roll separately first (they decouple at small angles), then add the fan's reaction torque as a yaw disturbance.

| Symbol | Meaning | Use now | Replace with |
|---|---|---|---|
| $m$, $d$, $L$, $J$ | Mass; pivot-to-CG; pivot-to-thrust-line; inertia about the pivot | Group 1's first delivery, from CAD (week 2) | Measured on the assembled body (week 8) |
| $T$ | Thrust at the test throttle | EDF listing: about 22 N maximum | Thrust stand (week 6) |
| $\tau_T$ | Fan spool-up time constant | 0.2–0.4 s | Thrust stand (week 6) |
| $\tau_s$, $\dot\delta_{\max}$ | Servo lag and rate limit | DS3240 datasheet: about 0.15 s per 60°, so $\dot\delta_{\max} \approx 400^\circ/\text{s}$ at the servo, less at the gimbal | Desk-rig step tests (§6) |
| $c$ | Damping at the pivot | A small guess; check how much it matters | Fitted to logged responses |

**Deliverable:** a one-page model note (equations, and this table with sources) and an implementation in MATLAB/Simulink or Python.

### 1.1 From the stand to free flight (added 2026-09-24)

The same rocket will fly, and the stand's pivot will be adjustable (Part 1 §6, item 5), so the tilt model comes in three versions. The pivot now moves, so measure the lever arm from the CG instead: $L_{\text{CG}}$ is the CG-to-gimbal distance. With the pivot a distance $d$ below the CG, §1's $L$ becomes $L_{\text{CG}} - d$, and §1's $J$ becomes $J_{\text{CG}} + m d^2$ (the parallel-axis theorem).

| Configuration | Tilt equation (one axis, linearised) | Use |
|---|---|---|
| Stand, CG a distance $d$ above the pivot | $(J_{\text{CG}} + m d^2)\,\ddot\theta = T\,(L_{\text{CG}} - d)\,\delta + m g d\,\theta - c\,\dot\theta$ | The inverted-pendulum demo; a harder test |
| Stand, pivot at the CG ($d = 0$) | $J_{\text{CG}}\,\ddot\theta = T L_{\text{CG}}\,\delta - c\,\dot\theta$ | Tuning that carries over to flight |
| Free flight | $J_{\text{CG}}\,\ddot\theta = T L_{\text{CG}}\,\delta$ | The outdoor tests |

With the pivot at the CG, gravity has no lever arm, exactly as in flight; only the pivot friction $c$ differs. Gains tuned on the inverted configuration were tuned for a harder plant, so re-check them with the pivot at the CG before flying.

Flight adds two things the stand locks out:

- **Sideways motion.** A tilted thrust pushes the rocket sideways. At hover ($T \approx mg$), $\ddot x \approx g\,\varphi$, where $\varphi$ is the thrust's tilt from vertical (body tilt plus gimbal angle). Holding position needs an outer loop around the attitude loop: the pilot for the tethered hover, and ArduPilot's GPS position modes for the free-hover stretch goal.
- **Yaw.** $J_z\,\ddot\psi = \tau_{\text{fan}} + \tau_{\text{yaw}}$: the fan's net reaction torque against the yaw actuator (Part 1 §6, item 4). A simple rate loop is enough, and it isn't part of the PID-versus-LQR comparison.

## 2. Controllers in simulation (weeks 2–3)

Build the ladder you will later compare on hardware:

1. **PID on attitude:** the baseline, and what stock ArduPilot runs. Tune it by hand and note what limits it (usually the servo rate limit).
2. **LQR:** a state-feedback gain $u = -Kx$ from a cost on angle error and servo effort. It needs $\dot\theta$ (the gyro gives it) and $\delta$ (servo feedback or the model).
3. *Optional:* **LQR with integral action**, for a steady bias such as thrust misalignment; or a **gain-scheduled** LQR across throttle, since $T$ changes the plant.

Run all three through the tests you will repeat on hardware: a step in the reference, a push (impulse torque), a throttle change. Record settling time, overshoot and peak servo rate. That table, repeated on the stand in weeks 9–10, is the comparison the paper promises. If time allows, run it in both stand positions; the runs with the pivot at the CG are the ones that speak to flight (§1.1).

## 3. Where the controller runs (decide this week)

| Path | Strength | Weakness | Use it for |
|---|---|---|---|
| **Stock ArduPilot** (SingleCopter frame, PID gains as parameters) | Closes the loop in days; logging, failsafes and arming built in | PID only; SingleCopter expects four flaps, not a two-servo gimbal, so the output mapping needs care: two outputs for the gimbal, and yaw gains zeroed on the stand. In flight, yaw must drive the yaw actuator (Part 1 §6, item 4): exhaust tabs need a custom mapping; four vanes use the stock one | First closed loop on hardware; the safe demo; the outdoor test |
| **ArduPilot custom controller** (`CC_TYPE`, switchable in flight) | Your controller inside the firmware, stock PID as the fallback, everything logged | Needs ArduPilot's build tools and C++ (§4, route B) | The LQR comparison |
| **Off-board** (a laptop or the Arduino computes $u$ and sends servo commands) | Quickest to write and change | 10–50 ms of latency and jitter against a servo lag of about 50 ms: risky for an inverted pendulum | Identification runs and open-loop sweeps, not the closed loop |
| **Arduino as flight controller** (BNO085 → Mega → servos) | Total control, simple | You write the estimator, logging, safety and arming yourselves | Only if the ArduPilot build proves too steep by week 4 |

**Recommendation:** stock ArduPilot first, the custom controller second as the research path, and the Arduino for bench identification. Outdoors, fly on ArduPilot only: its failsafes, arming checks and logs are what a flight needs. The off-board and Arduino paths stay on the bench.

## 4. Getting started with SITL

SITL runs the real ArduPilot firmware on your laptop against a simulated vehicle. Mission Planner, ArduPilot's ground-control program, connects to it as it would to a Pixhawk on USB: same parameters, arming checks, outputs and logs. It won't teach you the rig's physics: SITL's `singlecopter` is a free-flying vehicle with one fan and four flaps, not a pivoting body with a two-servo gimbal. Learn the software on it; don't tune the rig's gains on it. Now that the rocket will fly, SITL is also the place to rehearse the outdoor test: flight modes, the radio kill switch, the failsafe (`SIM_RC_FAIL` simulates losing the transmitter), and, for the stretch goal, GPS position modes. Its vehicle still isn't your rocket, so the rule about gains stands.

### Route A: Mission Planner's simulator (Windows; start here, nothing to build)

1. Install [Mission Planner](https://ardupilot.org/planner/docs/mission-planner-installation.html).
2. **Simulation** tab: type `singlecopter` in the **Model** box (it accepts any SITL model name) and tick **Wipe** to start from default parameters.
3. Click the copter (multirotor) icon and choose **Stable**. Mission Planner downloads the simulator, starts it and connects.
4. **Config → Full Parameter List:** check that `FRAME_CLASS` is `8` (SingleCopter); if not, set it and restart.
5. First exercises:
   - **Outputs:** SERVO1–4 drive the four flaps (Motor 1–4) and SERVO5 the fan (Motor 5). Which two would your gimbal servos use?
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

- **Pixhawk 6C (BOM row 8): SITL (§4).** Nothing emulates it in a browser for this vehicle yet; ArduPilot's browser build of SITL, merged in September 2026, covers planes only.
- **Logs: [UAV Log Viewer](https://plot.ardupilot.org) and [ArduPilot WebTools](https://firmware.ardupilot.org/Tools/WebTools/)** (PID Review, Filter Review). They run in the browser, and the log stays on your computer. Practise on SITL logs.
- **Arduino Mega (row 36), servos (row 17), IMU (row 28): [Wokwi](https://wokwi.com).** It simulates an Arduino Mega, a servo, an MPU6050 IMU and a logic analyser. Practise the bench-identification code: timed servo steps, PWM pulse widths on the logic analyser, fixed-rate IMU reads, CSV logging over serial. Limits: the servo is ideal (no lag, backlash or torque limit), and the MPU6050 is a different chip from the BNO085, without its on-chip sensor fusion.
- **Model and controllers (§1–§2): [MATLAB Online](https://matlab.mathworks.com) with Simulink, through HCT's licence** (sign in from the [HCT access page](https://www.mathworks.com/academia/tah-portal/higher-college-of-technology-40589700.html)), **or [Google Colab](https://colab.research.google.com)**: run `!pip install control` in a cell, and `control.lqr` works with no further setup.
- **ESC and EDF (rows 1–2):** nothing useful to simulate; the thrust curve comes from group 1's thrust stand.

## 6. The desk rig (when the servos and the Pixhawk arrive)

Bolt the two DS3240 servos and the Pixhawk to a plank, hinge it with a weight above the hinge so it wants to fall, and link a servo to it through a lever so it can push it back. No fan. It gives you:

- **Servo characterisation:** log step commands; fit $\tau_s$ and the rate limit; measure deadband and backlash through the linkage. These replace the datasheet values in §1.
- **Sign and axis check:** tilt the rig by hand; the servo must push the right way. A reversed sign is one of the most common causes of a first-run crash.
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

- **Linkage play:** backlash makes a deadband the LQR will hunt in. Measure it on the desk rig.
- **Battery voltage:** the same throttle gives less thrust at 21 V than at 25 V, so the plant drifts during a session. Log the voltage.
- **Fan torques:** the reaction torque disturbs yaw, and a pitch rate makes a roll torque through the spinning rotor. Small, but not zero.
- **IMU vibration:** what limited the nearest comparable student project (Maribor). Check the vibration metrics before trusting attitude.
- **Latency:** about 5–10 ms from IMU to servo command inside ArduPilot, plus the servo's own lag. Fine at 400 Hz; fatal for an off-board loop over a slow link.
- **The tether:** slack, it's invisible; taut, it's a spring in the plant. Note its state in every test record.
- **Wind (outdoors):** gusts push on the body, and the centre of pressure starts to matter.
- **Heat (outdoors):** sun and air temperature heat the LiPo and the ESC. Test early in the day and log temperatures.
- **Ground effect:** in the last few tens of centimetres before touchdown, the fan's thrust changes.
- **Compass:** heading matters once yaw is controlled, and the fan's high-current leads disturb the magnetometer. Twist them and route them away from the Pixhawk.
- **SITL's vehicle:** free-flying with four flaps, not your rocket with its gimbal and yaw actuator (§4).
