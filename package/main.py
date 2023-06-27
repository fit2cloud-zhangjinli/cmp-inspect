# _*_ coding: utf-8 _*_
"""
Time:     2023/5/17 下午2:26
Author:   JinLi
Version:  V 0.1
File:     main.py
"""

from package.utils.base import MySSH


if __name__ == "__main__":
    ssh = MySSH("10.1.13.107", "root", "Fit2cloud@2023", 22)
    ssh.Init()
    ref = ssh.BatchCMD('uname')
    ssh.GetAllDiskSpace()
    ssh.GetAllMemSpace()
    # result = stdout.read().decode('utf-8')
    print(ref)
    ssh.GetPing()
    ssh.CloseSSH()



