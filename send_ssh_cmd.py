def send_ssh_cmd(__cmd__, __stdin__ = None, __username__ = None, __password__= None , __IP__ = None , __port__ = None, __Packet__ = None, __openterminal__ = False):
    #__cmd__ : (string) command to be transitted to the Remote Machine using SSH
    #__username__ : (string) username for login for SSH to Remote Machine
    #__password__ : (string) password for login for SSH to Remote Machine
    #__IP__ : (string) IP address of Remote Machine
    #__Port__ : (int or int convertable string) port to connect through for SSH
    #__Packet__ : (dict) dict of information for connection, provides option for single variable data entry for connection {'username':, 'password':, 'host':}
    #__stdin__ : (iterable OR string) list of stdins
    #__openterminal__ : (boolean) if True open a terminal window on the Remote Machine else runs the command blindly

    try:
        import paramiko
        import numpy as np
        import time
    except:
        print("error importing modules")
        return
  
    #unpacks the dict 
    if __Packet__ is not None:
        print("unpacking connection packet")
        __username__ = __packet__['username']
        __password__ = __packet__['password']
        __IP__ = __packet__['host']

    ##Method
    try:
        ssh_client = paramiko.SSHClient() #creates SSH object - this is NOT the same as an FTP connection SSH is how we connect to things to send them terminal commands
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #adds a policy to ignore a missing host key
        ssh_client.connect(hostname=__IP__,username=__username__,password=__password__) #establishes the connection to the remote PC

        #option to blindly execute command or open terminal window and execute within this window
        if __openterminal__ == False:
            stdin, stdout, stderr = ssh_client.exec_command(__cmd__) 
        else:
            stdin, stdout, stderr = ssh_client.exec_command(f'export DISPLAY=:0.0 && gnome-terminal -- bash -login -c "{__cmd__}; exec bash"')

        execution_time = time.time() #store execution time for return

        #option to supply an input to stdin
        if __stdin__ is not None:
            if str(type(__stdin__)) == "<class 'str'>":
                stdin.write(f"{__stdin__}\n")
                stdin.flush()
                print(f"executed cmd: {__cmd__} with input: {__stdin__}")
            elif str(type(__stdin__)) == "<class 'list'>":
                for i in __stdin__:
                    stdin.write(f"{__stdin__[i]}\n")
                stdin.flush()
                print(f"executed cmd: {__cmd__} with list of inputs")

        else:
            print(f"executed cmd: {__cmd__} with no inputs")

        print("Terminal Output:")
        for line in iter(stdout.readline, ""):
            print(line, end="")
        print("Terminal Error:")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        print("Closing Connection...")
        ssh_client.close()
        print("Connection Closed")
    except Exception as e:
        print(f"Error: {e}")

    return stdout, stderr, execution_time