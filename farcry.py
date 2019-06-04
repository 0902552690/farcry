#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
from re import findall
import csv

def read_log_file(log_file_pathname):
    with open(log_file_pathname, 'r') as file:
        log_data = file.read()
    return log_data


def find_all_cvar(log_data):
    cvar_dic = {}
    for line in log_data.splitlines():
        if "Lua cvar" in line:
            key_value = line.split("(")[1][:-1].split(",")
            cvar_dic[key_value[0]] = key_value[1]
    return cvar_dic


def parse_log_start_time(log_data):
    start_time = log_data.splitlines()[0][15:].split(' ',1)
    # log_start_time = datetime.strptime(start_time, "%B %d, %Y %H:%M:%S")
    start_time = log_data.splitlines()[0][15:].split(' ',1)[1].split(' ')
    month_dic = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5,
                 'June':6, 'July':7, 'August':8, 'September':9, 'October':10,
                 'November':11, 'December':12}
    year = int(start_time[2])
    for month in month_dic:
        if start_time[0] == month:
            month = month_dic[month]
            break
    day = int(start_time[1][:-1])
    hour = int(start_time[3].split(":")[0])
    minute = int(start_time[3].split(":")[1])
    second = int(start_time[3].split(":")[2])
    log_start_time = datetime(year, month, day, hour, minute, second,
                              tzinfo=timezone(timedelta(hours=-5)))
    return log_start_time


def parse_match_map_name_and_game_mode(log_data):
    for line in log_data.splitlines():
        if "Loading level" in line:
            map_and_mode = line[8:-1].rstrip('-').lstrip('-').split()
            resu_tuple = (map_and_mode[4], map_and_mode[2].split("/")[1][:-1])

    return resu_tuple


def parse_frags(log_data, log_start_time):
    year = log_start_time.year
    month = log_start_time.month
    day = log_start_time.day
    hour = log_start_time.hour
    frags_list = []
    tmp_minute = 0
    for line in log_data.splitlines():
        if "killed" in line:
            frag_data = line.split(" ", 2)
            event = frag_data[2]
            frag_time  = datetime(year, month, day, hour,
                                  int(frag_data[0][1:6].split(":")[0]),
                                  int(frag_data[0][1:6].split(":")[1]),
                                  tzinfo=timezone(timedelta(hours=-5)))
            if line.endswith('itself'):
                killer_name = event.split("killed")[0]
                frags_list.append((frag_time, killer_name))
            else:
                killer_name = event.split("killed")[0]
                victim_name = event.split("killed")[1].split("with")[0][1:]
                weapon_code = event.split("killed")[1].split("with")[1][1:]
                cur_minute = int(frag_data[0][1:6].split(":")[0])
                if cur_minute < tmp_minute:
                    hour += 1
                    if hour == 24:
                        day += 1
                        hour == 0
                tmp_minute = cur_minute
                frags_list.append((frag_time, killer_name, victim_name,
                                   weapon_code))
    return frags_list


def prettify_frags(frags):
    prettified_frags = []
    emoji_dic = {'Vehicle':'🚙','Falcon':'🔫', 'Shotgun':'🔫', 'P90':'🔫',
                 'MP5':'🔫', 'M4':'🔫', 'AG36':'🔫', 'OICW':'🔫',
                 'SniperRifle':'🔫', 'M249':'🔫', 'MG':'🔫',
                 'VehicleMountedAutoMG':'🔫', 'VehicleMountedMG':'🔫',
                 'AG36Grenade':'💣', 'HandGrenade':'💣', 'OICWGrenade':'💣',
                 'StickyExplosive':'💣', 'Rocket':'🚀',
                 'VehicleMountedRocketMG':'🚀', 'VehicleRocket':'🚀',
                 'Machete':'🔪',
                 'Boat':'🚤'}
    killer_icon = '😛'
    victim_icon = '😦'
    suicide_icon = '☠️'
    for frag in frags:
        if len(frag) == 2:
            frag_time = '[' + frag[0].isoformat() + ']'
            append_str = frag_time + ' 😦 '+ frag[1] + ' ☠️'
            prettified_frags.append(append_str)
        else:
            weapon_icon = emoji_dic[frag[-1]]
            frag_time = '[' + frag[0].isoformat() + ']'
            append_str = frag_time + ' 😛 ' + frag[1] + ' ' + weapon_icon +\
                            ' 😦 '+ frag[2]
            prettified_frags.append(append_str)
    return prettified_frags


def parse_match_start_and_end_times(log_data, frags):
    # year = frags[0][0].year
    # month = frags[0][0].day
    # tzinfo = frags[0][0].tzinfo
    for line in log_data.splitlines():
        if 'loaded in' in line:
            start_time = frags[0][0]
            start_time = start_time.replace(minute = int(line[1:3]),
                                            second = int(line[4:6]))
        elif 'Statistics' in line:
            end_time = frags[-1][0]
            end_time = start_time.replace(minute = int(line[1:3]),
                                            second = int(line[4:6]))
        elif '_ERRORMESSAGE' in line:
            end_time = frags[-1][0]
            end_time = start_time.replace(minute = int(line[1:3]),
                                            second = int(line[4:6]))
            break
    return start_time, end_time

def write_frag_csv_file(log_file_pathname, frags):
    with open(log_file_pathname, 'w+') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for frag in frags:
            writer.writerow(frag)
    return csvfile
log_data = read_log_file('./logs/log00.txt')
cvar_dic = find_all_cvar(log_data)
log_start_time = parse_log_start_time(log_data)
parse_match_map_name_and_game_mode(log_data)
frags = parse_frags(log_data, log_start_time)
prettified_frags = prettify_frags(frags)
start_time, end_time = parse_match_start_and_end_times(log_data, frags)
write_frag_csv_file('./logs/log00.csv', frags)
