import sqlite3
import datetime
import requests
base = sqlite3.connect("base.db")
cur = base.cursor()
base.execute('CREATE TABLE IF NOT EXISTS users(username text PRIMARY KEY, password text, balance INT)')
base.execute('CREATE TABLE IF NOT EXISTS banknotes(nominal INT PRIMARY KEY, quantity INT)')
base.commit()
global str_name_transactions


class Person(object):
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def set_pass(self, old_pass, new_pass):
        if old_pass == self.password:
            self.password = new_pass


class User(Person):
    def __init__(self, login, password, balance):
        super().__init__(login, password)
        self.balance = balance

    def up_balance(self, login, password):
        sum_to_put = input("Введіть сумму, на яку хочете поповнити картку: ")
        if sum_to_put.isdigit():
            sum_to_put = int(sum_to_put)
            try: self.balance = self.balance[0] + sum_to_put
            except: self.balance = self.balance + sum_to_put
            cur.execute('UPDATE users SET balance = ? WHERE username = ?', (self.balance, login))
            base.commit()
            print("Поповненя успішне")
            start_menu(login, password, self.balance)
        else:
            print("Введіть будь-ласка додатнє число")
            self.up_balance(login, password)

    def down_balance(self, login, password):
        sum_to_get = input("Введіть сумму, яку хочете перевести: ")
        num_users_to_give_money = input("Введіть номер телефона користувача, кому хочете перевести кошти: ")
        if sum_to_get.isdigit():
            sum_to_get = int(sum_to_get)
        try:
            if sum_to_get <= self.balance[0]:
                self.balance = self.balance[0] - sum_to_get
                cur.execute('UPDATE users SET balance = ? WHERE username = ?', (self.balance, login))
                base.commit()
                print("Перевод успішний")
                start_menu(login, password, self.balance)
            else:
                print("Недостатньо коштів")
                self.down_balance(login, password)
        except:
            if sum_to_get <= self.balance:
                self.balance = self.balance - sum_to_get
                cur.execute('UPDATE users SET balance = ? WHERE username = ?', (self.balance, login))
                base.commit()
                print("Перевод успішний")
                start_menu(login, password, self.balance)
            else:
                print("Недостатньо коштів")
                self.down_balance(login, password)

        else:
            print("Введіть будь-ласка додатнє число")
            self.down_balance(login)

    def look_balance(self, login, password):
        try:
            print(self.balance[0])
        except:
            print(self.balance)
        start_menu(login, password, self.balance)


class Incasator(Person):
    def __init__(self, login, password):
        super().__init__(login, password)

    @staticmethod
    def look_valutes():
        banknotes_dict = {}
        tmp = cur.execute('SELECT * FROM banknotes')
        for i in tmp:
            temp_dict = {i[0]: i[1]}
            banknotes_dict.update(temp_dict)
        banknotes_list = [10, 20, 50, 100, 200, 500, 1000]
        for i in banknotes_list:
            print(str(i) + " - " + str(banknotes_dict[i]))
        login_menu()

    @staticmethod
    def set_valutes():
        banknotes_list = ["10", "20", "50", "100", "200", "500", "1000"]
        nominal = input("Введіть номінал купюру, кількість якої треба змінити: ")
        quantity = input("Введіть потрібну кількість: ")
        if quantity.isdigit():
            quantity = int(quantity)
            if quantity < 0:
                print("Неправильна кількість:")
                Incasator.set_valutes()
        else:
            print("Введіть будь-ласка число!")
            Incasator.set_valutes()

        if nominal not in banknotes_list:
            print(nominal)
            print("Такого номіналу не існує")
            Incasator.set_valutes()

        cur.execute('UPDATE banknotes SET quantity = ? WHERE nominal = ?', (quantity, nominal))
        base.commit()

        do = input("Якщо бажаєте ще внести зміни, натисніть '1': ")

        if do == "1":
            Incasator.set_valutes()
        else:
            raise SystemExit


class EntranceMenu(object):
    def __init__(self, login = "None", password = "None"):
        self.login = login
        self.password = password

    @staticmethod
    def new_user(login, password):
        cur.execute('INSERT INTO users VALUES(?, ?, ?)', (login, password, 0))
        base.commit()


