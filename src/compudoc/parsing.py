import textwrap

from pyparsing import *


class parsers:

    def make_commented_code_block_parser(
        comment_line_str, quote_beg_str="{{{", quite_end_str="}}}"
    ):
        """
        Given a string that identifies a comment to the end of line,
        return a parser that matches a commented code block.

        i.e., given '%', return a parser that matches

        % {{{
        %
        % }}}


        """
        begin_expr = Literal(comment_line_str) + Literal(quote_beg_str)
        end_expr = Literal(comment_line_str) + Literal(quite_end_str)

        commented_code_block_parser = begin_expr + SkipTo(
            end_expr,
            include=True,
            fail_on=(LineStart() + ~Literal(comment_line_str) + rest_of_line),
        )

        return commented_code_block_parser

    class code_blocks:
        settings_block = QuotedString(quote_char="{", end_quote_char="}")

    code_block = (
        Literal("{{{")
        + (
            code_blocks.settings_block.set_results_name("settings") + LineEnd()
            | LineEnd()
        )
        + SkipTo("}}}").leave_whitespace().set_results_name("code")
    )


def uncomment(text, comment_line_str):
    """
    Given a commented block of text, return an uncommented block.
    i.e. given

    % one
    %  two
    %   three

    with a comment_line_str = '%', return

     one
      two
       three

    _all_ characters before the comment character are removed.
    """
    lines = text.split("\n")
    for i in range(len(lines)):
        ibeg = lines[i].find(comment_line_str)
        if ibeg < 0:
            continue
        ibeg += len(comment_line_str)
        lines[i] = lines[i][ibeg:]
    return "\n".join(lines)


def is_commented_code_block(
    text, commented_code_block_parser=parsers.make_commented_code_block_parser("%")
):
    """
    Return true if text is a commented block of code. A commented block of code
    is a set of lines, each beginning with a comment char/string, with '{{{' and '}}}'
    markers at the top and bottom.

    i.e.

    % {{{
    % import pint
    % ureg = pint.UnitRegistry()
    % }}}
    """

    try:
        commented_code_block_parser.parse_string(text)
        return True
    except:
        return False


def extract_code(code_block, comment_line_str):
    """
    Extract code from a (possibly commented) code block.
    i.e., given

     {{{
     {key = val}
     import pint
     ureg = pint.UnitRegistry()
     }}}

    return

    import pint
    ureg = pint.UnitRegistry()
    """
    code = parsers.code_block.parse_string(uncomment(code_block, comment_line_str))[
        "code"
    ]
    code = textwrap.dedent(code)
    return code


def extract_settings(code_block, comment_line_str):
    """
    Extract settings from a (possibly commented) code block.
    i.e., given

     {{{
     {key = val}
     import pint
     ureg = pint.UnitRegistry()
     }}}

    return

    key = val
    """
    results = parsers.code_block.parse_string(uncomment(code_block, comment_line_str))
    if "settings" in results:
        return results["settings"]

    return None


def chunk_document(
    text, comment_block_parser=parsers.make_commented_code_block_parser("%")
):
    """
    Chunck a document into comment blocks and non-comment blocks. Comment blocks
    can be further processed to determine if they contain a code block.
    """
    blocks = []
    i = 0
    for match in original_text_for(comment_block_parser).scan_string(text):
        ibeg = match[1]
        iend = match[2]
        chunk = text[i:ibeg]
        blocks.append(chunk)

        chunk = text[ibeg : iend + 1]
        blocks.append(chunk)

        i = iend + 1
    chunk = text[i:]
    blocks.append(chunk)

    return blocks
