import textwrap
from pathlib import Path

from pyparsing import *


class CommentLineParseHolder:
    """
    Class for storing a comment line parser based on a template pattern.
    """

    def __init__(self, template_pattern):
        self.__template_pattern = template_pattern
        self.__parser = make_comment_line_parser(template_pattern)

    @property
    def template_pattern(self):
        return self.__template_pattern

    @property
    def parser(self):
        return self.__parser


class CodeBlockParseHolder:
    """
    Class for stroring a commented code block based on a comment line template pattern.
    """

    def __init__(
        self, template_pattern, block_start_marker="{{{", block_end_marker="}}}"
    ):
        self.__comment_line = CommentLineParseHolder(template_pattern=template_pattern)

        code_tag = "{{CODE}}"
        pre_text, post_text = split_comment_line_pattern(template_pattern, code_tag)
        pre_parser, post_parser = make_pre_and_post_text_parsers(pre_text, post_text)

        self.block_start_marker = block_start_marker
        self.__block_start_parser = (
            Suppress(LineStart())
            + Group(pre_parser + Literal(block_start_marker)("CODE") + post_parser)
            + Suppress(LineEnd())
        )
        self.block_end_marker = block_end_marker
        self.__block_end_parser = (
            Suppress(LineStart())
            + Group(pre_parser + Literal(block_end_marker)("CODE") + post_parser)
            + Suppress(LineEnd())
        )

        self.__parser = (
            self.__block_start_parser("BLOCK_START")
            + ZeroOrMore(
                self.__comment_line.parser,
                stop_on=self.__block_end_parser,
            )("CODE_BLOCK")
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

    def comment_code(self, text, prefix=" "):
        """
        Return a comment code block that contains the code.
        """
        lines = []

        lines.append(
            self.__comment_line.template_pattern.replace(
                "{{CODE}}", prefix+self.block_start_marker
            )
        )
        if text.endswith("\n"):
            text = text[0:-1]
        for l in text.split("\n"):
            line = self.__comment_line.template_pattern.replace("{{CODE}}", prefix+l)
            lines.append(line)
        lines.append(
            self.__comment_line.template_pattern.replace(
                "{{CODE}}", prefix+self.block_end_marker
            )
        )

        return "\n".join(lines) + "\n"


def parse_code_split_file(filepath: Path):
    block_map = {}
    block_identifier_line_parser = Literal("#") + Combine(
        Literal("COMMENTED-CODE-BLOCK-") + Word(nums)
    )("ID")
    current_id = "PREAMBLE"
    with filepath.open() as f:
        for line in f:
            line = line.rstrip("\n")
            try:
                r = block_identifier_line_parser.parse_string(line)
                current_id = r["ID"]
                continue
            except:
                pass

            if current_id not in block_map:
                block_map[current_id] = []

            block_map[current_id].append(line)
    block_map = {k: "\n".join(block_map[k]) for k in block_map }
    return block_map


def make_comment_line_parser(pattern):
    """
    Create a comment line parser from a template pattern.
    e.g. "# {{CODE}}"
    """
    regex = r"\s*" + pattern.replace("{{CODE}}", "(?P<CODE>.*)")
    parser = Suppress(LineStart()) + Regex(regex) + Suppress(LineEnd())

    return parser


##################################################################


def split_comment_line_pattern(template_pattern, code_tag="{{CODE}}"):
    i = template_pattern.find(code_tag)
    if i == -1:
        raise RuntimeError(
            f"Invalid comment line pattern. pattern must contain '{code_tag}' tag."
        )

    pre_code_text = template_pattern[:i]
    post_code_text = template_pattern[i + len(code_tag) :]

    return pre_code_text, post_code_text


def make_pre_and_post_text_parsers(pre_text, post_text):
    pre_parser = Literal(pre_text)
    post_parser = Literal(post_text)
    post_parser.set_whitespace_chars(" \t")

    # if len(post_text) > -0:
    #     post_parser = Literal(post_text)
    #     post_parser.set_whitespace_chars(" \t")
    # else:
    #     post_parser = Empty()

    return pre_parser, post_parser


def make_commented_code_line_parser(template_pattern, code_tag="{{CODE}}"):
    """
    Create a comment line parser from a template pattern.
    e.g. "# {{CODE}}"
    """

    # split the pattern into pre and post texts around code_tag i.e. {{CODE}}
    pre_text, post_text = split_comment_line_pattern(template_pattern, code_tag)

    pre_parser, post_parser = make_pre_and_post_text_parsers(pre_text, post_text)

    code_parser = SkipTo(post_parser if type(post_parser) != Empty else LineEnd())
    code_parser.set_whitespace_chars("")

    line_parser = (
        pre_parser("PRE_CODE") + code_parser("CODE") + post_parser("POST_CODE")
    )("LINE")

    # parser = Suppress(LineStart()) + line_parser + Suppress(LineEnd())
    parser = line_parser

    return parser


def make_commented_marker_line_parser(
    template_pattern, marker_text, code_tag="{{CODE}}"
):
    # split the pattern into pre and post texts around code_tag i.e. {{CODE}}
    pre_text, post_text = split_comment_line_pattern(template_pattern, code_tag)

    pre_parser, post_parser = make_pre_and_post_text_parsers(pre_text, post_text)

    marker_parser = Literal(marker_text)
    line_parser = (
        pre_parser("PRE_MARKER") + marker_parser("MARKER") + post_parser("POST_MARKER")
    )("LINE")

    # parser = Suppress(LineStart()) + line_parser + Suppress(LineEnd())
    parser = line_parser

    return parser


def make_commented_code_block_parser(
    template_pattern,
    begin_marker_text="{{{",
    end_marker_text="}}}",
    code_tag="{{CODE}}",
):

    begin_marker_parser = make_commented_marker_line_parser(
        template_pattern, begin_marker_text, code_tag
    )("BEGIN_MARKER")
    end_marker_parser = make_commented_marker_line_parser(
        template_pattern, end_marker_text, code_tag
    )("END_MARKER")
    code_line_parser = make_commented_code_line_parser(template_pattern, code_tag)

    parser = (
        begin_marker_parser
        + ZeroOrMore(code_line_parser, stop_on=end_marker_parser)("CODE_LINES")
        + end_marker_parser
    )

    return parser
