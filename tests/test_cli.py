import pathlib

from clirunner import CliRunner

from compudoc.__main__ import app

from .utils import *

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    assert "compudoc" in result.stdout


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


def test_gnuplot_scripts(tmp_path):
    with workingdir(tmp_path):
        input_file = pathlib.Path("graph.gnuplot")
        input_file.write_text(
            """
# {{{
# wavelength = 3
# wavenumber = 2 * 3.1415 / wavelength
# }}}
set term dumb

plot sin({{wavenumber|round(1)}}*x)
"""
        )

        result = runner.invoke(app, [f"{input_file}"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("graph-rendered.gnuplot").exists()

        rendered_text = pathlib.Path("graph-rendered.gnuplot").read_text()
        assert (
            rendered_text
            == """
# {{{
# wavelength = 3
# wavenumber = 2 * 3.1415 / wavelength
# }}}
set term dumb

plot sin(2.1*x)
"""
        )


def test_interpreter(tmp_path):
    with workingdir(tmp_path):
        input_file = pathlib.Path("main.tex")
        input_file.write_text(
            """
% {{{
% import sys
% interp = sys.executable
% }}}
{{interp}}
"""
        )

        result = runner.invoke(app, [f"{input_file}", "--python", "/usr/bin/python"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("main-rendered.tex").exists()

        rendered_text = pathlib.Path("main-rendered.tex").read_text()
        assert (
            rendered_text
            == """
% {{{
% import sys
% interp = sys.executable
% }}}
/usr/bin/python
"""
        )

        import os

        os.symlink("/usr/bin/python", "./python")
        result = runner.invoke(app, [f"{input_file}", "--python", "./python"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("main-rendered.tex").exists()

        rendered_text = pathlib.Path("main-rendered.tex").read_text()
        assert (
            rendered_text
            == """
% {{{
% import sys
% interp = sys.executable
% }}}
"""
            + os.getcwd()
            + """/python
"""
        )


def test_output_file_naming(tmp_path):
    with workingdir(tmp_path):
        input_file = pathlib.Path("main1.tex")
        input_file.write_text("TEXT\n")

        result = runner.invoke(app, [f"{input_file}"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("main1-rendered.tex").exists()

        input_file = pathlib.Path("main2.tex.compudoc")
        input_file.write_text("TEXT\n")

        result = runner.invoke(app, [f"{input_file}"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("main2.tex").exists()

        input_file = pathlib.Path("main3.tex.cd")
        input_file.write_text("TEXT\n")

        result = runner.invoke(app, [f"{input_file}"])
        assert result.exit_code == 0

        assert input_file.exists()
        assert pathlib.Path("main3.tex").exists()
