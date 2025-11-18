
_log = None


def _my_log_set(l):
    global _log
    
    _log = l

def _my_print(s: str):
    global _log

    if _log is None:
        print(s)
        return

    #
    _log.my_print(s)