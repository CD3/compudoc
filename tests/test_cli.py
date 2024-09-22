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

        rendered_text = pathlib.Path("main-rendered.tex").read_text()
        assert rendered_text == "TEXT\n"

        result = runner.invoke(app, [f"{input_file}", "main-processed.tex"])
        assert result.exit_code == 0
        assert pathlib.Path("main-processed.tex").exists()




def test_local_modules(tmp_path):
    """
    We can import and use custom python modules
    in our documents.
    """
    with workingdir(tmp_path):
        pathlib.Path("custom.py").write_text(
            """
import math

myPi = math.pi
        """
        )
        input_file = pathlib.Path("main-template.txt")
        output_file = pathlib.Path("main.txt")
        input_file.write_text(
            """
// {{{
// import custom
// }}}
pi = {{custom.myPi | fmt('.2f')}}
"""
        )

        result = runner.invoke(
            app, [f"{input_file}", f"{output_file}", "--comment-line-str", r"//"]
        )
        assert result.exit_code == 0
        assert output_file.exists()
        rendered_text = output_file.read_text()

        assert (
            rendered_text
            == """
// {{{
// import custom
// }}}
pi = 3.14
"""
        )
