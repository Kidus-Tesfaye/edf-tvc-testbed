"""Run the R4 Simulink plant with ArduPilot SITL."""
from pathlib import Path
from datetime import datetime
import argparse
import json
import os
import shutil
import socket
import sys

ROOT = Path(__file__).resolve().parent


def main():
    cases = [case['name'] for case in json.loads((ROOT/'config/cases.json').read_text())]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=cases + ['all'], default='wind_x1')
    parser.add_argument('--matlab', help='Path to MATLAB bin/matlab.exe')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if os.name != 'nt':
        raise SystemExit('The supplied firmware and connector binaries require Windows x64.')

    candidates = [args.matlab, os.environ.get('MATLAB_EXE'), shutil.which('matlab')]
    candidates += [str(path/'bin/matlab.exe') for path in sorted(Path('C:/Program Files/MATLAB').glob('R2025b*'), reverse=True)]
    matlab = next((Path(path).resolve() for path in candidates if path and Path(path).is_file()), None)
    if matlab is None:
        raise SystemExit('MATLAB not found. Use --matlab "C:\\Program Files\\MATLAB\\R2025b\\bin\\matlab.exe".')
    os.environ['MATLAB_EXE'] = str(matlab)

    import numpy
    from pymavlink import mavutil
    for name in ['model/R4_ArduPilot_JSON.slx', 'runtime/connector/pnet.mexw64',
                 'runtime/ardupilot/arducopter.exe', 'runtime/ardupilot/cygwin1.dll',
                 'config/copter.parm', 'config/gps_good.parm']:
        if not (ROOT/name).is_file():
            raise SystemExit('Missing file: '+name+'. Extract the complete package.')
    for kind, port in [(socket.SOCK_STREAM, 5760), (socket.SOCK_DGRAM, 9002)]:
        with socket.socket(socket.AF_INET, kind) as connection:
            try:
                connection.bind(('127.0.0.1', port))
            except OSError:
                raise SystemExit(f'Port {port} is in use. Close the other simulation before starting this one.')
    print('MATLAB:', matlab, flush=True)
    print('Python:', sys.version.split()[0], '| NumPy:', numpy.__version__, flush=True)
    if args.check_only:
        print('Dependencies, files and local ports checked. MATLAB licensing is checked on launch.')
        return

    sys.path.insert(0, str(ROOT/'scripts'))
    from run_sitl import run_case
    from analyse import analyse
    selected = cases if args.case == 'all' else [args.case]
    for name in selected:
        output = name + '_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        print('\nRunning', name, flush=True)
        folder = run_case(name, instance=0, output_name=output)
        metrics = analyse(name, folder)
        print('Maximum distance from launch: %.3f m' % metrics['max_radius_m'], flush=True)
        print('Touchdown offset: %.3f m' % metrics['radius_at_touchdown_m'], flush=True)
        print('Within 1 m:', metrics['radius_1m_pass'], '| Landing checks:', metrics['landing_model_pass'], flush=True)
        print('Saved:', folder, flush=True)
    print('\nRun complete.', flush=True)


if __name__ == '__main__':
    main()
