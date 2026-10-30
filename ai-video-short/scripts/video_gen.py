"""Parameterized wrapper around the built-in video generation client.

Adds Duration / AspectRatio control that the built-in CLI hardcodes.
Usage:
    VF_DURATION=10 VF_RATIO=9:16 python video_gen.py video "<prompt>" --token-stdin

The built-in buddy-cloud.py lives in the platform's skill directory.
Override its location via the BUDDY_CLOUD env var if your install differs.
"""
import importlib.util
import json
import os
import sys

BC = os.environ.get("BUDDY_CLOUD") or (
    r"C:\Users\asus\.workbuddy\plugins\marketplaces\workbuddy-builtin"
    r"\skills\buddy-multimodal-generation\scripts\buddy-cloud.py"
)

spec = importlib.util.spec_from_file_location("buddy_cloud", BC)
bc = importlib.util.module_from_spec(spec)
sys.modules["buddy_cloud"] = bc
spec.loader.exec_module(bc)

DURATION = int(os.environ.get("VF_DURATION", "10"))
RATIO = os.environ.get("VF_RATIO", "9:16")


def _patched_video_body(prompt: str) -> dict:
    return {
        "Vendor": bc._d("S2xpbmc="),
        "Model": "v2.6",
        "Prompt": prompt,
        "ModelParam": json.dumps({"Duration": DURATION, "AspectRatio": RATIO}),
        "LogoAdd": 1,
    }


bc._build_video_body = _patched_video_body
bc.main()
