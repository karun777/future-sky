"""W7-F8 code-only deployment and rollback; no production service calls."""
import importlib.util
from pathlib import Path
import test_wardrobe_deployment as baseline

class HudDeploymentTests(baseline.WardrobeDeploymentTests):
    def setUp(self):
        super().setUp()
        path = Path(__file__).resolve().parents[1] / "tools/deploy/w7f8/activate.py"
        spec = importlib.util.spec_from_file_location("hud_deploy", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for key in ("SOURCE", "LIVE", "command", "start_and_wait", "status"):
            setattr(module, key, getattr(self.m, key))
        self.m = module
