from .server.server import start_server

C = u'''
**************************************************
*                 __               __  ___  ___  *
*  _______  ___  / /________ _____/ /_/ _ \/ _ ) *
* / __/ _ \/ _ \/ __/ __/ _ `/ __/ __/ // / _  | *
* \__/\___/_//_/\__/_/  \_,_/\__/\__/____/____/  *
*                                                *
**************  V E R S I O N   0.1  *************
'''

if __name__ == '__main__':
    print(C)
    start_server()