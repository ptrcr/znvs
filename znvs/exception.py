class ZnvsException(Exception):
    '''Base for all znvs exceptions.'''
    pass


class ParameterError(ZnvsException):
    '''Error raised when input parameters validation fails.'''
    pass


class ChecksumError(ZnvsException):
    '''Error raised when NVS entry validation fails.'''
    pass
