import ipaddress

def split_into_24_subnets(network):
    try:
        # Парсим исходную сеть
        original_network = ipaddress.ip_network(network, strict=False)

        # Проверяем, что маска не больше /24 (иначе разбивать не нужно)
        if original_network.prefixlen > 24:
            print("Ошибка: Исходная маска должна быть /24 или меньше.")
            return []

        # Разбиваем на подсети /24
        subnets_24 = list(original_network.subnets(new_prefix=24))

        return subnets_24

    except ValueError as e:
        print(f"Ошибка: {e}")
        return []

# Пример использования
if __name__ == "__main__":
    input_network = input("Введите IP-адрес и маску (например, 152.118.0.0/16): ").strip()
    subnets = split_into_24_subnets(input_network)

    if subnets:
        print(f"\nРазбиение сети {input_network} на подсети /24:")
        for subnet in subnets:
            print(subnet)
    else:
        print("Не удалось разбить сеть.")