def login_menu():
    user_name = input("Введіть Ваш логін: ")
    user_pass = input("Введіть ваш пароль: ")
    if user_name == "admin" and user_pass == "admin":
        print("")
        print("Выберіть дію\n1. Переглянути наявні купюри\n2. Змінити кількість купюр")
        num = input("Ваш вибір: ")
        if num.isdigit() is False:
            print("Невірне значення")
            login_menu()
        num = int(num)
        if num == 1:
            Incasator.look_valutes()
            login_menu()
        if num == 2:
            Incasator.set_valutes()
    else:
        entrance_flag = False
        pass_from_sql = cur.execute('SELECT password FROM users WHERE username == ?', (user_name,)).fetchone()
        balance = cur.execute('SELECT balance FROM users WHERE username == ?', (user_name,)).fetchone()
        try:
            pass_from_sql = pass_from_sql[0]
        except TypeError:
            pass

        if pass_from_sql == user_pass:
            entrance_flag = True
            print("Вітаємо {}".format(user_name))
            start_menu(user_name, user_pass, balance)

        if entrance_flag is False:
            print(
                "Перевірте логін та пароль\nАбо якщо бажаєто зареєструватись, натисніть '1', інакше будь-який символ\n")
            num = input("Ваш вибір: \n")
            if num == "1":
                username = input("Введіть Ваше ім'я: ")
                password = input("Введіть Ваш пароль: ")
                EntranceMenu.new_user(username, password)
                login_menu()
            else:
                login_menu()


