# -*- coding:utf-8 -*-


import platform
import wmi
from win32com.client import Dispatch


class Win32Info(object):
    """Windows平台信息"""

    def __init__(self):
        self.wmi_obj = wmi.WMI()  # 获得Windows平台接口
        self.wmi_service_obj = Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")

    def collect(self):
        """主要方法"""
        data = {
            'os_type': platform.system(),
            'os_release': "%s %s  %s " % (platform.release(), platform.architecture()[0], platform.version()),
            'os_distribution': 'Microsoft',
            'asset_type': 'server'
        }

        # 获取cpu、内存、主板、硬盘、网卡硬件信息
        data.update(self.get_cpu_info())
        data.update(self.get_disk_info())
        data.update(self.get_motherboard_info())
        data.update(self.get_nic_info())
        data.update(self.get_ram_info())
        return data

    def get_cpu_info(self):
        """CPU处理器"""
        data = {}
        cpu_lists = self.wmi_obj.Win32_Processor()  # Win32_Processor：该方法获得处理器对象列表
        cpu_core_count = 0
        for cpu in cpu_lists:
            cpu_core_count += cpu.NumberOfCores  # NumberOfCores：该属性获得单个处理器中逻辑核心数量
        cpu_model = cpu_lists[0].Name  # Name：该属性获得处理器型号
        data['cpu_count'] = len(cpu_lists)
        data['model'] = cpu_model
        data['cpu_core_count'] = cpu_core_count

        return data

    def get_ram_info(self):
        """记忆体(Random Access Memory)；内存；随机存储器"""
        data = []
        ram_collections = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")  #
        for ram in ram_collections:
            ram_size = int(int(ram.Capacity) / (1024 ** 3))  # Capacity：容积、体积
            item_data = {
                'slot': ram.DeviceLocator.strip(),  # DeviceLocator： 设备定位器
                'capacity': ram_size,
                'model': ram.Caption,  # 标题
                'manufacturer': ram.Manufacturer,
                'sn': ram.SerialNumber,
            }
            data.append(item_data)

        return {'item': data}

    def get_motherboard_info(self):
        """主板、母板"""
        computer_info = self.wmi_obj.Win32_ComputerSystem()[0]  # Win32_ComputerSystem：该方法获得计算机系统数据对象
        system_info = self.wmi_obj.Win32_OperatingSystem()[0]  # Win32_OperatingSystem：该方法获得操作系统数据对象
        data = {}
        data['manufacturer'] = computer_info.Manufacturer  # 制造商
        data['model'] = computer_info.Model  # 型号
        data['wake_up_type'] = computer_info.WakeUpType  # 唤醒类型
        data['sn'] = system_info.SerialNumber  # 序列号
        return data

    def get_disk_info(self):
        """磁盘、硬盘"""
        data = []
        for disk in self.wmi_obj.Win32_DiskDrive():  # Win32_DiskDrive：获得硬盘对象列表
            disk_data = {}
            interface_choices = ['SAS', 'SCSI', 'SATA', 'SSD']  # 硬盘接口种类
            for interface in interface_choices:
                if interface in disk.Model:
                    disk_data['interface_type'] = interface
                    break
            else:
                disk_data['interface_type'] = 'unknown'

            disk_data['slot'] = disk.Index
            disk_data['manufacturer'] = disk.Manufacturer
            disk_data['model'] = disk.Model
            disk_data['capacity'] = int(int(disk.Size) / (1024 ** 3))
            disk_data['sn'] = disk.SerialNumber
            data.append(disk_data)

        return {'physical_disk_driver': data}

    def get_nic_info(self):
        """网络接口卡(Network Interface Card)--->>> nic 网卡"""

        data = []
        for nic in self.wmi_obj.Win32_NetworkAdapterConfiguration():  # 网络配适器配置
            if nic.MACAddress is not None:
                nic_data = {}
                nic_data['mac'] = nic.MACAddress
                nic_data['model'] = nic.Caption
                nic_data['name'] = nic.Index
                if nic.IPAddress is not None:
                    nic_data['ip_address'] = nic.IPAddress[0]
                    nic_data['net_mask'] = nic.IPSubnet  # 子网掩码
                else:
                    nic_data['ip_address'] = ''
                    nic_data['net_mask'] = ''  # mask：掩码
                data.append(nic_data)
        return {'nic': data}


if __name__ == '__main__':
    # 测试方式一
    # data = Win32Info().collect()
    # for key in data:
    #     print(key, ":", data[key])

    # 测试方式二（美化输出）
    data = Win32Info().collect()
    from pprint import pprint

    pprint(data)
