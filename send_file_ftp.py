### send_file_ftp.py
#created by N.Gulati

def send_file_ftp():
    try:
        import paramiko
        import numpy as np
        import time
    except Exception as E:
        print("error importing modules")
        print(E)
        return