class Curses(object):

    @staticmethod
    def convert_valute():
        link_rate_now = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
        page = requests.get(link_rate_now)
        rate = page.json()
        print("Список валют: USD, EUR, RUR, BTC на сьогодні\n")
        valute = input("Введіть будь-ласка валюту, яку потрібно конвертувати: ")
        sum_to_convert = input("Введіть сумму у валюті, яку треба конвертувати: ")
        valute_end = input("Введіть будь-ласка валюту, у яку треба конвертувати: ")
        if not sum_to_convert.isdigit():
            sum_to_convert = 0
            print("Введіть коретну сумму")
            Curses.convert_valute()


        check = False
        print("Ваша сумма: {} {}\n".format(sum_to_convert, valute))
        #global sum_uah
        for i in rate:
            if i['ccy'] == valute:
                sum_uah = float(i['sale']) * int(sum_to_convert)
                check = True
        if valute == "BTC":
            for i in rate:
                if i['ccy'] == "USD":
                    sum_uah = sum_uah * float(i['sale'])

        if check is not True:
            print("Нажаль такої валюти немає")
            return

        if valute_end == "BTC":
            for i in rate:
                if i['ccy'] == "USD":
                    sum_uah = sum_uah / float(i['sale'])

        for i in rate:
            if i['ccy'] == valute_end:
                res = sum_uah / float(i['sale'])
                print(sum_to_convert + " " + valute + " = " + str(float(res)) + " " + valute_end)

    @staticmethod
    def rate_today():
        link_rate_now = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
        page = requests.get(link_rate_now)
        rate = page.json()
        print("Список валют: USD, UER, RUR, BTC\n")
        valute = input("Введіть будь-ласка потрібну валюту: ")

        check = False
        for i in rate:
            if i['ccy'] == valute:
                print("Купівля: " + str(i['buy']))
                print("Продаж: " + str(i['sale']))
                check = True

        if check is not True:
            print("Нажаль такої валюти немає")
            Curses.rate_today()

    @staticmethod
    def print_rate(year_start=0, month_start=0, day_start=0):
        now = datetime.datetime.now()
        year_today = int(now.year)
        month_today = int(now.month)
        day_today = int(now.day)
        if year_start == 0:
            year_start, month_start, day_start = Curses.check_date()
        old_buy, old_sale = 0, 0
        my_list = Curses.create_list_of_dates(day_start, month_start, year_start, day_today, month_today, year_today)
        try:
            i = my_list[0]
        except:
            return

        i = i[2] + "." + i[1] + "." + i[0]
        print(i)
        link_rate = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}".format(i)
        page = requests.get(link_rate)
        rate = page.json()
        rate = rate["exchangeRate"]
        str_of_valutes = ""
        for i in rate:
            try:
                str_of_valutes += str(i["currency"])
                str_of_valutes += " "
            except:
                pass
        print(str_of_valutes)
        valute = input("Введіть потрібну валюту: ")
        today_check = False
        try:
            for i in my_list:
                i = i[2] + "." + i[1] + "." + i[0]
                link_rate = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}".format(i)
                page = requests.get(link_rate)
                rate = page.json()
                check = False
                for r in rate["exchangeRate"]:
                    if 'currency' in r.keys() and r['currency'] == valute:
                        if old_buy != 0 and old_sale != 0:
                            difference_buy = old_buy - r['purchaseRateNB']
                            difference_sale = old_sale - r['saleRateNB']
                            print(i)
                            print("Купівля: " + str(r['purchaseRateNB']) + "    " + str(difference_buy))
                            print("Продаж: " + str(r['saleRateNB']) + "    " + str(difference_sale))
                            old_buy = r['purchaseRateNB']
                            old_sale = r['saleRateNB']
                        else:
                            print(i)
                            print("Купівля: " + str(r['purchaseRateNB']))
                            print("Продаж: " + str(r['saleRateNB']))
                            old_buy = r['purchaseRateNB']
                            old_sale = r['saleRateNB']
                        check = True

                if check is not True:
                    print("Нажаль такої валюти немає, зачекайте 10 секунд\n")

                    Curses.print_rate(year_start, month_start, day_start)

            link_rate_now = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
            page = requests.get(link_rate_now)
            rate = page.json()
            for i in rate:
                if i['ccy'] == valute:
                    difference_buy = old_buy - float(i['buy'])
                    difference_sale = old_sale - float(i['sale'])
                    print("Сьгодні")
                    print("Купівля: " + str(i['buy']) + "   " + str(difference_buy))
                    print("Продаж: " + str(i['sale']) + "   " + str(difference_sale))
                    today_check = True

            if 'ccy' not in rate.keys():
                print("Сталася помилка, курсу цієї валюти на цю дату немає")
        except:
            if today_check:
                pass
            else:
                print("Якщо ви бажаєте подивитися курс на сьогодні, перейдіть у відповідний пункт меню")

    @staticmethod
    def check_date():
        global date
        date_now = datetime.date.today()
        year_today = int(str(date_now)[0:4])
        month_today = int(str(date_now)[5:7])
        day_today = int(str(date_now)[8:10])
        date = input("Ваша дата у форматі yyyy-mm-dd: ")
        if not date[0:4].isdigit() or not date[5:7].isdigit() or not date[8:10].isdigit():
            print("Невірна дата \n")
            Curses.check_date()
        if len(date) > 10:
            print("Невірна дата \n")
            Curses.check_date()
        year_start = int(str(date)[0:4])
        month_start = int(str(date)[5:7])
        day_start = int(str(date)[8:10])
        if year_start < year_today - 4:
            print("В цьому році неможливо знайти курс\n")
            Curses.check_date()
        if month_start > 12 or month_start < 1:
            print("Такого місяці не існує\n")
            Curses.check_date()
        if day_start > 31 or day_start < 1:
            print("У місяці не існує такого дня\n")
            Curses.check_date()
        if month_start == 2 and year_start % 4 == 0 and year_start % 400 != 0 and day_start > 29:
            print("В цьому році у лютому 29 днів\n")
            Curses.check_date()
        if month_start == 2 and year_start % 4 != 0 and day_start > 28:
            print("В цьому році у лютому 28 днів\n")
            Curses.check_date()
        if month_start in [4, 6, 9, 11] and day_start > 30:
            print("Некоректна дата, у цьомі місяці лише 30 днів\n")
            Curses.check_date()
        if year_start > year_today:
            print("Нажаль ми не навчилися знаходити курс у майбутньому\n")
            Curses.check_date()
        if year_start == year_today and month_start > month_today:
            print("Нажаль ми не навчилися знаходити курс у майбутньому\n")
            Curses.check_date()
        if year_start == year_today and month_start == month_today and day_start > day_today:
            print("Нажаль ми не навчилися знаходити курс у майбутньому\n")
            Curses.check_date()
        if year_start == year_today and month_start == month_today and day_start == day_today:
            print("Щоб переглянути курс сьогодні, перейдіть у відповідне меню:")

        return (year_start, month_start, day_start)

    @staticmethod
    def create_list_of_dates(day_start, month_start, year_start, day_today, month_today, year_today):
        list = []
        check_month = False
        while year_start <= year_today:
            while month_start <= 12:
                if month_start == month_today and year_start == year_today:
                    check_month = True
                if month_start in [1, 3, 5, 7, 8, 10, 12]:  # дней в месяце 31
                    while day_start <= 31:
                        if month_start < 10: month_start_str = "0" + str(month_start)
                        else: month_start_str = str(month_start)
                        if day_start < 10: day_start_str = "0" + str(day_start)
                        else: day_start_str = str(day_start)
                        tmp = []
                        tmp.append(str(year_start))
                        tmp.append(month_start_str)
                        tmp.append(day_start_str)
                        list.append(tmp)
                        day_start += 1
                        if check_month and day_start == day_today:
                            return list
                        if day_start > 31:
                            month_start += 1
                    day_start = 1

                if month_start == 2 and year_start % 4 == 0 and year_start % 400 != 0:  # высокосный год, дней в месяце 29
                    while day_start <= 29:
                        if month_start < 10: month_start_str = "0" + str(month_start)
                        else: month_start_str = str(month_start)
                        if day_start < 10: day_start_str = "0" + str(day_start)
                        else: day_start_str = str(day_start)
                        tmp = []
                        tmp.append(str(year_start))
                        tmp.append(month_start_str)
                        tmp.append(day_start_str)
                        list.append(tmp)
                        day_start += 1
                        if check_month and day_start == day_today:
                            return list
                        if day_start > 29:
                            month_start += 1
                    day_start = 1

                if month_start == 2 and year_start % 4 != 0:  # обычный год, дней в месяец 28
                    while day_start <= 28:
                        if month_start < 10: month_start_str = "0" + str(month_start)
                        else: month_start_str = str(month_start)
                        if day_start < 10: day_start_str = "0" + str(day_start)
                        else: day_start_str = str(day_start)
                        tmp = []
                        tmp.append(str(year_start))
                        tmp.append(month_start_str)
                        tmp.append(day_start_str)
                        list.append(tmp)
                        day_start += 1
                        if check_month and day_start == day_today:
                            return list
                        if day_start > 28:
                            month_start += 1

                    day_start = 1

                if month_start in [4, 6, 9, 11]:  # дней в месяце 30
                    while day_start <= 30:
                        if month_start < 10: month_start_str = "0" + str(month_start)
                        else: month_start_str = str(month_start)
                        if day_start < 10: day_start_str = "0" + str(day_start)
                        else: day_start_str = str(day_start)
                        tmp = []
                        tmp.append(str(year_start))
                        tmp.append(month_start_str)
                        tmp.append(day_start_str)
                        list.append(tmp)
                        day_start += 1
                        if check_month and day_start == day_today:
                            return list
                        if day_start > 30:
                            month_start += 1
                    day_start = 1

            month_start = 1
            year_start += 1


