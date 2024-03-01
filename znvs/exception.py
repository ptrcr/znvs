class ZnvsException(Exception):
    '''Base for all znvs exceptions.'''
    pass


class ValidationError(ZnvsException):
    '''Error raised when input parameters validation fails.'''
    pass
