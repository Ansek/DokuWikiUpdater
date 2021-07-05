# Значение входных параметров по умолчанию
URL = 'http://192.168.1.137'
# Метки для поиска таблиц
BEG_CUR_EMP = '<html><a name=\'BegCurEmp\'></a></html>'  # Начало списка действующих сотрудников
END_CUR_EMP = '<html><a name=\'EndCurEmp\'></a></html>'  # Конец списка действующих сотрудников
BEG_FOR_EMP = '<html><a name=\'BegForEmp\'></a></html>'  # Начало списка бывших сотрудников
END_FOR_EMP = '<html><a name=\'EndForEmp\'></a></html>'  # Конец списка бывших сотрудников
# Заголовок таблицы
TABLE_HEADER = '^ ФИО сотрудника ^ Должность ^ Примечание ^'
# Шаблон для создания новой страницы
PAGES = '''====== {{0}} ======
===== Описание =====\n{0}
===== История отдела =====\n{0}
===== Действующие сотрудники =====\n{2}\n{1}\n{3}
===== Бывшие сотрудники =====\n{4}\n{1}\n{5}
===== Достижение отдела =====\n{0}'''.format(
    '(пункт создан автоматически, пожалуйста, заполните его данными)',
    TABLE_HEADER, BEG_CUR_EMP, END_CUR_EMP, BEG_FOR_EMP, END_FOR_EMP)

import sys
import csv
import getpass as gp
import argparse as ap
import dokuwiki as dw

# Обрабатывает аргументы командной строки
def get_args():
    # Определение парсера для указания параметров парсера
    parser = ap.ArgumentParser(
        description='Выполняет обновление информации о сотрудниках в DokuWiki.',
        epilog='© Июнь 2021. Автор: Секунов Александр. Группа: 4832.',
        add_help=False
    )
    parser.add_argument("user", help = 'Имя пользователя для доступа к DokuWiki')
    parser.add_argument("file", help = 'TSV-файл с информацией о сотрудниках')
    parser.add_argument("-a", "--address", default=URL, help = 'Адрес сервера DokuWiki')
    parser.add_argument('-h', '--help', action='help', help='Вызов справки')
    # Парсинг и возврат параметров
    return parser.parse_args(sys.argv[1:])

# Получает актуальный список сотрудников из файла
def get_list_from_file(filename):
    with open(args.file, encoding='utf-8') as f:
        # Чтение данных из файла в список
        t = csv.reader(f, delimiter='\t')
        l = list()
        i = 1
        for r in t:
            e = list(r)
            # Проверка корректности разбора
            if (len(e) < 5):
                print("В строке {0} нехватка полей. Возможно пропущен символ табуляции".format(i))
            else:
                l.append(e)
            i += 1
        # Сортировка по полям: подразделение, отдел, ФИО
        l.sort(key=lambda x:(x[1], x[0], x[2]))
        return l

# Извлекает текст содержимого таблицы из текста по меткам
def get_table(page, beg_str, end_str):
    beg = page.find(beg_str)        # Позиция метки начала
    end = page.find(end_str)        # Позиция метки конца
    beg = page.rfind('^', beg, end) # Пропуск заголовка
    return page[beg + 2:end - 1]    # Убрать символы ^ и \n

# Извлекает значения из строк таблицы
def parse_table(table):
    l = []
    for row in table.split('\n'):
        if row != '':
            values = row.split('|')
            l.append([values[1].strip(), values[2].strip(), values[3].strip()])
    return l

# Возвращает список действующих сотрудников из DokuWiki
def get_clist_from_wiki(page):
    table = get_table(page, BEG_CUR_EMP, END_CUR_EMP)
    return parse_table(table)

# Возвращает список действующих сотрудников из DokuWiki
def get_flist_from_wiki(page):
    table = get_table(page, BEG_FOR_EMP, END_FOR_EMP)
    return parse_table(table)

# Преобразование списка в таблицу DokuWiki
def list_to_table(list):
    table = ''
    for row in list:
        table += '| {0} | {1} | {2} |\n'.format(row[0], row[1], row[2])
    return table

# Формат ссылка на страницы отдела в DokuWiki
def format_link(department, subdivision):
    id = 'структура:{1}:{0}'.format(department, subdivision)
    return id.replace(" ", "").lower()

# Формирование и отправка страницы в DokuWiki
def set_page(wiki, page, page_id, clist, flist):
    b1 = page.find(BEG_CUR_EMP)
    e1 = page.find(END_CUR_EMP)
    b2 = page.find(BEG_FOR_EMP)
    e2 = page.find(END_FOR_EMP)
    # Сортировка по ФИО
    clist.sort(key=lambda x:(x[1]))
    flist.sort(key=lambda x:(x[1]))
    # Формирование обновленной страницы
    new_page = '{0}{1}\n{2}\n{3}{4}{5}\n{6}\n{7}{8}'.format(page[0:b1],
        BEG_CUR_EMP, TABLE_HEADER, list_to_table(clist), page[e1:b2],
        BEG_FOR_EMP, TABLE_HEADER, list_to_table(flist), page[e2:])
    # Отправка страницы в DokuWiki
    wiki.pages.set(page_id, new_page)

