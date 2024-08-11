from bs4 import BeautifulSoup
import os, time, re, requests, json
from terminaltables import SingleTable
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

# Логотип программы
logo = """
   _____            _____       _   _                 _____            _             
  / ____|          |  __ \     | | | |               |  __ \          (_)            
 | |  __  ___ _ __ | |__) |   _| |_| |__   ___  _ __ | |  | | _____  ___ _ __   __ _ 
 | | |_ |/ _ \ '_ \|  ___/ | | | __| '_ \ / _ \| '_ \| |  | |/ _ \ \/ / | '_ \ / _` |
 | |__| |  __/ | | | |   | |_| | |_| | | | (_) | | | | |__| | (_) >  <| | | | | (_| |
  \_____|\___|_| |_|_|    \__, |\__|_| |_|\___/|_| |_|_____/ \___/_/\_\_|_| |_|\__, |
                           __/ |                                                __/ |
                          |___/                                                |___/ 
"""

# Описание основного меню
def print_main_menu():
    print(f"{Fore.RED}{logo}")
    print(f"""
{Fore.LIGHTYELLOW_EX}╭─────────────────────────━━━━━━━━━━━━━━━━━━━━━━─────────────────────╮
{Fore.LIGHTYELLOW_EX}| {Fore.RED}[1] {Fore.CYAN}Попробовать получить пароль по email (иногда работает)         {Fore.LIGHTYELLOW_EX}| 
{Fore.LIGHTYELLOW_EX}| {Fore.RED}[2] {Fore.CYAN}Поиск информации по нику                                       {Fore.LIGHTYELLOW_EX}| 
{Fore.LIGHTYELLOW_EX}| {Fore.RED}[3] {Fore.CYAN}Получить информацию по IP                                      {Fore.LIGHTYELLOW_EX}| 
{Fore.LIGHTYELLOW_EX}| {Fore.RED}[4] {Fore.CYAN}Поиск информации по нескольким параметрам (ник, имя, город ...){Fore.LIGHTYELLOW_EX}| 
{Fore.LIGHTYELLOW_EX}| {Fore.RED}[5] {Fore.CYAN}Получить историю ников для Minecraft                           {Fore.LIGHTYELLOW_EX}| 
{Fore.LIGHTYELLOW_EX}| {Fore.RED}cls {Fore.CYAN}Очистить экран                                                 {Fore.LIGHTYELLOW_EX}|
{Fore.LIGHTYELLOW_EX}| {Fore.RED}ctrl + c {Fore.CYAN}Выйти из программы                                        {Fore.LIGHTYELLOW_EX}|
╰─────────────────────────━━━━━━━━━━━━━━━━━━━━━━─────────────────────╯
""")

# Чтение конфигурационного файла для API ключа
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()

# Класс для работы с утечками данных
class DataLeakChecker:
    def check_email(self, email_address):
        data_list = []
        try:
            response = requests.get(f"https://haveibeenpwned.com/api/v2/breachedaccount/{email_address}",
                                    headers={"Content-Type": "application/json",
                                             "Accept": "application/json",
                                             "User-Agent": "geniuszly",
                                             "hibp-api-key": config["HIBP_API_KEY"]})
            if response.status_code == 200:
                breaches = json.loads(response.text)
                for breach in breaches:
                    data_list.append({'Title': breach['Title'], 'Domain': breach['Domain'], 'Date': breach['BreachDate']})
            return data_list
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            return None

# Символы для отображения статусов
symbols = {
    'warning': f"[{Fore.RED}!{Fore.RESET}]",
    'question': f"[{Fore.YELLOW}?{Fore.RESET}]",
    'found': f"[{Fore.GREEN}+{Fore.RESET}]",
    'info': f"[{Fore.BLUE}I{Fore.RESET}]",
    'wait': f"[{Fore.MAGENTA}*{Fore.RESET}]"
}

