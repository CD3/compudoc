import pyparsing
import pytest

from compudoc.parsing import *


@pytest.fixture
def simple_document_text():
    text = """
This is some text
% {{{ {}
% import pint
% ureg = pint.UnitRegistry()
%
% }}}

This is more text.

% {{{
% x = Q_(1,'m')
% y = Q_(2,'ft')
%
% }}}

"""
    return text


def test_code_extraction(simple_document_text):
    p = CodeBlockParseHolder("%{{CODE}}")

    assert (
        p.extract_code(
            """\
    % {{{
    % x = 1
    % y = 2
    % }}}
    """,
        )
        == "x = 1\ny = 2\n"
    )

    assert (
        p.extract_code(
            """\
    % {{{
    % x = 1
    % y = 2
    % }}}
    """,
        )
        == "x = 1\ny = 2\n"
    )

    assert (
        p.extract_code(
            """\
    % {{{
    % x = 1
    % y = 2
    % }}}
    """,
        )
        == "x = 1\ny = 2\n"
    )


def test_comment_line_parser():
    import re

    comment_pattern = "# {{CODE}}"
    comment_regex = r"\s*" + comment_pattern.replace("{{CODE}}", "(?P<CODE>.*)")
    assert re.match(comment_regex, "# import pint")
    assert re.match(comment_regex, "# import pint").group("CODE") == "import pint"

    comment_line_parser = (
        pyparsing.Suppress(pyparsing.LineStart())
        + pyparsing.Regex(comment_regex)
        + pyparsing.Suppress(pyparsing.LineEnd())
    )

    results = comment_line_parser.parse_string("  # import pint")
    assert results
    assert results["CODE"] == "import pint"

    comment_block_parser = pyparsing.OneOrMore(comment_line_parser)

    results = comment_line_parser.search_string(
        "# one \n# import pint\n# ureg = pint.UnitRegistry()  \n"
    )
    assert results
    assert results[0]["CODE"] == "one "
    assert results[1]["CODE"] == "import pint"
    assert results[2]["CODE"] == "ureg = pint.UnitRegistry()  "

    comment_line_parser = CommentLineParseHolder("# {{CODE}}")

    results = comment_line_parser.parser.parse_string("# import pint")
    assert results
    assert results["CODE"] == "import pint"

    comment_line_parser = CommentLineParseHolder("<!---{{CODE}}--->")
    results = comment_line_parser.parser.parse_string("<!---import math--->")
    assert results
    assert results["CODE"] == "import math"


def test_comment_block_parser():
    comment_code_block = CodeBlockParseHolder("# {{CODE}}")

    assert comment_code_block.block_start_parser.parse_string("# {{{")
    assert comment_code_block.block_start_parser.parse_string("    # {{{")
    assert comment_code_block.block_start_parser.parse_string("    # {{{      ")
    assert (
        comment_code_block.block_start_parser.parse_string("# {{{")[0]["CODE"] == "{{{"
    )
    assert (
        comment_code_block.block_start_parser.parse_string("    # {{{")[0]["CODE"]
        == "{{{"
    )
    assert comment_code_block.block_end_parser.parse_string("# }}}")
    assert comment_code_block.block_end_parser.parse_string("    # }}}")
    assert comment_code_block.block_end_parser.parse_string("    # }}}   ")
    assert comment_code_block.block_end_parser.parse_string("# }}}")[0]["CODE"] == "}}}"
    assert (
        comment_code_block.block_end_parser.parse_string("    # }}}")[0]["CODE"]
        == "}}}"
    )

    results = comment_code_block.parser.parse_string(
        """\
 # {{{
 # import pint
 # ureg = pint.UnitRegistry()
 # }}}
"""
    )
    assert results

    assert "".join(results["BLOCK_START"][0]) == "# {{{"
    assert results["BLOCK_START"][0]["CODE"] == "{{{"

    assert "".join(results["BLOCK_END"][0]) == "# }}}"
    assert results["BLOCK_END"][0]["CODE"] == "}}}"

    print(results.dump())
    return
    assert "".join(results["CODE_LINES"]) == "# import pint"
    assert results["CODE_LINES"][0]["CODE"] == "import pint"

    return

    results = comment_code_block.parser.parse_string(
        """\
 # {{{
 # import pint
 # ureg = pint.UnitRegistry()
 # }}}
"""
    )
    assert results

    assert "".join(results["BLOCK_START"][0]) == "# {{{"
    assert results["BLOCK_START"][0]["CODE"] == "{{{"

    assert "".join(results["BLOCK_END"][0]) == "# }}}"
    assert results["BLOCK_END"][0]["CODE"] == "}}}"

    print(results.dump())
    assert results["CODE_LINES"] == ["import pint"]
    assert "".join(results["CODE_LINES"]) == "# import pint"


