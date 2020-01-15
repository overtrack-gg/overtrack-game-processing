from typing import TYPE_CHECKING, Any
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
elif TYPE_CHECKING:
    from typing_extensions import Literal
else:
    class _Literal:
        def __getitem__(self, typeargs: Any) -> Any: ...
    Literal = _Literal()
