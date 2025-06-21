import subprocess
import os
import pytest

def run_alembic_cmd(args):
    result = subprocess.run([
        "alembic", *args
    ], capture_output=True, text=True)
    return result

@pytest.mark.order(1)
def test_alembic_upgrade_success():
    result = run_alembic_cmd(["upgrade", "head"])
    assert result.returncode == 0, f"Alembic upgrade failed: {result.stderr}"
    assert "Running upgrade" in result.stdout or result.stderr

@pytest.mark.order(2)
def test_alembic_downgrade_success():
    # Получаем первую ревизию (head^)
    result = run_alembic_cmd(["downgrade", "-1"])
    assert result.returncode == 0, f"Alembic downgrade failed: {result.stderr}"
    assert "Running downgrade" in result.stdout or result.stderr
    # Возвращаем обратно
    result2 = run_alembic_cmd(["upgrade", "head"])
    assert result2.returncode == 0

@pytest.mark.order(3)
def test_alembic_upgrade_failure():
    # Пробуем апгрейд на несуществующую ревизию
    result = run_alembic_cmd(["upgrade", "nonexistent"])
    assert result.returncode != 0
    assert "not a valid revision" in result.stderr.lower() or "failed" in result.stderr.lower() or "error" in result.stderr.lower() 