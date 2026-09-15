from __future__ import annotations

from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY_IDS = {
    "embedded-system-team-lead",
    "embedded-architecture-expert",
    "linux-bsp-expert",
    "mcu-rtos-expert",
    "driver-component-expert",
    "debug-reliability-expert",
    "verification-expert",
    "embedded-review-governor",
}


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise AssertionError(f"missing YAML frontmatter: {path}")
    return yaml.safe_load(parts[1])


class TargetSkillFilesTest(unittest.TestCase):
    def test_registry_and_physical_skill_contracts_are_target_only(self):
        registry = yaml.safe_load((EDGE / "skills.yaml").read_text(encoding="utf-8"))
        self.assertEqual(registry["status"], "target-v1")
        self.assertEqual(registry["execution_surface"], "target")
        self.assertTrue(registry["rules"]["physical_skill_location_is_canonical"])
        self.assertTrue(registry["rules"]["skill_frontmatter_owner_must_match_registry"])
        self.assertEqual(len(registry["skills"]), 23)

        seen = set()
        for item in registry["skills"]:
            skill_id = item["id"]
            self.assertNotIn(skill_id, seen)
            seen.add(skill_id)
            self.assertTrue(item["path"].startswith("skills/"), item)
            path = EDGE / item["path"]
            self.assertTrue(path.is_file(), path)
            meta = frontmatter(path)
            self.assertEqual(meta["id"], skill_id)
            self.assertEqual(meta["version"], "1.0.0")
            self.assertEqual(meta["owner_kind"], item["owner_kind"])
            self.assertEqual(meta["owner"], item["owner_id"])
            self.assertEqual(meta["max_action_level"], "A2_GENERATE")
            text = path.read_text(encoding="utf-8")
            self.assertFalse(LEGACY_IDS & set(text.replace("`", "").replace(",", " ").split()), path)

        tree_files = list((EDGE / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(tree_files), 23)


if __name__ == "__main__":
    unittest.main()
