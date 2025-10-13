# discriminant.py

def calculate_discriminant(a, b, c):
    """
    Функция для вычисления дискриминанта квадратного уравнения.
    Формула: D = b^2 - 4ac
    """
    discriminant = b**2 - 4 * a * c
    return discriminant


if __name__ == "__main__":
    # Пример использования
    a = float(input("Введите коэффициент a: "))
    b = float(input("Введите коэффициент b: "))
    c = float(input("Введите коэффициент c: "))

    D = calculate_discriminant(a, b, c)
    print(f"Дискриминант: {D}")
