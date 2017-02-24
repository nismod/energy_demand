#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import energy_demand.main_functions as mf


def test_conversion_ktoe_gwh():

    # in test value
    in_value = 10
    expected = in_value * 11.6300000

    # call function
    out_value = mf.conversion_ktoe_gwh(in_value)

    assert out_value == expected
# ----
'''
def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
'''