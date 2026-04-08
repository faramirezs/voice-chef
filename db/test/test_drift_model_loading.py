from pathlib import Path

from db.scripts import drift_check


def test_drift_check_prefers_models_subdirectory() -> None:
    loaded = [Path(p).as_posix() for p in drift_check._LOADED_MODEL_FILES]

    assert loaded
    assert all("/fastapi/app/models/" in p for p in loaded)
    assert any(p.endswith("/fastapi/app/models/users.py") for p in loaded)
    assert any(p.endswith("/fastapi/app/models/tmp_recipe.py") for p in loaded)
