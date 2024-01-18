class Drink:
    # Значение статического атрибута
    _volume = 200

    # Создаем метод (private) для инициализации объекта
    def __init__(self, name, price):
        # Присваиваем значения динамическим атрибутам
        self.name = name
        self.price = price
        # Устанавливаем начальное значение атрибута remains (сколько миллилитров осталось)
        self._remains = self._volume

    # Запрашиваем информацию о напитке
    def drink_info(self):
        print(
            f"Название: {self.name}. Стоимость: {self.price}. Объем: {self._volume}. Осталось: {self._remains}"
        )

    # Служебный метод (protected), чтобы узнать, достаточно ли напитка.
    def _is_enough(self, need):
        if self._remains >= need and self._remains > 0:
            return True
        print("Осталось недостаточно напитка")
        return False

    # Метод, чтобы сказать другу сделать глоток.
    def sip(self):
        if self._is_enough(20) == True:
            self._remains -= 20
            print("Друг сделал глоток")

    # Говорим другу сделать маленький глоток.
    def small_sip(self):
        if self._is_enough(10) == True:
            self._remains -= 10
            print("Друг сделал маленький глоток")

    # Говорим другу выпить напиток залпом.
    def drink_all(self):
        if self._is_enough(0) == True:
            self._remains = 0
            print("Друг выпил напиток залпом")

    def tell_price(self):
        print(f"Друг объявляет стоимость своего напитка")
        return self.price


class Juice(Drink):
    # Создаём статический атрибут, который будет содержать название нашего напитка.
    _juice_name = "сок"

    # Вызываем инициализатор класса и указываем в нём только те аргументы, которые запрашиваем при создании объекта.
    def __init__(self, price, taste):
        # Передаём конструктору родительского класса значение атрибута __juice_name.
        super().__init__(self._juice_name, price)
        # Определяем значение нового динамического атрибута taste.
        self.taste = taste

    def drink_info(self):  # Полиморфизм
        print(
            f"Вкус сока: {self.taste}. Стоимость: {self.price}. Объем: {self._volume}. Осталось: {self._remains}"
        )


# Создаём экземпляр класса Juice.
apple_juice = Juice(250, "яблочный")
# Пробуем вызвать методы, прописанные в родительском классе Drink.
apple_juice.small_sip()
apple_juice.sip()
apple_juice.drink_info()

tea = Drink("чай", 500)
print(tea.tell_price())  # Сначала друг объявит стоимость чая.
beetlejuice = Juice(1988, "жучиный")
print(beetlejuice.tell_price())

# Создаем экземпляр
coffee = Drink("Кофе", 300)
# coffee._remains = 10  # Приравниваем остаток кофе к 10 мл. Игнорировать уровни доступа можно, НО не надо.
coffee.sip()  # Пытаемся сделать обычный глоток.
coffee.drink_info()  # Узнаём информацию о напитке.