def test_document_parsing():
    text = """\
line 1
line 2
% {{{
% import pint
% ureg = pint.UnitRegistry()
% Q_ = ureg.Quantity
% }}}
line 3
line 4
% {{{
% x = 10
% def f(a):
%   return a*2
% }}}
line 5\
"""
    comment_code_block = CodeBlockParseHolder("%{{CODE}}")
    blocks = []
    i = 0
    for match in comment_code_block.get_comment_code_blocks(text):
        ibeg = match[1]
        iend = match[2]
        # need to add the text chunk before
        # this code chunk
        chunk = text[i:ibeg]
        blocks.append(chunk)

        # and this code chunk
        chunk = text[ibeg : iend + 1]
        blocks.append(chunk)
        i = iend + 1
    chunk = text[i:]
    blocks.append(chunk)

    assert len(blocks) == 5
    assert not comment_code_block.is_comment_code_block(blocks[0])
    assert comment_code_block.is_comment_code_block(blocks[1])
    assert not comment_code_block.is_comment_code_block(blocks[2])
    assert comment_code_block.is_comment_code_block(blocks[3])
    assert not comment_code_block.is_comment_code_block(blocks[4])

    assert (
        comment_code_block.extract_code(blocks[1])
        == "import pint\nureg = pint.UnitRegistry()\nQ_ = ureg.Quantity\n"
    )
    assert (
        comment_code_block.extract_code(blocks[3])
        == "x = 10\ndef f(a):\n  return a*2\n"
    )


def test_extracting_code_from_block():
    comment_code_block = CodeBlockParseHolder("%{{CODE}}")
    text = "% {{{\n% import pint\n% ureg = pint.UnitRegistry()\n% Q_ = ureg.Quantity\n% }}}\n"
    assert comment_code_block.is_comment_code_block(text)
    text = comment_code_block.extract_code(text)
    assert text == "import pint\nureg = pint.UnitRegistry()\nQ_ = ureg.Quantity\n"


def test_making_comment_code_block():
    comment_code_block = CodeBlockParseHolder("%{{CODE}}")
    text = "import pint\nureg = pint.UnitRegistry()\nQ_ = ureg.Quantity\n"
    assert not comment_code_block.is_comment_code_block(text)

    # by default, code will be indented one space
    commented_text = comment_code_block.comment_code(text)
    assert (
        commented_text
        == "% {{{\n% import pint\n% ureg = pint.UnitRegistry()\n% Q_ = ureg.Quantity\n% }}}\n"
    )
    assert comment_code_block.is_comment_code_block(commented_text)

    # we can not indent the code
    commented_text = comment_code_block.comment_code(text, prefix="")
    assert (
        commented_text
        == "%{{{\n%import pint\n%ureg = pint.UnitRegistry()\n%Q_ = ureg.Quantity\n%}}}\n"
    )
    assert comment_code_block.is_comment_code_block(commented_text)
    # or indent it more
    commented_text = comment_code_block.comment_code(text, prefix="   ")
    assert (
        commented_text
        == "%   {{{\n%   import pint\n%   ureg = pint.UnitRegistry()\n%   Q_ = ureg.Quantity\n%   }}}\n"
    )
    assert comment_code_block.is_comment_code_block(commented_text)

    # or use a non-space prefix
    commented_text = comment_code_block.comment_code(text, prefix=">> ")
    assert (
        commented_text
        == "%>> {{{\n%>> import pint\n%>> ureg = pint.UnitRegistry()\n%>> Q_ = ureg.Quantity\n%>> }}}\n"
    )
    # but this makes it not a comment block anymore...
    assert not comment_code_block.is_comment_code_block(commented_text)


