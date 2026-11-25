# R4 flight simulation

Single EDF, four vanes, a climb to 5 m, an 8-second hover and landing without ropes.
The recorded runs are from 6 November 2026.

## Watch

Download this branch and open `START_HERE.html` in a browser for the interactive
3D playback. The presentation video is
`playback/R4_Full_Flight_1ms_Crosswind.mp4`. Both show the +X 1 m/s crosswind case.
The viewer uses the R4 CAD geometry and recorded position, attitude and vane angles.

## Run

Windows x64, MATLAB R2025b with Simulink, and Python 3.12 are required.
From this folder in PowerShell, run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

The default case is `wind_x1`. Use `run.py --case all` for all eight cases,
or `run.py --check-only` to check dependencies, files and local ports.
If MATLAB is elsewhere, add `--matlab "D:\MATLAB\R2025b\bin\matlab.exe"`.
Open `model/R4_ArduPilot_JSON.slx` to inspect the diagram.
Use `run.py` to start the complete simulation, including ArduPilot.
Keep TCP 5760 and UDP 9002 available and run one copy at a time.
New recordings go in `results/`. Startup and simulation can take several minutes.

## Model

ArduCopter 4.7.3 beta runs the SingleCopter controller and EKF3 on the computer.
Simulink calculates rigid-body motion, fan and servo response, vane forces,
wind drag and foot contact. Simulated IMU, rangefinder and GPS readings feed
the controller. The full flight uses Loiter followed by LAND.

The physics solver is fixed-step RK4 at 1/2400 s, with sensor/actuator exchange
at 1200 Hz and the native controller loop at 400 Hz. These runs used a mass
of 2.0128 kg and assumed available thrust of 27.616 N, giving T/W about 1.40.
The team target is measured installed T/W greater than 1.5.

GPS updates at 10 Hz with 0.20 m noise per axis, 0.30 m slow position wander
and 0.20 s delay. Nominal foot stiffness is 8000 N/m per foot and damping is
50 N s/m. These properties and the vane forces still need bench measurements.
The simulation used no physical Pixhawk. Ground effect, leg strength and
actual GPS performance have yet to be verified.

## Recorded results

| Case | Maximum distance (m) | Touchdown offset (m) | Landing checks |
| --- | ---: | ---: | --- |
| calm | 0.496 | 0.384 | Pass |
| wind_x1 | 0.387 | 0.267 | Pass |
| wind_nx1 | 0.450 | 0.366 | Pass |
| wind_y1 | 0.597 | 0.351 | Pass |
| wind_ny1 | 0.392 | 0.194 | Pass |
| wind_x05 | 0.515 | 0.277 | Pass |
| gps_phase2 | 0.570 | 0.462 | Bounce check |
| contact_stress | 0.370 | 0.297 | Pass |

All eight stayed within a 1 m radius of launch, settled and disarmed.
Seven passed every conservative landing check. `gps_phase2` rebounded
8.6 mm against the selected 5 mm limit before settling.
`contact_stress` doubles foot stiffness and halves damping.
The cases test selected conditions and do not establish a real-flight success rate.

The CSV and per-case measurements are in `recorded/`.
[Download the full recordings and runnable package](https://github.com/Kidus-Tesfaye/edf-tvc-testbed/releases/download/r4-simulation-2026-11-06/R4_simulation.zip).
The ZIP includes all eight MAT recordings, native DataFlash logs, GPS samples
and setup instructions. File paths in JSON metadata are relative to the package.
Firmware startup and sensor timing can cause reruns to differ from the recording.

## Third-party components

ArduPilot, Cygwin and pnet notices and source references are in
`runtime/licenses/` and `runtime/connector/`.
Three.js is included under its MIT license in `playback/vendor/THREE_LICENSE.txt`.
Python dependencies are listed in `requirements.txt`.