class Give_nominals(object):

    @staticmethod
    def get_money(user_name, password, user_balance):
        print("Введіть сумму кратну '10', яку потрібно зняти\n Мінімальна сумма 10")
        sum_to_get = input("Ваша сумма: ")
        if sum_to_get.isdigit() is False:
            print("Введіть коректну сумму\n")
            Give_nominals.get_money(user_name, password, user_balance)
        sum_to_get = int(sum_to_get)
        if sum_to_get < 10 or sum_to_get % 10 != 0:
            print("Введіть коректну сумму:\n")
            Give_nominals.get_money(user_name, password, user_balance)
        sum_to_get_copy = sum_to_get
        try:
            if sum_to_get > int(user_balance):
                print("Недостятньо коштів...")
                start_menu(user_name, password, user_balance)
        except:
            if sum_to_get > int(user_balance[0]):
                print("Недостятньо коштів...")
                start_menu(user_name, password, user_balance)

        Give_nominals.banknotes_to_get(sum_to_get, user_name, sum_to_get_copy, user_balance, password)

    @staticmethod
    def banknotes_to_get(sum_to_get, user_name, sum_to_get_copy, user_balance, password):
        copy_sum_to_get = sum_to_get
        banknotes_dict = {}
        tmp = cur.execute('SELECT * FROM banknotes')
        for i in tmp:
            temp_dict = {i[0]: i[1]}
            banknotes_dict.update(temp_dict)
        list = [1000, 500, 200, 100, 50, 20, 10]
        uah_10 = uah_20 = uah_50 = uah_100 = uah_200 = uah_500 = uah_1000 = 0
        print(sum_to_get)

        while sum_to_get >= 1000 and int(banknotes_dict[1000]) > 0:
            uah_1000 += 1
            banknotes_dict[1000] = int(banknotes_dict[1000]) - 1
            sum_to_get -= 1000
        sum_to_get, uah_1000 = Give_nominals.exit_from_func(sum_to_get, 1000, uah_1000)

        while sum_to_get >= 500 and int(banknotes_dict[500]) > 0:
            uah_500 += 1
            banknotes_dict[500] = int(banknotes_dict[500]) - 1
            sum_to_get -= 500
        sum_to_get, uah_500 = Give_nominals.exit_from_func(sum_to_get, 500, uah_500)

        while sum_to_get >= 200 and int(banknotes_dict[200]) > 0:
            uah_200 += 1
            banknotes_dict[200] = int(banknotes_dict[200]) - 1
            sum_to_get -= 200
        sum_to_get, uah_200 = Give_nominals.exit_from_func(sum_to_get, 200, uah_200)

        while sum_to_get >= 100 and int(banknotes_dict[100]) > 0:
            uah_100 += 1
            banknotes_dict[100] = int(banknotes_dict[100]) - 1
            sum_to_get -= 100
        sum_to_get, uah_100 = Give_nominals.exit_from_func(sum_to_get, 100, uah_100)

        while sum_to_get >= 50 and int(banknotes_dict[50]) > 0:
            uah_50 += 1
            banknotes_dict[50] = int(banknotes_dict[50]) - 1
            sum_to_get -= 50
        sum_to_get, uah_50 = Give_nominals.exit_from_func(sum_to_get, 50, uah_50)

        while sum_to_get >= 20 and int(banknotes_dict[20]) > 0:
            uah_20 += 1
            banknotes_dict[20] = int(banknotes_dict[20]) - 1
            sum_to_get -= 20
        sum_to_get, uah_20 = Give_nominals.exit_from_func(sum_to_get, 20, uah_20)

        while sum_to_get >= 10 and int(banknotes_dict[10]) > 0:
            uah_10 += 1
            banknotes_dict[10] = int(banknotes_dict[10]) - 1
            sum_to_get -= 10
        sum_to_get, uah_10 = Give_nominals.exit_from_func(sum_to_get, 10, uah_10)

        if sum_to_get != 0:
            Give_nominals.greedy_method(copy_sum_to_get, user_name, sum_to_get_copy, user_balance, password)
        else:
            try: new_balance = user_balance - copy_sum_to_get
            except: new_balance = user_balance[0] - copy_sum_to_get
            cur.execute('UPDATE users SET balance == ? WHERE username == ?', (new_balance, user_name))
            banknotes_list = []
            cur.execute('DELETE  FROM banknotes')
            base.commit()
            for i in list:
                tmp = []
                tmp.append(i)
                tmp.append(banknotes_dict[i])
                banknotes_list.append(tmp)
            cur.executemany('INSERT INTO banknotes VALUES (?, ?)', (banknotes_list))
            base.commit()
            if uah_1000 != 0: print("1000 - " + str(uah_1000))
            if uah_500 != 0: print("500 - " + str(uah_500))
            if uah_200 != 0: print("200 - " + str(uah_200))
            if uah_100 != 0: print("100 - " + str(uah_100))
            if uah_50 != 0: print("50 - " + str(uah_50))
            if uah_20 != 0: print("20 - " + str(uah_20))
            if uah_10 != 0: print("10 - " + str(uah_10))
            start_menu(user_name, password, user_balance)

    @staticmethod
    def exit_from_func(sum_to_get, nominal, variable):
        banknotes_dict = {}
        tmp = cur.execute('SELECT * FROM banknotes')
        for i in tmp:
            temp_dict = {i[0]: i[1]}
            banknotes_dict.update(temp_dict)
        list = [10, 20, 50, 100, 200, 500, 1000]
        check = True
        while check and variable != 0:
            for i in list:
                if sum_to_get % i == 0 and int(banknotes_dict[i]) > 0:
                    check = False

            if check: sum_to_get += nominal; variable -= 1

        if check:
            return sum_to_get, 0
        else:
            return sum_to_get, variable

    @staticmethod
    def greedy_method(sum_to_get, user_name, sum_to_get_copy, user_balance, password):
        list = [1000, 500, 200, 100, 50, 20, 10]
        banknotes_dict = {}
        tmp = cur.execute('SELECT * FROM banknotes')
        for i in tmp:
            temp_dict = {i[0]: i[1]}
            banknotes_dict.update(temp_dict)
        uah_10 = uah_20 = uah_50 = uah_100 = uah_200 = uah_500 = uah_1000 = 0

        while sum_to_get >= 1000 and int(banknotes_dict[1000]) > 0:
            uah_1000 += 1
            banknotes_dict[1000] = int(banknotes_dict[1000]) - 1
            sum_to_get -= 1000

        while sum_to_get >= 500 and int(banknotes_dict[500]) > 0:
            uah_500 += 1
            banknotes_dict[500] = int(banknotes_dict[500]) - 1
            sum_to_get -= 500

        while sum_to_get >= 200 and int(banknotes_dict[200]) > 0:
            uah_200 += 1
            banknotes_dict[200] = int(banknotes_dict[200]) - 1
            sum_to_get -= 200

        while sum_to_get >= 100 and int(banknotes_dict[100]) > 0:
            uah_100 += 1
            banknotes_dict[100] = int(banknotes_dict[100]) - 1
            sum_to_get -= 100

        while sum_to_get >= 50 and int(banknotes_dict[50]) > 0:
            uah_50 += 1
            banknotes_dict[50] = int(banknotes_dict[50]) - 1
            sum_to_get -= 50

        while sum_to_get >= 20 and int(banknotes_dict[20]) > 0:
            uah_20 += 1
            banknotes_dict[20] = int(banknotes_dict[20]) - 1
            sum_to_get -= 20

        while sum_to_get >= 10 and int(banknotes_dict[10]) > 0:
            uah_10 += 1
            banknotes_dict[10] = int(banknotes_dict[10]) - 1
            sum_to_get -= 10
        if sum_to_get == 0:
            new_balance = user_balance - sum_to_get_copy
            cur.execute('UPDATE users SET balance == ? WHERE username == ?', (new_balance, user_name))
            banknotes_list = []
            cur.execute('DELETE  FROM banknotes')
            base.commit()
            for i in list:
                tmp = []
                tmp.append(i)
                tmp.append(banknotes_dict[i])
                banknotes_list.append(tmp)
            cur.executemany('INSERT INTO banknotes VALUES (?, ?)', (banknotes_list))
            base.commit()

            if uah_1000 != 0: print("1000 - " + str(uah_1000))
            if uah_500 != 0: print("500 - " + str(uah_500))
            if uah_200 != 0: print("200 - " + str(uah_200))
            if uah_100 != 0: print("100 - " + str(uah_100))
            if uah_50 != 0: print("50 - " + str(uah_50))
            if uah_20 != 0: print("20 - " + str(uah_20))
            if uah_10 != 0: print("10 - " + str(uah_10))

        value = 0
        list_of_values = cur.execute('SELECT * FROM banknotes')
        for i in list_of_values:
            value += i[1]

        if sum_to_get != 0 and value != 0:
            print("Нажаль банкомат не може видасти потрібну сумму, спробуйте змінити сумму\n")
            num = input("Якщо бажаєте вийти, натисніть '1', інакше будь який символ: ")
            if num == "1":
                start_menu(user_name, password, user_balance)
            Give_nominals.get_money(user_name, password, user_balance)

        elif sum_to_get != 0 and value == 0:
            print("Нажаль банкомат не має грошей\n")
            start_menu(user_name, password, user_balance)