def test_making_block_start_and_end_comment_lines():
    template_pattern = "% {{CODE}}"
    parser = make_comment_line_parser(
        template_pattern.replace("{{CODE}}", r"\s*(?P<CODE>" + "{{{" + ")")
    )

    assert parser.parse_string("% {{{")
    assert parser.parse_string(" % {{{")
    assert parser.parse_string(" % {{{ ")
    with pytest.raises(Exception) as e:
        assert not parser.parse_string("%{{{")

    parser = CodeBlockParseHolder(template_pattern)

    assert parser.parser.parse_string("% {{{\n% }}}\n")
    assert parser.parser.parse_string(" % {{{\n % }}}\n")
    assert parser.parser.parse_string("% {{{\n% import pint\n% }}}\n")


def test_making_commented_line_parser():
    comment_line_parser = make_commented_code_line_parser("%{{CODE}}")

    results = comment_line_parser.parse_string("% import pint  ")
    assert results
    assert "".join(results["LINE"]) == "% import pint  "
    assert results["CODE"] == " import pint  "

    results = comment_line_parser.parse_string("  % import pint  ")
    assert results
    assert "".join(results["LINE"]) == "% import pint  "
    assert results["CODE"] == " import pint  "

    results = comment_line_parser.search_string("% x = 1  \n% y = 3")
    assert len(results) == 2

    comment_line_parser = make_commented_code_line_parser("<!--{{CODE}}-->")

    results = comment_line_parser.parse_string("<!-- import pint -->")

    assert results
    assert "".join(results["LINE"]) == "<!-- import pint -->"
    assert results["CODE"] == " import pint "

    start_block_parser = make_commented_marker_line_parser(
        "%{{CODE}}", marker_text="{{{"
    )

    results = start_block_parser.parse_string("  % {{{  ")
    assert results
    assert "".join(results["LINE"]) == "%{{{"
    assert results["MARKER"] == "{{{"

    start_block_parser = make_commented_marker_line_parser(
        "<!--{{CODE}}-->", marker_text="{{{"
    )

    results = start_block_parser.parse_string("  <!-- {{{ --> ")
    assert results
    assert "".join(results["LINE"]) == "<!--{{{-->"
    assert results["MARKER"] == "{{{"


def test_pyparsing_literals():
    # some tests I wrote while trying to figure out the parsers
    # work.
    p = pyparsing.Literal("a") + pyparsing.Literal("b")

    assert p.parse_string("ab")
    assert p.parse_string("a b")


def test_making_comment_block_parser():
    commented_code_block_parser = make_commented_code_block_parser("%{{CODE}}")

    results = commented_code_block_parser.parse_string(
        """% {{{
% import pint
% ureg = pint.UnitRegistry()
%
% def make_q(v,u):
%   return ureg.Quantity(v,u)
%
% x = make_q(2,'m')
% }}}
"""
    )

    assert results["CODE_LINES"][0] == "%"
    assert results["CODE_LINES"][1] == " import pint"
    assert results["CODE_LINES"][2] == "%"
    assert results["CODE_LINES"][3] == " ureg = pint.UnitRegistry()"
    assert results["CODE_LINES"][4] == "%"
    assert results["CODE_LINES"][5] == ""
    assert results["CODE_LINES"][6] == "%"
    assert results["CODE_LINES"][7] == " def make_q(v,u):"
    assert results["CODE_LINES"][8] == "%"
    assert results["CODE_LINES"][9] == "   return ureg.Quantity(v,u)"
    assert results["CODE_LINES"][10] == "%"
    assert results["CODE_LINES"][11] == ""
    assert results["CODE_LINES"][12] == "%"
    assert results["CODE_LINES"][13] == " x = make_q(2,'m')"
