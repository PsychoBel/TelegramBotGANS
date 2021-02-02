from typing import Dict
import dis, itertools
from types import CodeType


def count_operations(source_code: CodeType) -> Dict[str, int]:
    """Count byte code operations in given source code.

    :param source_code: the bytecode operation names to be extracted from
    :return: operation counts

    Usage example:
    >>> expected_value = {
    ...     'CALL_FUNCTION': 2,
    ...     'LOAD_CONST': 5,
    ...     'LOAD_NAME': 2,
    ...     'MAKE_FUNCTION': 1,
    ...     'POP_TOP': 1,
    ...     'RETURN_VALUE': 2,
    ...     'STORE_FAST': 1,
    ...     'STORE_NAME': 1,
    ... }
    ...
    >>> source = \"\"\"
    ... def sorted1(*args, **kwargs):
    ...     return sorted(*args, **kwargs)
    ... \"\"\"
    ...
    >>> count_operations(compile(source, '<string>', 'exec'))
    True
    """
    operation_counts = {}
    list_of_operations = dis.get_instructions(source_code)
    for operation in list_of_operations:
        if isinstance(operation.argval, CodeType):

            if operation.opname in operation_counts:
                operation_counts[operation.opname] += 1
            else:
                operation_counts.update({operation.opname: 1})
            operation_argval = count_operations(operation.argval)

            operation_counts = {x: operation_counts.get(x, 0) + operation_argval.get(x, 0) for x in
                         set(itertools.chain(operation_counts, operation_argval))}

        else:
            if operation.opname in operation_counts:
                operation_counts[operation.opname] += 1
            else:
                operation_counts.update({operation.opname: 1})

    operation_counts = {key: operation_counts[key] for key in sorted(operation_counts)}
    return operation_counts


if __name__ == "__main__":
    import doctest
    doctest.testmod()