def start_menu(login, password, balance=0):
    balance = cur.execute('SELECT balance FROM users WHERE username == ?', (login,)).fetchone()
    user = User(login, password, balance)
    print("")
    print("Введіть дію:\n1. Продивитись баланс\n2. Поповнити баланс\n3. Перевести кошти\n4. Подивитися курс сьогодні\n5. Порівняти курс\n6. Конвертувати\n7. Зняти кошти "
          "\n8. Вихід")
    number_from_user = input("Ваша дія: ")
    print("")
    if number_from_user.isdigit():
        number_from_user = int(number_from_user)
        if number_from_user == 1:
            user.look_balance(login, password)
        if number_from_user == 2:
            user.up_balance(login, password)
        if number_from_user == 3:
            user.down_balance(login, password)
        if number_from_user == 4:
            Curses.rate_today()
            start_menu(login, password, balance)
        if number_from_user == 5:
            Curses.print_rate()
            start_menu(login, password, balance)
        if number_from_user == 6:
            Curses.convert_valute()
            start_menu(login, password, balance)
        if number_from_user == 7:
            Give_nominals.get_money(login, password, balance)
        if number_from_user == 8:
            print("До зустрічі {}!".format(login))
            raise SystemExit
        if number_from_user < 1 or number_from_user > 8:
            print("Дії з таким номером не існує")
            start_menu(login, password, balance)
    else:
        print("Введіть буль-ласка число")
        start_menu(login, password, balance)


x = Person("Vlad", 1111)
login_menu()
