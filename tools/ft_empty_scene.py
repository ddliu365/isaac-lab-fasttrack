"""Boot Isaac Sim headless, build a minimal scene, step 100 frames, exit. Used by ft-smoke."""
import argparse, time
from isaaclab.app import AppLauncher
parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
t0 = time.time()
app = AppLauncher(args).app
import isaaclab.sim as sim_utils
sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=0.01, device=args.device))
sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
sim.reset()
t1 = time.time()
for _ in range(100):
    sim.step()
t2 = time.time()
print(f"FT_EMPTY_SCENE ok boot={t1-t0:.1f}s steps100={t2-t1:.2f}s", flush=True)
# SimulationApp.close() can hang on lingering Kit threads in headless mode; hard-exit after the marker.
import os, sys; sys.stdout.flush(); os._exit(0)
