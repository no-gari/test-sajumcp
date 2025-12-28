# utils/time_utils.py

GAN_10 = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
JI_12 = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

def get_si_ji_by_clock(hour, minute):
    total_min = hour * 60 + minute
    ranges = [((1410, 1439), '子'), ((0, 89), '子'), ((90, 209), '丑'), ((210, 329), '寅'),
              ((330, 449), '卯'), ((450, 569), '辰'), ((570, 689), '巳'), ((690, 809), '午'),
              ((810, 929), '未'), ((930, 1049), '申'), ((1050, 1169), '酉'), ((1170, 1289), '戌'),
              ((1290, 1409), '亥')]
    for (start, end), branch in ranges:
        if start <= total_min <= end:
            return branch
    return '?'

def get_hour_gan(day_gan, hour_ji):
    return GAN_10[(GAN_10.index(day_gan) * 2 + JI_12.index(hour_ji)) % 10]