# Функция для поиска информации в Google
def search_in_google(query='', secondary_query=''):
    encoding_dict = {
        "%21": "!", "%23": "#", "%24": "$", "%26": "&", "%27": "'",
        "%28": "(", "%29": ")", "%2A": "*", "%2B": "+", "%2C": ",",
        "%2F": "/", "%3A": ":", "%3B": ";", "%3D": "=", "%3F": "?",
        "%40": "@", "%5B": "[", "%5D": "]", "%20": " ", "%22": "\"",
        "%25": "%", "%2D": "-", "%2E": ".", "%3C": "<", "%3E": ">",
        "%5C": "\\", "%5E": "^", "%5F": "_", "%60": "`", "%7B": "{",
        "%7C": "|", "%7D": "}", "%7E": "~"
    }

    def decode_url(encoded_url):
        for char, decoded_char in encoding_dict.items():
            encoded_url = encoded_url.replace(char, decoded_char)
        return encoded_url

    urls = re.findall('url\\?q=(.*?)&', query.text if query else secondary_query.text)
    for url in urls:
        decoded_url = decode_url(url)
        if not any(blocked in decoded_url for blocked in ["googleusercontent", "/settings/ads", "/policies/faq"]):
            print(f"{Fore.RED}[++] Возможный детект: {Fore.GREEN}{decoded_url}")

