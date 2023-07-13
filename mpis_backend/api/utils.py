def get_majimbo(data_serializer):
    majimbo = ''
    for data in data_serializer:
        jimbo = list(data.values())
        majimbo += f'{jimbo[1]}.{jimbo[0]}\n'
    return majimbo


def get_sekta(data_serializer):
    sektas = ''
    for data in data_serializer:
        sekta = list(data.values())
        sektas += f'{sekta[1]}.{sekta[0]}\n'
    return sektas