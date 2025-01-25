import textwrap

from pyparsing import *


class CodeBlockParser:
    def __init__(self, comment_line_str):
        self.__comment_line_str = comment_line_str
        self.__parser = parsers.make_commented_code_block_parser(
            self.__comment_line_str
        )

    @property
    def comment_line_str(self):
        return self.__comment_line_str

    @property
    def parser(self):
        return self.__parser


class CommentLine:
    """
    Class for storing a comment line parser based on a template pattern.
    """

    def __init__(self, template_pattern):
        self.__template_pattern = template_pattern
        self.__parser = parsers.make_comment_line_parser(template_pattern)

    @property
    def template_pattern(self):
        return self.__template_pattern

    @property
    def parser(self):
        return self.__parser


class CommentCodeBlock:
    """
    Class for stroring a commented code block based on a comment line template pattern.
    """

    def __init__(
        self, template_pattern, block_start_marker="{{{", block_end_marker="}}}"
    ):
        self.__comment_line = CommentLine(template_pattern=template_pattern)
        self.block_start_marker = block_start_marker
        self.__block_start_parser = parsers.make_comment_line_parser(
            template_pattern.replace(
                "{{CODE}}", r"\s*(?P<CODE>" + block_start_marker + ")"
            )
        )
        self.block_end_marker = block_end_marker
        self.__block_end_parser = parsers.make_comment_line_parser(
            template_pattern.replace(
                "{{CODE}}", r"\s*(?P<CODE>" + block_end_marker + ")"
            )
        )

        self.__parser = (
            self.__block_start_parser("BLOCK_START")
            + ZeroOrMore(self.__comment_line.parser, stop_on=self.__block_end_parser)(
                "CODE_BLOCK"
            )
            + self.__block_end_parser("BLOCK_END")
        )

    @property
    def parser(self):
        return self.__parser

    @property
    def comment_line_parser(self):
        return self.__comment_line.parser

    @property
    def block_start_parser(self):
        return self.__block_start_parser

    @property
    def block_end_parser(self):
        return self.__block_end_parser

    def is_comment_code_block(self, text):
        try:
            result = self.__parser.parse_string(text)
            return True
        except:
            return False

    def get_comment_code_blocks(self, text):
        """
        Return all comment code blocks in text.
        """
        for match in self.__parser.scan_string(text):
            yield match

    def extract_code(self, text):
        """
        Extract code from a comment code block.
        """
        if not self.is_comment_code_block(text):
            return ""

        lines: list[str] = []

        results = self.__parser.parse_string(text)
        for result in results["CODE_BLOCK"]:
            line = self.__comment_line.parser.parse_string(result)["CODE"]
            lines.append(line)

        return textwrap.dedent("\n".join(lines) + "\n")

    def comment_code(self, text):
        """
        Return a comment code block that contains the code.
        """
        lines = []

        lines.append(
            self.__comment_line.template_pattern.replace(
                "{{CODE}}", self.block_start_marker
            )
        )
        if text.endswith("\n"):
            text = text[0:-1]
        for l in text.split("\n"):
            line = self.__comment_line.template_pattern.replace("{{CODE}}", l)
            lines.append(line)
        lines.append(
            self.__comment_line.template_pattern.replace(
                "{{CODE}}", self.block_end_marker
            )
        )

        return "\n".join(lines) + "\n"


class parsers:

    def make_comment_line_parser(pattern):
        """
        Create a comment line parser from a template pattern.
        e.g. "# {{CODE}}"
        """
        regex = r"\s*" + pattern.replace("{{CODE}}", "(?P<CODE>.*)")
        parser = Suppress(LineStart()) + Regex(regex) + Suppress(LineEnd())

        return parser

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
