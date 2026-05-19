from pyparsing import (
    Combine,
    Group,
    Literal,
    OneOrMore,
    Optional,
    ParseException,
    Suppress,
    Word,
    alphanums,
    alphas,
    nums,
)


class parsers:
    class latex:
        # ---- basic tokens ----
        lbrace = Suppress("{")
        rbrace = Suppress("}")
        lbrack = Suppress("[")
        rbrack = Suppress("]")

        backslash = Literal("\\")

        # ---- number parser (e.g., 9.3, 10, -2.1) ----
        sign = Optional(Literal("-") | Literal("+"))
        integer = Word(nums)
        float_part = Combine(integer + "." + integer)
        number = Combine(sign + (float_part | integer))("value")

        # ---- latex command like \meter or \second ----
        command = Combine(backslash + Word(alphas))("cmd")

        # ---- unit parser: sequence of commands ----
        # e.g. \meter\per\second
        unit = Combine(OneOrMore(command))("unit")

        # ---- optional arguments [] ----
        opt_arg = Suppress(lbrack + Optional(Word(alphanums)) + rbrack)

        # ---- full \SI parser ----
        si = (
            Suppress(Literal("\\SI"))
            + Optional(opt_arg)
            + lbrace
            + number
            + rbrace
            + lbrace
            + unit
            + rbrace
        )


# ---- wrapper function ----
def parse_siunitx_si(s: str):
    try:
        result = parsers.latex.si.parse_string(s, parse_all=True)
        return result["value"], result["unit"][0]
    except ParseException as e:
        raise ValueError(f"Could not parse input: {s}") from e
