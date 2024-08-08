#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **type-checking function code magic** (i.e., global string
constants embedded in the implementations of functions type-checking arbitrary
objects against arbitrary PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ NAMES                              }....................
NAME_PREFIX = '__beartype_'
'''
Substring prefixing the names of all *other* global string constants declared by
this submodule.
'''

# ....................{ NAMES ~ func                       }....................
FUNC_CHECKER_NAME_PREFIX = f'{NAME_PREFIX}checker_'
'''
Substring prefixing the unqualified basenames of all type-checking raiser and
tester functions created by the
:func:`beartype._check.checkmake._make_func_checker` factory function.
'''

# ....................{ NAMES ~ parameter                  }....................
# To avoid colliding with the names of arbitrary caller-defined parameters, the
# beartype-specific parameter names *MUST* be prefixed by "__beartype_".

ARG_NAME_CONF = f'{NAME_PREFIX}conf'
'''
Name of the **private beartype configuration parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the
:class:`beartype.BeartypeConf` instance configuring each wrapper function
generated by the :func:`beartype.beartype` decorator).
'''


ARG_NAME_CLS_STACK = f'{NAME_PREFIX}cls_stack'
'''
Name of the **private decorated type stack parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the type stack
conditionally passed to wrappers generated by the :func:`beartype.beartype`
decorator whose type-checking logic requires one or more of the classes
lexically containing the decorated methods wrapped by these wrappers).
'''


ARG_NAME_EXCEPTION_PREFIX = f'{NAME_PREFIX}exception_prefix'
'''
Name of the **private exception prefix parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the human-readable
label prefixing the representation of the currently type-checked object in
exception messages raised when this object violates its type hint, conditionally
passed to wrappers generated by the :func:`beartype.door.die_if_unbearable`
type-checker injected for :pep:`526`-compliant annotated variable assignments by
:mod:`beartype.claw`-published import hooks).
'''


ARG_NAME_FUNC = f'{NAME_PREFIX}func'
'''
Name of the **private decorated callable parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the decorated
callable passed to each wrapper function generated by the
:func:`beartype.beartype` decorator).
'''


ARG_NAME_GETRANDBITS = f'{NAME_PREFIX}getrandbits'
'''
Name of the **private getrandbits parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the highly performant C-based
:func:`random.getrandbits` function conditionally passed to wrappers generated
by the :func:`beartype.beartype` decorator whose type-checking logic requires
one or more random integers).
'''


ARG_NAME_GET_VIOLATION = f'{NAME_PREFIX}get_violation'
'''
Name of the **private exception raising parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the
:func:`beartype._check.error.errorget.get_func_pith_violation`
function raising human-readable exceptions on call-time type-checking failures
passed to each wrapper function generated by the :func:`beartype.beartype`
decorator).
'''


ARG_NAME_HINT = f'{NAME_PREFIX}hint'
'''
Name of the **private type hint parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the user-defined type hint unconditionally
passed to the current wrapper function generated by the
:func:`beartype.door.die_if_unbearable` type-checker receiving that hint).
'''


#FIXME: Excise us up, pleas. This should no longer be required.
ARG_NAME_TYPISTRY = f'{NAME_PREFIX}typistry'
'''
Name of the **private beartypistry parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the beartypistry singleton conditionally
passed to every wrapper function generated by the :func:`beartype.beartype`
decorator requiring one or more types or tuples of types cached by this
singleton).
'''


ARG_NAME_WARN = f'{NAME_PREFIX}warn'
'''
Name of the **standard warn function** (i.e., :mod:`beartype`-specific
parameter whose default value is the :func:`warnings.warn` function
conditionally passed to every wrapper function generated by the
:func:`beartype.beartype` decorator configured by either the
:attr:`beartype.BeartypeConf.violation_param_type` or
:attr:`beartype.BeartypeConf.violation_return_type` options to emit
non-fatal warnings rather than raise fatal exceptions).
'''

# ....................{ NAMES ~ var                        }....................
VAR_NAME_ARGS_LEN = f'{NAME_PREFIX}args_len'
'''
Name of the local variable providing the **positional argument count** (i.e.,
number of positional arguments passed to the current call).
'''


VAR_NAME_RANDOM_INT = f'{NAME_PREFIX}random_int'
'''
Name of the local variable providing a **pseudo-random integer** (i.e.,
unsigned 32-bit integer pseudo-randomly generated for subsequent use in
type-checking randomly indexed container items by the current call).
'''


VAR_NAME_VIOLATION = f'{NAME_PREFIX}violation'
'''
Name of the local variable providing the **violation exception** (i.e.,
exception describing a type-checking violation to be either raised as a fatal
exception or emitted as a non-fatal warning by the current call as configured by
the :attr:`beartype.BeartypeConf.violation_param_type` and
:attr:`beartype.BeartypeConf.violation_return_type` options).
'''

# ....................{ NAMES ~ var : pith                 }....................
VAR_NAME_PITH_PREFIX = f'{NAME_PREFIX}pith_'
'''
Substring prefixing all local variables providing a **pith** (i.e., either the
current parameter or return value *or* item contained in the current parameter
or return value type-checked by the current call).
'''


VAR_NAME_PITH_ROOT = f'{VAR_NAME_PITH_PREFIX}0'
'''
Name of the local variable providing the **root pith** (i.e., value of the
current parameter or return value being type-checked by the current call).
'''

# ....................{ CODE ~ pith                        }....................
CODE_PITH_ROOT_NAME_PLACEHOLDER = '?|PITH_ROOT_NAME`^'
'''
Placeholder source substring to be globally replaced by the **root pith name**
(i.e., name of the current parameter if called by the
:func:`pep_code_check_param` function *or* ``return`` if called by the
:func:`pep_code_check_return` function) in the parameter- and return-agnostic
code generated by the memoized
:func:`beartype._check.checkmake.make_code_raiser_func_pith_check` function.

See Also
--------
:attr:`beartype._data.error.dataerrmagic.EXCEPTION_PLACEHOLDER`
    Related commentary.
'''
