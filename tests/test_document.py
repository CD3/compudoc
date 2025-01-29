import asyncio
from pathlib import Path

import pytest

from compudoc.document import *
from compudoc.execution_engines import *
from compudoc.parsing import *

from .utils import *


@pytest.fixture
def simple_document_text():
    text = """
This is some text
% {{{
% import pint
% ureg = pint.UnitRegistry
% Q_ = ureg.Quantity
%
% }}}

This is more text.

% {{{
% x = Q_(1,'m')
%
% }}}

The length is $L = {{'{:Lx}'.format(x)}}$.

"""
    return text


def test_initializing_engine():
    async def run():
        assert True
        assert True
        temp = "x = {{x}}"
        process = Python()
        await process.start()
        await process.eval("import pint")
        await process.eval("import jinja2")
        await process.eval("x = 2")
        await process.eval("y = [2,3]")
        await process.eval(f"template = jinja2.Template('{temp}')")
        await process.eval(f"x")

        result = await process.eval("x")
        assert result == "2"
        result = await process.eval("y")
        assert result == "[2, 3]"
        result = await process.eval("template.render(**globals())")
        assert result == "'x = 2'"
        await process.stop()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


def test_document_rendering(simple_document_text):
    doc = Document()
    rendered_text = doc.parse_and_render(simple_document_text, quiet=True)
    assert r"The length is $L = \SI[]{1}{\meter}$." in rendered_text

    doc.clear()
    rendered_text = doc.parse_and_render(
        """\
Line 1
% {{{
% x = 1.2
% }}}
Line 2: x = {{x}}
""",
        quiet=True,
    )

    assert (
        rendered_text
        == """\
Line 1
% {{{
% x = 1.2
% }}}
Line 2: x = 1.2
"""
    )

    doc.clear()
    rendered_text = doc.parse_and_render(
        """\
Line 1

% {{{
% x = 1.2
% }}}
Line 2: x = {{x}}
""",
        quiet=True,
    )

    assert (
        rendered_text
        == """\
Line 1

% {{{
% x = 1.2
% }}}
Line 2: x = 1.2
"""
    )

    doc = Document("#{{CODE}}")
    rendered_text = doc.parse_and_render(
        """\
Line 1

# {{{
# x = 1.2
# }}}
Line 2: x = {{x}}
""",
        quiet=True,
    )

    assert (
        rendered_text
        == """\
Line 1

# {{{
# x = 1.2
# }}}
Line 2: x = 1.2
"""
    )
    doc.clear()
    rendered_text = doc.parse_and_render(
        """\
Line 1

# {{{
# x = 1.2
# }}}
Line 2: x = {{x}}
""",
        strip_comment_blocks=True,
        quiet=True,
    )

    assert (
        rendered_text
        == """\
Line 1

Line 2: x = 1.2
"""
    )


def test_include_file_filter(tmp_path):
    with workingdir(tmp_path):
        Path("include.txt").write_text(r"""INCLUDED FROM FILE""")

        doc = Document()

        rendered_text = doc.parse_and_render(
            """\
    % {{{
    % import pathlib
    % def include_filter(filename):
    %   return pathlib.Path(filename).read_text()
    %
    % jinja2_env.filters['include'] = include_filter
    % }}}
    This is {{"include.txt" | include}}!
    """,
            quiet=True,
        )

        assert (
            rendered_text
            == """\
    % {{{
    % import pathlib
    % def include_filter(filename):
    %   return pathlib.Path(filename).read_text()
    %
    % jinja2_env.filters['include'] = include_filter
    % }}}
    This is INCLUDED FROM FILE!
    """
        )

        doc.clear()
        rendered_text = doc.parse_and_render(
            """\
    This is {{"include.txt" | insert}}!
    """,
            quiet=True,
        )

        assert (
            rendered_text
            == """\
    This is INCLUDED FROM FILE!
    """
        )
