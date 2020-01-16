from typing import TYPE_CHECKING, Any, Type
import sys

try:
    from typing import Literal
except:
    if sys.version_info >= (3, 8):
        from typing import Literal
    elif TYPE_CHECKING:
        from typing_extensions import Literal
    else:
        class _Literal:
            def __getitem__(self, typeargs: Any) -> Type[str]:
                return str
        Literal = _Literal()
