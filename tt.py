import os

s = [-1, -3, -5, 3, 6]
# s = list(map(lambda x: abs(x) < 3, s))
print(s)


# print("---")
# print("all:", all(type(i) == int for i in s))
# print("any:", any(type(i) != float for i in s))


def check_all_values_type(data: any, value_type: type):
    """Check if all values are the same type"""

    return all(type(_) == value_type for _ in data)


def check_all_values_expression(data: any, expression):
    """Check if all values are satisfy expression
    actually it boolshit function

    some_num = 7

    def func(arg):
        if arg < some_num:
            return True
        else:
            return False
    """

    return all(list(map(lambda x: expression(x), data)))


def binary_represeentation(data):
    """
    Converts numbers into binary representation (same as bin() but without 0b)

    :param data: str() / int()
    :return: binary (00001010)
    """
    integer_number = data
    integer_number = int(integer_number)
    result = ''
    for x in range(8):
        r = integer_number % 2
        integer_number = integer_number//2
        result += str(r)
    result = result[::-1]

    return result


chislo = 7


def func(arg):
    if arg < chislo:
        return True
    else:
        return False


print(check_all_values_type(data=s, value_type=int))
print(check_all_values_expression(data=s, expression=func))
print(binary_represeentation(10))


"""ЗАДАЧИ"""
london = {'name': 'London1', 'location': 'London Str', 'vendor': 'Cisco'}
keys = london.keys()
print(keys)
london['ip'] = '10.1.1.1'
print(id(keys))


dd = dict.fromkeys(london)
print(dd)
dd["name"] = 55
for i in dd.values():
    print(id(i))

a = tuple([1,2,3,4,4,4,4,4])

print(a)
c = list(a)
print(c)
b = set(a)
print(b)
gg = " "

print(bool( None))
print("-----")
ss = "gfgf660-"

print(ss.isalnum())


london_co = {
    'r1': {
        'location': '21 New Globe Walk',
        'vendor': 'Cisco',
        'model': '4451',
        'ios': '15.4',
        'ip': '10.255.0.1'
    },
    'r2': {
        'location': '21 New Globe Walk',
        'vendor': 'Cisco',
        'model': '4451',
        'ios': '15.4',
        'ip': '10.255.0.2'
    },
    'sw1': {
        'location': '21 New Globe Walk', 'vendor': 'Cisco',
        'model': '3850',
        'ios': '3.6.XE',
        'ip': '10.255.0.101',
        'vlans': '10,20,30',
        'routing': True
    }
}

# user_input1 = str(input("Введите имя устройства: ")).lower()
# user_input2 = str(input(f"Введите имя параметра: "
#                         f"{tuple(london_co.get(user_input1, 'Такого устройства нет'))}: ")).lower()
#
# print(london_co.get(user_input1).get(user_input2, "Такого параметра нет"))


tip1 = """
IP: 10.1.1.195/28
              mask ->   (net IP  + 0000) 
┌---------------┴----------------┐┌-┴-┐
0000 1010 0000 0001 0000 0001 1100 0011

             net IP
┌---------------┴----------------┐┌---┐
0000 1010 0000 0001 0000 0001 1100 0000

bin_mask = "1" * mask + "0" * (32 - mask)

Подсказка:
Есть адрес хоста в двоичном формате и маска сети 28. Адрес сети это первые 28 бит
адреса хоста + 4 ноля.
То есть, например, адрес хоста 10.1.1.195/28 в двоичном формате будет
bin_ip = "00001010000000010000000111000011"

А адрес сети будет первых 28 символов из bin_ip + 0000 (4 потому что всего
в адресе может быть 32 бита, а 32 - 28 = 4)
00001010000000010000000111000000

"""

network = input("Ведите адрес сети: ")

ip, mask = network.split("/")
mask = int(mask)

oct1, oct2, oct3, oct4 = list(map(lambda x: int(x), ip.split(".")))
bin_ip_str = "{:08b}{:08b}{:08b}{:08b}".format(oct1, oct2, oct3, oct4)
# 00001010 00000001 00000001 11000000
bin_mask = "1" * mask + "0" * (32 - mask)
# 00001010 00000001 00000001 11000011
bin_ip_str = "{:08b}{:08b}{:08b}{:08b}".format(oct1, oct2, oct3, oct4)

bin_network_str = bin_ip_str[:mask] + "0" * (32 - mask)

ip_output = f"""
Network:
{oct1:<8} {oct2:<8} {oct3:<8} {oct4:<8}
{oct1:08b} {oct2:08b} {oct3:08b} {oct4:08b}"""

mask_output = f"""
Mask:
/{mask}
{int(bin_mask[0:8], 2):<8} {int(bin_mask[8:16], 2):<8} {int(bin_mask[16:24], 2):<8} {int(bin_mask[24:32], 2):<8}
{int(bin_mask[0:8], 2):08b} {int(bin_mask[8:16], 2):08b} {int(bin_mask[16:24], 2):08b} {int(bin_mask[24:32], 2):08b}"""


host_network_output = f"""
Host Network:
{int(bin_network_str[0:8], 2):<8} {int(bin_network_str[8:16], 2):<8} {int(bin_network_str[16:24], 2):<8} {int(bin_network_str[24:32], 2):<8}
{int(bin_network_str[0:8], 2):08b} {int(bin_network_str[8:16], 2):08b} {int(bin_network_str[16:24], 2):08b} {int(bin_network_str[24:32], 2):08b}

Host Mask:
/{mask}
{int(bin_mask[0:8], 2):<8} {int(bin_mask[8:16], 2):<8} {int(bin_mask[16:24], 2):<8} {int(bin_mask[24:32], 2):<8}
{int(bin_mask[0:8], 2):08b} {int(bin_mask[8:16], 2):08b} {int(bin_mask[16:24], 2):08b} {int(bin_mask[24:32], 2):08b}"""

print(ip_output)
print(mask_output)
print(host_network_output)

int("11111111", 2)