# Функция для поиска информации по запросу
def google_search():
    print(f"\n{symbols['info']} Введите имя, фамилию, город, спорт, школу ... \n (Чем больше информации, тем точнее будет поиск)\n")
    user_input = input(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Введите данные: ")
    print(f"\n{symbols['wait']} Идет поиск информации...")
    search_url = "https://www.google.com/search?num=20&q=\\%s\\"
    try:
        search_terms = user_input.split()
        if not search_terms:
            print(f"{Fore.RED}[!]{Fore.GREEN} Недостаточно параметров...\n")
            return
        search_query = "+".join(search_terms)
        response = requests.get(search_url % search_query)
        search_in_google(query=response)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")

# Функция для поиска утечек по email
def search_email():
    print()
    email_input = input(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Введите email: ")
    print(f"\n{symbols['wait']} Идет проверка данных для '{email_input}'...")
    leaker = DataLeakChecker()
    leaks = leaker.check_email(email_input)

    if leaks:
        table_data = [('Title', 'Domain', 'Date')]
        for leak in leaks:
            table_data.append((leak['Title'], leak['Domain'], leak['Date']))
        table = SingleTable(table_data, " Leaked Site ")
        print(table.table)

        print(f"\n{symbols['wait']} Поиск пароля...")

        dump_table = [('Email', 'Password')]
        google_search_url = "https://www.google.fr/search?num=100&q=\\intext:\"%s\"\\"
        content = requests.get(google_search_url % email_input).text
        urls = re.findall('url\\?q=(.*?)&', content)
        count_passwords = 0

        if not urls:
            print(symbols['warning'] + f" Нет результатов для '{email_input}'...")
        else:
            print(symbols['wait'] + f" Проверка {len(urls)} ссылок...")
            for url in urls:
                if not any(blocked in url for blocked in ["googleusercontent", "/settings/ads", "webcache.googleusercontent.com/", "/policies/faq"]):
                    try:
                        page_text = requests.get(url).text
                        password_match = re.search(email_input + r":([a-zA-Z0-9_ & * $ - ! / ; , ? + =  | \. ]+)", page_text)
                        if password_match:
                            password = password_match.group().split(":")[1]
                            dump_table.append((email_input, password))
                            count_passwords += 1
                    except:
                        pass
            if count_passwords > 0:
                dump_table_display = SingleTable(dump_table, " Dump ")
                print(f"\n{dump_table_display.table}")
            else:
                print(symbols['warning'] + f" Пароль для '{email_input}' не найден.")

# Функция для поиска информации по нику пользователя
def search_username():
    print()
    username = input(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Введите ник: ")
    print(f"\n  {symbols['wait']} Поиск информации для '{username}'...")

    search_url = "https://www.google.com/search?num=100&q=\\%s\\"
    search_url_2 = "https://www.google.com/search?num=100&q=\\intitle:\"%s\"\\"
    response = requests.get(search_url % username)
    response2 = requests.get(search_url_2 % username)
    search_in_google(query=response, secondary_query=response2)

# Функция для получения информации по IP
def search_ip():
    print()
    target_ip = input(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Введите IP: ")
    ip_info_url = "http://ip-api.com/json/"
    try:
        response = requests.get(ip_info_url + target_ip)
        ip_data = json.loads(response.text)
        if ip_data['status'] == 'fail':
            print(f"{symbols['warning']} Невозможно получить данные для IP: {target_ip}")
        else:
            print(rf"""
{Fore.LIGHTYELLOW_EX}╭─────────────────━━━━━━━━━━━━━━━━━━━━─────────────╮
| {Fore.LIGHTGREEN_EX}IP: {ip_data['query']}                        {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}ISP: {ip_data['isp']}                           {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}Country: {ip_data['country']}                        {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}TimeZone: {ip_data['timezone']}                            {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}Region: {ip_data['regionName']} - {ip_data['zip']}                          {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}City: {ip_data['city']}                                {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}Lat/Lon: {ip_data['lat']}/{ip_data['lon']}                          {Fore.LIGHTYELLOW_EX}|
| {Fore.LIGHTGREEN_EX}Org: {ip_data['org']}                             {Fore.LIGHTYELLOW_EX}|
╰─────────────────━━━━━━━━━━━━━━━━━━━━─────────────╯
            """)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")

# Функция для получения истории ников Minecraft
def get_minecraft_username_history():
    print()
    minecraft_nick = input(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Введите ник Minecraft: ")
    lower_nick = minecraft_nick.lower()
    namemc_url = f"https://ru.namemc.com/profile/{lower_nick}"

    try:
        response = requests.get(namemc_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Проверка на статус аккаунта
            status_div = soup.find("div", class_="card-body text-center")
            if status_div and "Статус Доступно" in status_div.get_text():
                print(Fore.RED + f"  NICK: {Fore.YELLOW}{lower_nick}")
                print(Fore.RED + f"  TYPE: {Fore.YELLOW}Cracked")
                return

            # Парсинг UUID
            uuid_element = soup.find("span", {"class": "text-muted"})
            uuid = uuid_element.text if uuid_element else "Не найден"

            # Парсинг истории ников
            names_section = soup.find("div", {"id": "name-history"})
            names_list = []
            if names_section:
                names = names_section.find_all("strong")
                names_list = [name.text.strip() for name in names]

            names_display = "\n".join([f"  {name}" for name in names_list])

            print()
            print(Fore.RED + f"  NICK: {Fore.YELLOW}{lower_nick}")
            print(Fore.RED + f"  TYPE: {Fore.YELLOW}Premium")
            print(Fore.RED + f"  UUID: {Fore.GREEN}{uuid}")
            print(Fore.RED + f"  HISTORY NICKS:\n{Fore.CYAN}{names_display}")
            print()
        else:
            print(f"{Fore.RED}Ошибка: Не удалось получить доступ к сайту NameMC.")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")

# Печать основного меню
print_main_menu()

# Основной цикл программы
try:
    while True:
        command = input(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Введите команду: ")
        if command == "1":
            search_email()
        elif command == "2":
            search_username()
        elif command == "3":
            search_ip()
        elif command == "4":
            google_search()
        elif command == "5":
            get_minecraft_username_history()
        elif command == "cls":
            os.system("cls")
            print_main_menu()
except KeyboardInterrupt:
    print(f"{Fore.LIGHTYELLOW_EX}[ {Fore.LIGHTRED_EX}GenPythonDoxing {Fore.LIGHTYELLOW_EX}] {Fore.LIGHTBLUE_EX}» Программа завершена.")
    time.sleep(1.5)
except Exception as e:
    print(f"{Fore.RED}Error: {e}")
