__all__ = ['TippyError', 'CommandError', 'ParserError']

class TippyError(Exception): pass

class CommandError(TippyError): pass

class ParserError(TippyError): pass

class EnginError(TippyError): pass
