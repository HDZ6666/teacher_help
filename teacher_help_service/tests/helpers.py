from contextlib import contextmanager

import pytest

from exceptions.exception import ServiceException


@contextmanager
def raises_service(fragment: str = ''):
    """
    断言抛出 ServiceException 且 message 包含指定片段（ServiceException 的 str() 为空，不能用 match）
    """
    with pytest.raises(ServiceException) as info:
        yield info
    assert fragment in (info.value.message or ''), info.value.message
