import pathlib

from typer.testing import CliRunner

from compudoc.__main__ import app

from .utils import *

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    assert "main [OPTIONS] INPUT_FILE [OUTPUT_FILE_TEMPLATE]" in result.stdout


def test_simple_documents(tmp_path):
    with workingdir(tmp_path):
        input_file = pathlib.Path("main.tex")
        input_file.write_text("TEXT\n")

        result = runner.invoke(app, [f"{input_file}"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("main-rendered.tex").exists()
        assert not pathlib.Path("main-processed.tex").exists()

        result = runner.invoke(app, [f"{input_file}", "main-processed.tex"])
        assert result.exit_code == 0
        assert pathlib.Path("main-processed.tex").exists()
