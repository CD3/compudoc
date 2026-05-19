import pytest

from compudoc.utils import *


def test_siunitx_si_parsing():
    v, u = parse_siunitx_si(r"\SI[]{9.8}{\meter\per\second\squared}")
    print(v, u)
    assert v == "9.8"
    assert u == "\meter\per\second\squared"
