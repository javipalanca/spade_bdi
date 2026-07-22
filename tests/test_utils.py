import pytest

from spade_bdi.utils import parse_literal


testdata = [
    ("predicate", "predicate", ""),
    ("foo(42)", "foo", (42,)),
    ("foo('bar')", "foo", ("bar",)),
    ("foo(1, 2)", "foo", ((1, 2),)),
]


@pytest.mark.parametrize("predicate,functor_exp,args_exp", testdata)
def test_parse_literal_parameters(predicate, functor_exp, args_exp):
    functor, args = parse_literal(predicate)
    assert functor == functor_exp
    assert args == args_exp
