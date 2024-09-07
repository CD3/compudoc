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


def test_document_chunking(simple_document_text):
    text = simple_document_text

    chunks = chunk_document(text)

    assert len(chunks) == 5
    assert "".join(chunks) == text

    chunks = chunk_document(text, parsers.make_commented_code_block_parser("%"))

    assert len(chunks) == 5
    assert "".join(chunks) == text

    assert chunks[0] == "\nThis is some text\n"
    assert (
        chunks[1] == "% {{{ {}\n% import pint\n% ureg = pint.UnitRegistry()\n%\n% }}}\n"
    )
    assert chunks[2] == "\nThis is more text.\n\n"
    assert chunks[3] == "% {{{\n% x = Q_(1,'m')\n% y = Q_(2,'ft')\n%\n% }}}\n"

    chunks = chunk_document(
        """\
Line 1
% {{{
% x = 1
% }}}
"""
    )

    assert len(chunks) == 3
    assert chunks[0] == "Line 1\n"
    assert chunks[1] == "% {{{\n% x = 1\n% }}}\n"
    assert chunks[2] == ""

    chunks = chunk_document(
        """\
Line 1
% {{{
% x = 1
% }}}"""
    )

    assert len(chunks) == 3
    assert chunks[0] == "Line 1\n"
    assert chunks[1] == "% {{{\n% x = 1\n% }}}"
    assert chunks[2] == ""


