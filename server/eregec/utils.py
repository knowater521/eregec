
__M_COLOR = "\033[0m"
__E_COLOR = "\033[31m"
__W_COLOR = "\033[35m"
__I_COLOR = "\033[33m"
__R_COLOR = "\033[0m"

def perror(string):
    print(__M_COLOR + 'EregecServer: ' + __E_COLOR + 'Error: ' + string + __R_COLOR)

def pwarning(string):
    print(__M_COLOR + 'EregecServer: ' + __W_COLOR + 'Warning: ' + string + __R_COLOR)

def pinfo(string):
    print(__M_COLOR + 'EregecServer: ' + __I_COLOR + 'Info: ' + string + __R_COLOR)