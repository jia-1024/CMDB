# -*- coding:utf-8 -*-


import subprocess


def collect():
    """
    Linux平台下主要信息收集函数
    关键接口为：dmidecode-->>> DMI（Desktop Management Interface,DMI）
    """

    filter_keys = ['Manufacturer', 'Serial Number', 'Product Name', 'UUID', 'Wake-up Type']
    raw_data = {}

    for key in filter_keys:
        try:
            res = subprocess.Popen('sudo dmidecode -t system|grep {}'.format(key), stdout=subprocess.PIPE, shell=True)
            result = res.stdout.read().decode()
            data_list = result.split(':')
            if data_list.__len__() > 1:
                raw_data[key] = data_list[1].strip()
            else:
                raw_data[key] = ''
        except Exception as e:
            print(e)
            raw_data[key] = ''
    data = dict()
    data['asset_type'] = 'server'
    data['manufacturer'] = raw_data['Manufacturer']
    data['sn'] = raw_data['Serial Number']
    data['model'] = raw_data['Product Name']
    data['uuid'] = raw_data['UUID']
    data['wake_up_type'] = raw_data['Wake-up Type']

    # TODO 获取硬件信息例如 硬盘，内存，网卡，cpu，操作系统等等
    data.update(get_os_info())  # 获取操作系统信息
    data.update(get_cpu_info())  # 获取CPU信息
    data.update(get_ram_info())  # 获取内存信息
    data.update(get_nic_info())  # 网卡信息
    data.update(get_disk_info())  # 硬盘信息
    return data


def get_os_info():
    """
    获得操作系统相关信息
    系统关键API接口为：lsb——release--->>>>Linux Standard Base
    """

    distributor = subprocess.Popen('lsb_release -a|grep {}'.format('Distributor ID'), stdout=subprocess.PIPE,
                                   shell=True)
    distributor = distributor.stdout.read().decode().split(':')
    release = subprocess.Popen('lsb_release -a|grep {}'.format('Description'), stdout=subprocess.PIPE, shell=True)
    release = release.stdout.read().decode().split(':')
    data_dic = {
        'os_distributor': distributor,
        'os_release': release,
        'os_type': 'Linux',
    }
    return data_dic


def get_cpu_info():
    """
    获取CPU硬件信息
    关键指令：cat /proc/cpuinfo
    :return:
    """

    raw_cmd = 'cat /proc/cpuinfo'
    raw_data = {
        'cpu_model': '{} |grep "model name" | head -1'.format(raw_cmd),
        'cpu_count': '{} |grep "processor"|wc -l'.format(raw_cmd),
        'cpu_core_count': "%s |grep 'cpu cores' |awk -F: '{SUM +=$2} END {print SUM}'" % raw_cmd,
    }
    for key, cmd in raw_data.items():
        try:
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            raw_data[key] = result.stdout.read().decode().strip()
        except ValueError as e:
            raw_data[key] = ''
    data = {
        'cpu_model': raw_data['cpu_count'],
        'cpu_core_count': raw_data['cpu_core_count'],
    }
    cpu_model = raw_data['cpu_model'].split(':')
    if len(cpu_model) > 1:
        data['cpu_model'] = cpu_model
    else:
        data['cpu_model'] = ''
    return data


