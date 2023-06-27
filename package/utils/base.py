import paramiko
import math


class MySSH:
    def __init__(self, address, username, password, default_port):
        self.address = address
        self.default_port = default_port
        self.username = username
        self.password = password

    def Init(self):
        try:
            self.ssh_obj = paramiko.SSHClient()
            self.ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_obj.connect(self.address, self.default_port, self.username, self.password, timeout=3,
                                 allow_agent=False, look_for_keys=False)
            self.sftp_obj = self.ssh_obj.open_sftp()
        except Exception:
            return False

    def BatchCMD(self, command):
        try:
            stdin, stdout, stderr = self.ssh_obj.exec_command(command, timeout=3)
            result = stdout.read()
            if len(result) != 0:
                result = str(result).replace("\\n", "\n")
                result = result.replace("b'", "").replace("'", "")
                return result
            else:
                return None
        except Exception:
            return None

    def CloseSSH(self):
        try:
            self.sftp_obj.close()
            self.ssh_obj.close()
        except Exception:
            pass

    def GetSystemVersion(self):
        return self.BatchCMD("uname")

    # 测试主机连通率
    def GetPing(self):
        try:
            if self.GetSystemVersion() != None:
                print("{} 已连通.".format(self.address))
                return True
            else:
                return False
        except Exception:
            return False

    # 拉取磁盘数据到本地，并返回字典
    def GetAllDiskSpace(self):
        ref_dict = {}
        cmd_dict = {"Linux\n": "df | grep -v 'Filesystem' | awk '{print $5 \":\" $6}'",
                    "AIX\n": "df | grep -v 'Filesystem' | awk '{print $4 \":\" $7}'"
                    }
        try:
            os_version = self.GetSystemVersion()
            for version, run_cmd in cmd_dict.items():
                if (version == os_version):
                    os_ref = self.BatchCMD(run_cmd)
                    ref_list = os_ref.split("\n")
                    for each in ref_list:
                        if each != "":
                            ref_dict[str(each.split(":")[1])] = str(each.split(":")[0])
            print("利用率字典: {}".format(ref_dict))
            return ref_dict
        except Exception:
            return False

    # 拉取内存数据到本地。
    def GetAllMemSpace(self):
        cmd_dict = {"Linux\n": "cat /proc/meminfo | head -n 2 | awk '{print $2}' | xargs | awk '{print $1 \":\" $2}'",
                    "AIX\n": "svmon -G | grep -v 'virtual' | head -n 1 | awk '{print $2 \":\" $4}'"
                    }
        try:
            os_version = self.GetSystemVersion()
            for version, run_cmd in cmd_dict.items():
                if (version == os_version):
                    os_ref = self.BatchCMD(run_cmd)
                    mem_total = math.ceil(int(os_ref.split(":")[0].replace("\n", "")) / 1024)
                    mem_free = math.ceil(int(os_ref.split(":")[1].replace("\n", "")) / 1024)
                    percentage = 100 - int(mem_free / int(mem_total / 100))
                    print("利用百分比: {}  \t 总内存: {}  \t 剩余内存: {}".format(percentage, mem_total, mem_free))
                    return str(percentage) + " %"
        except Exception:
            return False

    # 获取CPU利用率数据
    def GetCPUPercentage(self):
        ref_dict = {}
        cmd_dict = {"Linux\n": "vmstat | tail -n 1 | awk '{print $13 \":\" $14 \":\" $15}'",
                    "AIX\n": "vmstat | tail -n 1 | awk '{print $14 \":\" $15 \":\" $16}'"
                    }
        try:
            os_version = self.GetSystemVersion()
            for version, run_cmd in cmd_dict.items():
                if (version == os_version):
                    os_ref = self.BatchCMD(run_cmd)
                    ref_list = os_ref.split("\n")
                    for each in ref_list:
                        if each != "":
                            each = each.split(":")
                            ref_dict = {"us": each[0], "sys": each[1], "idea": each[2]}
            print("CPU利用率数据: {}".format(ref_dict))
            return ref_dict
        except Exception:
            return False

    # 获取到系统负载利用率 也就是一分钟负载五分钟负载十五分钟负载
    def GetLoadAVG(self):
        ref_dict = {}
        cmd_dict = {"Linux\n": "cat /proc/loadavg | awk '{print $1 \":\" $2 \":\" $3}'",
                    "AIX\n": "uptime | awk '{print $10 \":\" $11 \":\" $12}'"
                    }
        try:
            os_version = self.GetSystemVersion()
            for version, run_cmd in cmd_dict.items():
                if (version == os_version):
                    os_ref = self.BatchCMD(run_cmd)
                    ref_list = os_ref.split("\n")
                    for each in ref_list:
                        if each != "":
                            each = each.replace(",", "").split(":")
                            ref_dict = {"1avg": each[0], "5avg": each[1], "15avg": each[2]}
                            print("负载利用率: {}".format(ref_dict))
                            return ref_dict
            return False
        except Exception:
            return False

    # 检测指定进程是否存活
    def CheckProcessStatus(self, processname):
        cmd_dict = {
            "Linux\n": "ps aux | grep '{0}' | grep -v 'grep' | awk {1} | wc -l".format(processname, "{'print $2'}"),
            "AIX\n": "ps aux | grep '{0}' | grep -v 'grep' | awk {1} | wc -l".format(processname, "{'print $2'}")
        }
        try:
            os_version = self.GetSystemVersion()
            for version, run_cmd in cmd_dict.items():
                if (version == os_version):
                    os_ref = self.BatchCMD(run_cmd)
                    ret_flag = str(os_ref.split("\n")[0].replace(" ", "").strip())
                    if ret_flag != "0":
                        return True
            return False
        except Exception:
            return "None"

    # 检测指定端口是否存活
    def CheckPortStatus(self, port):
        cmd_dict = {"Linux\n": "netstat -antp | grep {0} | awk {1}".format(port, "{'print $6'}")
            , "AIX\n": "netstat -ant | grep {0} | head -n 1 | awk {1}".format(port, "{'print $6'}")
                    }
        try:
            os_version = self.GetSystemVersion()
            for version, run_cmd in cmd_dict.items():
                if (version == os_version):
                    os_ref = self.BatchCMD(run_cmd)
                    ret_flag = str(os_ref.split("\n")[0].replace(" ", "").strip())
                    if ret_flag == "LISTEN" or ret_flag == "ESTABLISHED":
                        return True
            return False
        except Exception:
            return False


