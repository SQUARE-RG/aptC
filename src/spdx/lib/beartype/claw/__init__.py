#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook API.**

This subpackage publishes :pep:`302`- and :pep:`451`-compliant import hooks
enabling external callers to automatically decorate well-typed third-party
packages and modules with runtime type-checking dynamically generated by the
:func:`beartype.beartype` decorator in a single line of code.
'''

# ....................{ TODO                               }....................
#FIXME: Technically, we're not quite done here. The "beartype.claw" API
#currently silently ignores attempts to subject the "beartype" package itself to
#@beartyping. Ideally, that API should instead raise human-readable exceptions
#when users explicitly attempt to do so when calling either the
#beartype_package() or beartype_packages() functions. After implementing that
#functionality, assert that in our test suite, please.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.claw._clawmain import (
    beartype_all as beartype_all,
    beartype_package as beartype_package,
    beartype_packages as beartype_packages,
    beartype_this_package as beartype_this_package,
)
from beartype.claw._pkg.clawpkgcontext import (
    beartyping as beartyping,
)