# Начало программы
if __name__ == '__main__':
    try:
        args = get_args()                                           # Получение параметров командной строки
        wiki = dw.DokuWiki(args.address, args.user, gp.getpass())   # Создание объекта для связи с DokuWiki
        file = get_list_from_file(args.file)                        # Получение данных из файла в виде списка
        if file.count == 0:
            raise Exception("Список в файле пуст")

        # Сравнение значение списка из файла и из страницы DokuWiki
        department = file[0][0]     # Отдел
        subdivision = file[0][1]    # Подразделение
        current_list_f = list()     # Список действующих сотрудников из файла
        page_id_list = list()       # Список проверенных страниц
        print(subdivision)          # Вывод заголовка подразделения
        file.append([None, None])   # Для еще одной итерации
        # Группировка операций по отделу и подразделение
        for row in file:
            # Набор данных 
            if department == row[0] and subdivision == row[1]:
                current_list_f.append(row[2:])
            # Обработка данных
            else:
                print('   {0}:'.format(department), end='')
                # Загрузка таблиц из DokuWiki
                page_id = format_link(department, subdivision)
                page = wiki.pages.get(page_id)
                page_id_list.append(page_id)            # Сохранение для проверки
                if (page == ''):                        # Если страницы нет, то добавляется шаблон для неё
                    page = PAGES.format(department)
                    print('\n     Создана новая страница', end='')
                # Получение списка действующих и бывших сотрудников из DokuWiki
                current_list_dw = get_clist_from_wiki(page)
                former_list_dw = get_flist_from_wiki(page)
                
                page_changed = False                    # Флаг, были ли изменения на странице
                is_old = [False] * len(current_list_f)  # Для определения новых сотрудников
                # Сравнение данных из DokuWiki
                for w in current_list_dw:
                    have = False                        # Флаг наличия в файле
                    # Сравнение с данными из файла (по конкретному отделу)
                    for i in range(len(current_list_f)):
                        f = current_list_f[i]
                        if (w[0] == f[0]):      # Проверка по ФИО
                            have = is_old[i] = True
                            if (w[1] != f[1]):  # Проверка по должности
                                print('\n     {0}: изменена должность'.format(f[0]), end='')
                                page_changed = True
                            if (w[2] != f[2]):  # Проверка по пометке отдела кадров
                                print('\n     {0}: изменена пометка отдела кадров'.format(f[0]), end='')
                                page_changed = True
                            break
                    # Если сотрудник из списка текущих в DokuWiki не найден в файле
                    if (not have):
                        former_list_dw.append(w) # Перемещение в список бывших
                        print('\n     {0}: перемещение в список бывших сотрудников'.format(w[0]), end='')
                        page_changed = True
                # Проверка наличия новых сотрудников
                for i in range(len(current_list_f)):
                    if (not is_old[i]):
                        print('\n     {0}: добавление в список действующих сотрудников'.format(current_list_f[i][0]), end='')
                        page_changed = True
                
                # Если требуется обновление страницы
                if page_changed:
                    set_page(wiki, page, page_id, current_list_f, former_list_dw)
                    print()
                else:
                    print(' нет изменений')

                # Если перебор данных не закончен
                if (row[0] != None):
                    # Вывод заголовка поздразделения
                    if (subdivision != row[1]):
                        print(row[1])
                    # Обновление информации
                    department = row[0]
                    subdivision = row[1]
                    current_list_f.clear()
                    current_list_f.append(row[2:])

        # Проверка на незатронутые страницы, в которых остались действующие сотрудники
        for p in wiki.pages.list():
            if not p['id'] in page_id_list and p['id'].find('структура') == 0:
                # Проверка наличия метки таблицы действующих сотрудников
                page = wiki.pages.get(p['id'])
                if page.find(BEG_CUR_EMP):
                    # Проверка наличия данных о действующих сотрудниках
                    current_list_dw = get_clist_from_wiki(page)
                    if len(current_list_dw) > 0:
                        # Получение списка бывших сотрудников
                        former_list_dw = get_flist_from_wiki(page)
                        former_list_dw.extend(current_list_dw)
                        print('{0} - перемещение списка действующих сотрудников в список бывших '.format(p['id']))
                        set_page(wiki, page, p['id'], [], former_list_dw)

    except (Exception) as err:
        print('\nError: {0}'.format(err))