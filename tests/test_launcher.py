from pathlib import Path

from word_turn_launcher import run_self_check


def test_self_check_score_range_and_items():
    checks, score = run_self_check()
    assert checks
    assert 0 <= score <= 100


def test_output_dir_check_is_repairable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "app.py").write_text("", encoding="utf-8")
    (tmp_path / "word_replacer.py").write_text("", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("", encoding="utf-8")

    checks, _ = run_self_check()
    output_check = [c for c in checks if c.item == "输出目录"][0]
    assert output_check.ok is False
    assert output_check.repair is not None

    repaired, _ = output_check.repair()
    assert repaired is True
    assert Path("output").exists()
