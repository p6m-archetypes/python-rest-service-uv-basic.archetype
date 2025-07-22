"""{{ PrefixName }} {{ SuffixName }} API module.

This module provides the business contracts layer including:
- Service interfaces
- Data transfer objects (DTOs)
- Business exceptions
"""

from .{{ prefix_name }}_service import {{ PrefixName }}{{ SuffixName }}
from .models import (
    {{ PrefixName }}Dto,
    Get{{ PrefixName }}Request,
    Get{{ PrefixName }}Response,
    Get{{ PrefixName }}sRequest,
    Get{{ PrefixName }}sResponse,
    Create{{ PrefixName }}Response,
    Update{{ PrefixName }}Response,
    Delete{{ PrefixName }}Request,
    Delete{{ PrefixName }}Response,
)
from .exception.error_code import ErrorCode
from .exception.service_exception import ServiceException

__all__ = [
    # Service interface
    "{{ PrefixName }}{{ SuffixName }}",
    
    # DTOs
    "{{ PrefixName }}Dto",
    "Get{{ PrefixName }}Request",
    "Get{{ PrefixName }}Response", 
    "Get{{ PrefixName }}sRequest",
    "Get{{ PrefixName }}sResponse",
    "Create{{ PrefixName }}Response",
    "Update{{ PrefixName }}Response",
    "Delete{{ PrefixName }}Request",
    "Delete{{ PrefixName }}Response",
    
    # Exceptions
    "ErrorCode",
    "ServiceException",
] 