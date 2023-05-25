
import os
import re

old_set_dict = {}

# Цель работ перенести стык с вышестоящим оборудованием на другой узел,
# для этого необходимо изменить конфигурацию на atn (узел huawei) и создать новый канал на agg(узел huawei)

# Предварительно собрал актуальную конфигурацию потов и сохранил её в log_file.txt
# Читаю файл построчно и сохраняю необходимые параметры в old_set_dict

with open('log_file.txt', 'r') as log_file:
    for i_str in log_file:
        if re.search(r'\*{7}\sIP:.*', i_str) != None:
            in_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', i_str)
            ip_address = in_list[0]
        elif re.search(r'interface\s.*', i_str) != None:
            interface = i_str.split(' ')[1][:-1]
            old_set_dict[(ip_address, interface)] = ''
        elif re.search(r'mpls l2vc\s.*', i_str) != None:
            if len(old_set_dict[(ip_address, interface)]) == 0:
                old_set_dict[(ip_address, interface)] = f'\tun{i_str}'
            else:
                second_str = f'\tun{i_str}{old_set_dict[ip_address, interface]}'
                old_set_dict[(ip_address, interface)] = second_str
        elif re.search(r'commit', i_str) != None:
            ip_address = None
            interface = None
            second_str = None

#Формирую новые параметры
# номер PW

def pw_create(vlan, agg_num):
    # 61 3061 71 1
    # 1 - 4294967295
    pw = f'93{vlan}{14 if agg_num == 1 else 15}0'
    if pw.isdigit():
        if 1 < int(pw) < 4294967295:
            return pw
    else:
        print('Ошибка при формировании PW')
        return None

# описание к этому номеру PW


def pw_desc(atn_name, atn_int):
    atn = re.findall(r'[Aa]tn\d*\b', atn_name)[0]
    position_num = re.findall(r'\b\d{2,6}\b', atn_name)[0] if re.search(
        r'\b\d{2,6}\b', atn_name) != None else '_'
    port = re.sub(r'/', '', re.findall(r'\d*/\d*/\d*', atn_int)[0])
    return f'{atn}_{position_num}_{port}'

#Формирую конфигурацию для agg

def for_agg(vsi_name, atn_ip, atn_int, vlan, atn_name, agg_num):
    pw = pw_create(vlan, agg_num)

    result = f'vsi {vsi_name}\n pwsignal ldp\n'
    result += f'  peer {atn_ip} negotiation-vc-id {pw} tnl-policy atn_policy upe ignore-standby-state\n'
    result += f'  peer {atn_ip} negotiation-vc-id {pw} pw {pw_desc(atn_name, atn_int)}\n'
    result += f'  peer  10.0.0.15\n' if agg_num == 1 else f'  peer  10.0.0.14\n'

    return result, pw

#Формирую конфигурацию для atn

def for_atn(atn_ip, atn_int, pw_1, pw_2):
    int_re_conf = f'  int {atn_int}\n'
    # int_re_conf = ''
    int_re_conf += old_set_dict.get((atn_ip, atn_int))
    if re.search(r'\.\d*', atn_int) is None:
        int_re_conf += f'\tmpls l2vc  10.0.0.15 pw-template PW {pw_2} tagged ignore-standby-state\n'
        int_re_conf += f'\tmpls l2vc  10.0.0.14 pw-template PW {pw_1} tagged secondary\n'
        int_re_conf += f'\tmpls l2vpn redundancy master\n\tmpls l2vpn reroute delay 90\n'
    else:
        int_re_conf += f'\tmpls l2vc  10.0.0.15 pw-template PW {pw_2} ignore-standby-state\n'
        int_re_conf += f'\tmpls l2vc  10.0.0.14 pw-template PW {pw_1} secondary\n'
        int_re_conf += f'\tmpls l2vpn redundancy master\n\tmpls l2vpn reroute delay 90\n'
    return int_re_conf

vsi_agg_1 = []
vsi_agg_2 = []
atn_conf_dict = {}

# Помимо старых данных нужны и новые, считываю данные их vsi_data.txt
# и формирую новые конфиги, результат сохраняю в agg1_Sochi.txt, agg2_Sochi.txt
# и atn_Sochi.txt

with open('vsi_data.txt', 'r') as vsi_data:
    agg_1_file = open('agg1_Sochi.txt', 'w')
    agg_2_file = open('agg2_Sochi.txt', 'w')

    for i_vsi in vsi_data:
        client_info = i_vsi[:-1].split('\t')
        # vsi_name = client_info[0]
        # atn_ip = client_info[1]
        # atn_int = client_info[2]
        # vlan = client_info[3]
        # atn_name = client_info[4]

        for_agg_1, pw_1 = for_agg(client_info[0], client_info[1], client_info[2], client_info[3], client_info[4], 1)
        for_agg_2, pw_2 = for_agg(client_info[0], client_info[1], client_info[2], client_info[3], client_info[4], 2)

        agg_1_file.write(for_agg_1)
        agg_2_file.write(for_agg_2)

        if pw_1 is None or pw_2 is None:
            break

        atn_int_conf = for_atn(client_info[1], client_info[2], pw_1, pw_2)

        if atn_conf_dict.get(client_info[1]) is None:
            atn_conf_dict[client_info[1]] = [atn_int_conf]
        else:
            atn_conf_dict[client_info[1]].append(atn_int_conf)
    else:
        agg_1_file.close()
        agg_2_file.close()

        with open('atn_Sochi.txt', 'w') as atn_Sochi:
            for i_key, value in atn_conf_dict.items():
                atn_Sochi.write(f'{i_key}\n')
                for in_value in value:
                    atn_Sochi.write(in_value)
                atn_Sochi.write(f'\treturn\nY\nsave\nY\n')