def get_ram_info():
    """
    获得内存信息
    关键API:dmidecode -t memory
    :return:
    """
    # 获得未处理的信息
    raw_data = subprocess.Popen('sudo dmidecode -t memory', stdout=subprocess.PIPE, shell=True)
    # 初步处理，将获得到的数据按照\n结尾切割组成列表
    raw_list = raw_data.stdout.read().decode().split('\n')
    raw_ram_list = []  # 最终会获得一个二元列表，每个列表包含每条Memory Device 信息项的所有行，Memory Device 所在行除外。
    item_list = []  # 该列表临时存储每条Memory Device信息项但不包含Memory Device所在行的临时列表
    for line in raw_list:
        if line.startswith('Memory Device'):
            raw_ram_list.append(item_list)
            item_list = []
        else:
            item_list.append(line.strip())
    ram_list = []
    for item in raw_ram_list:
        item_ram_size = 0
        ram_item_to_dic = {}
        for i in item:
            data = i.split(':')
            if len(data) == 2:
                key, v = data
                if key == 'Size':
                    if v.strip() != 'No Module Installed':
                        ram_item_to_dic['capacity'] = v.split()[0].strip()
                        item_ram_size = v.strip().split()[0]
                    else:
                        ram_item_to_dic['capacity'] = ''
                if key == 'Type':
                    ram_item_to_dic['model'] = v.strip()
                if key == 'Manufacturer':
                    ram_item_to_dic['manufacturer'] = v.strip()
                if key == 'Serial Number':
                    ram_item_to_dic['sn'] = v.strip()
                if key == 'Asset Tag':
                    ram_item_to_dic['asset_tag'] = v.strip()
                if key == 'Locator':
                    ram_item_to_dic['slot'] = v.strip()
        if item_ram_size == 0:
            pass
        else:
            ram_list.append(ram_item_to_dic)

    raw_total_size = subprocess.Popen('cat /proc/meminfo|grep MemTotal', stdout=subprocess.PIPE, shell=True)
    raw_total_size = raw_total_size.stdout.read().decode().split(':')
    ram_data = {'ram': ram_list}
    if len(raw_total_size) == 2:
        total_gb_size = int(raw_total_size[1].split()[0]) / 1024 ** 2
        ram_data['ram_size'] = total_gb_size
    return ram_data


def get_nic_info():
    """
    获得网卡信息
    :return:
    """
    raw_data = subprocess.Popen('ifconfig -a ', shell=True, stdout=subprocess.PIPE)
    raw_data = raw_data.stdout.read().decode().split('\n')
    nic_dic = dict()
    next_ip_line = False
    last_mac_addr = None
    for line in raw_data:
        if next_ip_line:
            next_ip_line = False
            nic_name = last_mac_addr.split()[0]
            mac_addr = last_mac_addr.split('HWaddr')[1].strip()
            raw_ip_addr = line.split('inet addr:')
            raw_bcast = line.split('Bcast:')
            raw_netmask = line.split('Mask')
            if len(raw_ip_addr) > 1:
                ip_addr = raw_ip_addr[1].split()[0]
                network = raw_bcast[1].split()[0]
                netmask = raw_netmask[1].split()[0]
            else:
                ip_addr, network, netmask = None, None, None
            if mac_addr not in nic_dic:
                nic_dic[mac_addr] = {
                    'name': nic_name,
                    'mac': mac_addr,
                    'net_mask': netmask,
                    'network': network,
                    'bonding': 0,
                    'model': 'unknown',
                    'ip_address': ip_addr,
                }
            else:
                if '{}_bonding_addr'.format(mac_addr) not in nic_dic:
                    random_mac_addr = '{}_bonding_addr'.format(mac_addr)
                else:
                    random_mac_addr = '{}_bonding_addr2'.format(mac_addr)
                nic_dic[random_mac_addr] = {'name': nic_name,
                                            'mac': random_mac_addr,
                                            'net_mask': netmask,
                                            'network': network,
                                            'bonding': 1,
                                            'model': 'unknown',
                                            'ip_address': ip_addr,
                                            }

        if 'HWaddr' in line:
            next_ip_line = True
            last_mac_addr = line
    nic_list = []
    for k, v in nic_dic.items():
        nic_list.append(v)
    return {'nic': nic_list}


def get_disk_info():
    """
    获得磁盘信息
    linux:hdparm显示与设定硬盘的参数
    :return: 
    """
    raw_data = subprocess.Popen('sudo hdparm -i /dev/sda |grep Model', stdout=subprocess.PIPE, shell=True)
    raw_data = raw_data.stdout.read().decode()
    data_list = raw_data.split(',')
    model = data_list[0].split('=')
    model = model if len(model) > 1 else None
    try:
        sn = data_list[2].split('=')[1].strip()
    except IndexError:
        sn = ''
    data_size = subprocess.Popen('sudo fdisk -l /dev/sda | grep Disk|head -1', stdout=subprocess.PIPE, shell=True)
    data_size = data_size.stdout.read().decode().split("sda: ")[1].split()[0]

    result = {'physical_disk_driver': []}

    disk_dict = dict()
    disk_dict['model'] = model
    disk_dict['sn'] = sn
    disk_dict['size'] = data_size
    result['physical_disk_driver'].append(disk_dict)
    return result


if __name__ == '__main__':
    """Linux平台系统信息收集测试"""
    data = collect()
    from pprint import pprint

    pprint(data)
