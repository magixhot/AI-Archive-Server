from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent

SRC_ROOT = PACKAGE_ROOT.parent

PROJECT_ROOT = SRC_ROOT.parent


ARCHIVE_ROOT = PROJECT_ROOT / "AI-Archive"

MODELS_ROOT = ARCHIVE_ROOT / "models"

REGISTRY_ROOT = ARCHIVE_ROOT / "registry"

REGISTRY_FILE = REGISTRY_ROOT / "models.json"