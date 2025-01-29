import textwrap

from pyparsing import *


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
        for match in self.__parser.scan_string(text, always_skip_whitespace=False):
            # scan_string will include blank lines in front of
            # comment blocks with the comment blocks. So we want to manually
            # skip these
            ibeg = match[1]
            iend = match[2]
            while text[ibeg] == "\n" and ibeg < iend:
                ibeg += 1
            yield (match[0], ibeg, iend)

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
