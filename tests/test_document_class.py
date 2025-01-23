import pytest

from compudoc.document import *


def test_document_building():
    doc = Document()

    assert len(list(doc.iter_blocks())) == 0

    b = TextBlock("Hi")
    assert b.text == "Hi"
    doc.append(b)

    b = CodeBlock("import pint")
    assert b.text == "import pint"
    doc.append(b)

    b = TextBlock("Bye")
    assert b.text == "Bye"
    doc.append(b)

    assert len(list(doc.iter_blocks())) == 3



def test_parsing_1():
    text = """
Line 1
Line 2
% {{{
% import pathlib
% }}}
Line 3
% {{{
% cwd = pathlib.Path()
% }}}
Line 4: {{cwd}}
"""

    doc = Document()
    with pytest.raises(RuntimeError) as e:
        doc.parse(text)

    doc.set_comment_block_parser(CodeBlockParser("%"))
    doc.parse(text)


    assert len(list(doc.iter_blocks())) == 5
    assert len(list(doc.iter_code_blocks())) == 2
    assert len(list(doc.iter_text_blocks())) == 3

    assert len(list(doc.enumerate_code_blocks())) == 2
    assert len(list(doc.enumerate_text_blocks())) == 3

    code_blocks_enumeration = list(doc.enumerate_code_blocks())

    assert code_blocks_enumeration[0][0] == 1
    assert code_blocks_enumeration[0][1].text == "% {{{\n% import pathlib\n% }}}\n"
    assert code_blocks_enumeration[1][0] == 3
    assert (
        code_blocks_enumeration[1][1].text == "% {{{\n% cwd = pathlib.Path()\n% }}}\n"
    )

    text_blocks_enumeration = list(doc.enumerate_text_blocks())

    assert text_blocks_enumeration[0][0] == 0
    assert text_blocks_enumeration[0][1].text == "\nLine 1\nLine 2\n"
    assert text_blocks_enumeration[1][0] == 2
    assert text_blocks_enumeration[1][1].text == "Line 3\n"
    assert text_blocks_enumeration[2][0] == 4
    assert text_blocks_enumeration[2][1].text == "Line 4: {{cwd}}\n"

    with pytest.raises(RuntimeError) as e:
        rendered_text = doc.render()
    doc.set_template_engine(Jinja2())
    with pytest.raises(RuntimeError) as e:
        rendered_text = doc.render()
    doc.set_execution_engine(Python())
    rendered_text = doc.render()

    assert rendered_text == """
Line 1
Line 2
% {{{
% import pathlib
% }}}
Line 3
% {{{
% cwd = pathlib.Path()
% }}}
Line 4: .
"""
