import paramiko
password = "1pepper2"
NAO_IP = '192.168.1.101'
p = paramiko.SSHClient()
p.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())  # This script doesn't work for me unless this line is added!
p.connect(NAO_IP, port=22, username="nao", password=password)
stdin, stdout, stderr = p.exec_command("qicli call ALTabletService._openSettings")
opt = stdout.readlines()
opt = "".join(opt)
print(opt)