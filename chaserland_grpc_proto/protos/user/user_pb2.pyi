from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OAuthProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OAUTH_PROVIDER_UNSPECIFIED: _ClassVar[OAuthProvider]
    OAUTH_PROVIDER_GITHUB: _ClassVar[OAuthProvider]
OAUTH_PROVIDER_UNSPECIFIED: OAuthProvider
OAUTH_PROVIDER_GITHUB: OAuthProvider

class OAuthLoginRequest(_message.Message):
    __slots__ = ("code", "provider")
    CODE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    code: str
    provider: OAuthProvider
    def __init__(self, code: _Optional[str] = ..., provider: _Optional[_Union[OAuthProvider, str]] = ...) -> None: ...

class OAuthLoginResponse(_message.Message):
    __slots__ = ("access_token", "token_type")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    token_type: str
    def __init__(self, access_token: _Optional[str] = ..., token_type: _Optional[str] = ...) -> None: ...
