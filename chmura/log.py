from lo3.settings import LOGGING_LEVEL, LOGGING_COLORS

LOGGING_LEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRIT']

if LOGGING_COLORS:
    class TermColors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
else:
    class TermColors:
        HEADER = ''
        OKBLUE = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''


def debug(message, params=''):
    send_msg(message, params, 'DEBUG', TermColors.OKBLUE)


def info(message, params=''):
    send_msg(message, params, 'INFO', TermColors.ENDC)


def warning(message, params=''):
    send_msg(message, params, 'WARN', TermColors.WARNING)


def error(message, params=''):
    send_msg(message, params, 'ERROR', TermColors.FAIL)


def crititcal(message, params=''):
    send_msg(message, params, 'CRIT', TermColors.FAIL + TermColors.BOLD)


def send_msg(message, params, typ, color):
    try:
        if LOGGING_LEVELS.index(typ) < LOGGING_LEVELS.index(LOGGING_LEVEL):
            return
    except ValueError:
        print(TermColors.FAIL + TermColors.BOLD + '[SYNTAX ERROR] Undefined log type(', typ,
              ') or LOGGING_LEVEL(', LOGGING_LEVEL, ')!!!' + TermColors.ENDC)
    if params is not '':
        params = '{' + params + '}'
    print(color + '[' + typ + ']', message, params + TermColors.ENDC)
