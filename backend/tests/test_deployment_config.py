import tomllib
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DeploymentConfigTest(unittest.TestCase):
    def test_render_uses_temporary_sqlite_and_health_check(self) -> None:
        blueprint = yaml.safe_load((PROJECT_ROOT / "render.yaml").read_text(encoding="utf-8"))
        service = blueprint["services"][0]
        environment = {item["key"]: item for item in service["envVars"]}

        self.assertEqual(service["runtime"], "python")
        self.assertEqual(service["rootDir"], "backend")
        self.assertEqual(service["healthCheckPath"], "/api/health")
        self.assertIn("--port $PORT", service["startCommand"])
        self.assertEqual(
            environment["DATABASE_URL"]["value"],
            "sqlite:////tmp/localhub.db",
        )
        self.assertFalse(environment["CORS_ORIGINS"]["sync"])
        self.assertNotIn("disk", service)

    def test_netlify_builds_frontend_and_rewrites_spa_routes(self) -> None:
        config = tomllib.loads((PROJECT_ROOT / "netlify.toml").read_text(encoding="utf-8"))

        self.assertEqual(config["build"]["base"], "frontend")
        self.assertEqual(config["build"]["command"], "pnpm run build")
        self.assertEqual(config["build"]["publish"], "dist")
        self.assertEqual(config["redirects"][0]["from"], "/*")
        self.assertEqual(config["redirects"][0]["to"], "/index.html")
        self.assertEqual(config["redirects"][0]["status"], 200)