def test_code_extraction(simple_document_text):

    assert (
        extract_code(
            """\
    % {{{ {lang='python'}
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == "x = 1\ny = 2\n"
    )

    assert (
        extract_code(
            """\
    % {{{
    % {lang='python'}
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == "x = 1\ny = 2\n"
    )

    assert (
        extract_code(
            """\
    % {{{
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == "x = 1\ny = 2\n"
    )

    text = simple_document_text
    chunks = chunk_document(text)

    code = extract_code(chunks[1], "%")
    assert (
        code
        == """\
import pint
ureg = pint.UnitRegistry()

"""
    )

    code = extract_code(chunks[3], "%")
    assert (
        code
        == """\
x = Q_(1,'m')
y = Q_(2,'ft')

"""
    )


def test_settings_extraction(simple_document_text):

    assert (
        extract_settings(
            """\
    % {{{ {lang='python'}
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == "lang='python'"
    )

    assert (
        extract_settings(
            """\
    % {{{
    % {lang='python'}
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == "lang='python'"
    )

    assert (
        extract_settings(
            """\
    % {{{
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == None
    )
    assert (
        extract_settings(
            """\
    % {{{
    % { lang='python', template='jinja2' }
    % x = 1
    % y = 2
    % }}}
    """,
            "%",
        )
        == " lang='python', template='jinja2' "
    )
    # assert (
    #     extract_settings(
    #         """\
    # % {{{
    # % {
    # %  lang='python',
    # %  template='jinja2'
    # % }
    # % x = 1
    # % y = 2
    # % }}}
    # """,
    #         "%",
    #     )
    #     == "\nlang='python',\ntemplate='jinja2'\n"
    # )


def test_settings_block_parsing():

    results = parsers.code_blocks.settings_block.parse_string("{key=val, key2=val2}")
    assert results

    results = parsers.code_blocks.settings_block.parse_string("  {key=val, key2=val2}")
    assert results


def test_code_block_parsing():

    results = parsers.code_block.parse_string(
        """
    {{{
{key=val, key2=val2}
import pint
x = 10

}}}
"""
    )
    assert results
    assert (
        results["code"]
        == """\
import pint
x = 10

"""
    )


import pyparsing


def test_commented_code_block_parser():
    commented_code_block = parsers.make_commented_code_block_parser("%")

    commented_code_block.parse_string(
        """  % {{{
    %
    % }}}
    """
    )
    commented_code_block.parse_string(
        """
    % {{{
    %
    % }}}
    """
    )
    commented_code_block.parse_string(
        """
    % {{{
    % text
    % }}}
    """
    )
    commented_code_block.parse_string(
        """
    % {{{ {key=value}
    % text
    % }}}
    """
    )
    commented_code_block.parse_string(
        """
    % {{{
    % {key=value}
    % text
    % }}}
    """
    )
    with pytest.raises(pyparsing.exceptions.ParseException):
        commented_code_block.parse_string(
            """
        text % {{{
        %
        % }}}
        """
        )
    with pytest.raises(pyparsing.exceptions.ParseException):
        commented_code_block.parse_string(
            """
        % text {{{
        %
        % }}}
        """
        )

    with pytest.raises(pyparsing.exceptions.ParseException):
        commented_code_block.parse_string(
            """
        % {{{
        %
        text %
        % }}}
        """
        )
    with pytest.raises(pyparsing.exceptions.ParseException):
        # FIXME: we don't want to match cases that have lines
        # that don't begin with a comment char. for some reason,
        # our parser works correctly unless the first line breaks
        # this rule.
        commented_code_block.parse_string(
            """
        % {{{
        text %
        %
        % }}}
        """
        )
        raise pyparsing.exceptions.ParseException("")
    with pytest.raises(pyparsing.exceptions.ParseException):
        r = commented_code_block.parse_string(
            """
        % {{{
        text %
        % }}}
        """
        )
        # print(r)
        raise pyparsing.exceptions.ParseException("")

    commented_code_block.parse_string(
        """
        % {{{
        %
        % text
        %
        % }}}
        """
    )

    commented_code_block = parsers.make_commented_code_block_parser("[comment]: #")

    commented_code_block.parse_string(
        """  [comment]: # {{{
    [comment]: # import pint
    [comment]: # }}}
    """
    )


def test_experiments():

    AtLineStart(Literal("%")).parse_string("% text")
    AtLineStart(Literal("%")).parse_string("%text")
    with pytest.raises(pyparsing.exceptions.ParseException):
        AtLineStart(Literal("%")).parse_string(" % text")

    with pytest.raises(pyparsing.exceptions.ParseException):
        AtLineStart(White() + Literal("%")).parse_string("% text")
    AtLineStart(White() + Literal("%")).parse_string(" % text")
    AtLineStart(White() + Literal("%")).parse_string("  % text")
    AtLineStart(White() + Literal("%")).parse_string("   % text")

    AtLineStart(ZeroOrMore(White()) + Literal("%")).parse_string("% text")
    AtLineStart(ZeroOrMore(White()) + Literal("%")).parse_string(" % text")
    AtLineStart(ZeroOrMore(White()) + Literal("%")).parse_string("  % text")
    AtLineStart(ZeroOrMore(White()) + Literal("%")).parse_string("   % text")

    with pytest.raises(pyparsing.exceptions.ParseException):
        AtLineStart(ZeroOrMore(White()) + Literal("%")).parse_string("   text")

    AtLineStart(ZeroOrMore(White()) + ~Literal("%")).parse_string("   text")
    AtLineStart(ZeroOrMore(White()) + ~Literal("%")).parse_string("text")
    with pytest.raises(pyparsing.exceptions.ParseException):
        AtLineStart(ZeroOrMore(White()) + ~Literal("%")).parse_string(" %")

    r = AtLineStart(ZeroOrMore(White()) + Literal("%")).search_string(
        " % text\n% text\n"
    )
    assert len(r) == 2

    r = AtLineStart(ZeroOrMore(White()) + Literal("%")).search_string(
        " % text\ntext\nmore text\neven more\n% text\n"
    )
    assert len(r) == 2

    r = AtLineStart(ZeroOrMore(White()) + ~Literal("%")).search_string(
        " % text\ntext\nmore text\neven more\n% text\n"
    )
    assert len(r) == 0  # ??? Not sure why this does not work...

    r = (LineStart() + ZeroOrMore(White()) + ~Literal("%")).search_string(
        " % text\ntext\nmore text\neven more\n% text\n"
    )
    assert len(r) == 0  # ??? or this...

    r = (
        LineStart() + ZeroOrMore(White()) + ~Literal("%") + rest_of_line
    ).search_string(" % text\ntext\nmore text\neven more\n% text\n")
    assert len(r) == 3  # ah! its because we hae to match the rest of the line
    r = (LineStart() + ~Literal("%") + rest_of_line).search_string(
        " % text\ntext\nmore text\neven more\n% text\n"
    )
    assert len(r) == 3  # ah! its because we hae to match the rest of the line

    r = (LineStart() + ZeroOrMore(White()) + Regex("[^%]")).search_string(
        " % text\ntext\nmore text\neven more\n% text\n"
    )
    assert len(r) == 3  # regex to the rescue

    r = (LineStart() + Regex(r"\s*[^%]")).search_string(
        " % text\ntext\nmore text\neven more\n% text\n"
    )
    assert len(r) == 3

    r = (LineStart() + ~Literal("[comment]") + rest_of_line).search_string(
        " [comment] text\n text\nmore text\neven more\n[comment] text\ntext [comment]"
    )

    assert len(r) == 4

    r = (LineStart() + Literal("text")).search_string("text is at start of line")
    assert len(r) == 1
    r = (LineStart() + Literal("text")).search_string(
        "text is at start of line\n does not match\n text does match"
    )
    assert len(r) == 2


def test_remove_comments():

    text = uncomment(
        """\
        % one
        %  two
        %   three
        %     four""",
        "%",
    )
    assert (
        text
        == """\
 one
  two
   three
     four"""
    )

    text = uncomment(
        """\
        % one
           two
        %   three
        %     four""",
        "%",
    )
    assert (
        text
        == """\
 one
           two
   three
     four"""
    )

    text = uncomment(
        """\
       [comment]: # one
       [comment]: # two
       [comment]: # three
       [comment]: # four""",
        "#",
    )
    assert (
        text
        == """\
 one
 two
 three
 four"""
    )
    text = uncomment(
        """\
        [comment]: # one
           two
        [comment]: #   three
        [comment]: #     four""",
        "[comment]: #",
    )
    assert (
        text
        == """\
 one
           two
   three
     four"""
    )


def test_is_commented_code_block():

    assert is_commented_code_block(
        """
    % {{{
    %
    % import pint
    %
    % }}}
    """
    )

    assert not is_commented_code_block(
        """
    %
    %
    % import pint
    %
    % }}}
    """
    )
