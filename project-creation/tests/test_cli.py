import pytest

from project_creation.cli import main


def test_cli_help_is_available(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    assert "Post-award Cyber project provisioning" in capsys.readouterr().out
