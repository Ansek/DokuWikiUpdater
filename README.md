# DokuWikiUpdater
Данный Python-скрипт осуществляет обновление информации о сотрудниках на страницах отделов вики-движка DokuWiki, используя данные из TSV-файла, согласно заданию по производственной практике.
- [Формулировка задания](#Wording);
- [Настройка DokuWiki в Ubuntu 20.04](#Setting);
    - [Установка и подготовка HTTP-сервера Apache](#Setting);
    - [Установка DokuWiki](#Setting);
    - [Настройка DokuWiki для работы со скриптом](#Setting);
- [Описание работы со скриптом](#Script).

## <a name="Wording"></a> Формулировка задания:
 Имеется инсталляция DokuWiki для нужд крупной организации, структура wiki следующая. Каждому отделу соответствует отдельная страница, название отдела совпадает с названием страницы. На такой странице, среди прочей информации, есть перечни действующих и бывших сотрудников, оформленные в виде таблиц. Можно и нужно предложить дополнительные невидимые метки, которые будут вставляться в код вики-страниц вокруг таблиц со списком сотрудников на странице отдела, чтобы эти блоки кода страниц было проще найти программно.
 Также есть текстовый файл в формате TSV, который с определенной периодичностью обновляется (выгружается из базы данных), со следующей структурой:
- название отдела;
- название подразделения, к которому относится отдел;
- ФИО сотрудника;
- должность сотрудника;
- дополнительные пометки отдела кадров.

Доступа к самой базе нет, только к выгрузке в текстовом файле. Одна строка в файле соответствует одной занятой единице штатного расписания. Если один человек работает сразу в нескольких отделах (совместитель), в файле будет несколько строк с одним и тем же ФИО, но разными названиями отдела.
Необходимо написать скрипт на питоне (версии не ниже 3.7) для автоматической сверки данных на страницах вики с очередной выгрузкой из базы сотрудников. Скрипт должен обновлять только ту часть страницы каждого из отделов, где находится список действующих и бывших сотрудников. Должны быть обработаны следующие сценарии:

1. В выгрузке есть сотрудник, который отсутствует на странице отдела в вики. Нужно добавить этого сотрудника в таблицу со списком действующих сотрудников на странице в вики.
2. В выгрузке нет сотрудника, который присутствует на странице отдела в вики. Нужно переместить запись об этом сотруднике на странице в вики из таблицы действующих сотрудников отдела в таблицу бывших сотрудников.
3. Сотрудник есть и в выгрузке, и на странице отдела в вики, однако значение полей "должность" или "пометки отдела кадров" отличаются. Нужно обновить соответствующие поля в вики, т.к. информация в выгрузке более актуальна.
4. Ситуация перехода сотрудника из одного отдела в другой равносильна выполнению сценариев 1 и 2 одновременно, поскольку для старого отдела сотрудник в выгрузке будет отсутствовать, а для нового он появится. Отдельно учитывать этот случай не нужно, код должен его корректно обрабатывать за счет сценариев 1 и 2.
5. В выгрузке присутствует отдел, страницы которого нет в вики. Нужно создать новую страницу для этого отдела, на странице создать таблицу текущих сотрудников на основе данных из выгрузки, и пустую таблицу бывших сотрудников (только заголовки столбцов).
 Поскольку доступ к корпоративной вики ограничен, самостоятельно установить DokuWiki и наполнить ее тестовыми данными о нескольких вымышленных отделах. Продемонстрировать корректную обработку всех сценариев. 

## <a name="Setting"></a> Настройка DokuWiki в Ubuntu 20.04:
1.<a name="Setting1"></a> Установка и подготовка HTTP-сервера Apache.
- Обновление информации о пакетах:

        sudo apt update
- Установка Apache и библиотек для работы с PHP для DokuWiki:

        sudo apt install apache2 php php-xml libapache2-mod-php
- Изменение владельца, для доступа к директории `/var/www/html`:
        
        sudo chown -R $USER:$USER /var/www/html
2.<a name="Setting2"></a> Установка DokuWiki.
- Далее требуется скачать архив DokuWiki c [оффициального сайта](https://www.dokuwiki.org/dokuwiki), перенести его содержимое в директорию `/var/www/html` (для удаленного доступа из Windows можно, например, использовать [WinSCP](https://winscp.net/eng/download.php)) и перейти в неё:
        
        cd /var/www/html/
- После чего выполнить команду, для предоставления доступа к трём директориям:

        chmod -R 777 data/ ; chmod -R 777 lib/ ; chmod -R 777 conf/

- Для установки DokuWiki на сервере нужно перейти по ссылке `<IP-адрес сервера или домен>/install.php` и заполнить предоставленную форму.

3.<a name="Setting3"></a> Настройка DokuWiki для работы со скриптом.
- Войти в свою учетную запись и перейти к настройкам *"Управление" → "Настройки вики"* (*"Admin" → "Configuration Manager"*) и выполнить дальнейшие изменения.
- В категории *"Параметры аутентификации"* (*"Authentication"*):
    - Для разрешения доступа по XML-RPC нужно установить галочку у пункта *"remote"*;
    - В пункте *"remoteuser"* нужно перечислить названия аккаунтов пользователей, которые будут обновлять информацию о сотрудниках через скрипт. Новых пользователей можно добавить в пункте *"Управление" → "Управление пользователями"* (*"Admin" → "User Manager"*).
- В категории *"Параметры правки"* (*"Editing"*):
    - Чтобы скрыть HTML-метки, которые используются для определения таблиц, нужно поставить галочку у пункта *"htmlok"*.

***Дополнительно:*** для перезагрузки Apache можно воспользоваться следующей командой:

    sudo systemctl reload apache2
Это может пригодится, например, для смены часового пояса (чтобы в DokuWiki указывалось корректное время внесенных изменений):

    sudo timedatectl set-timezone Europe/Moscow 
## <a name="Script"> Описание работы со скриптом: 
Для работы требуется наличие библиотеки python-dokuwiki, которую можно установить командой: 

    pip install dokuwiki

Предполагается, что страница отделов имеет следующую структуру:
```
====== <Название отдела> ======
===== Описание =====
<Текст описания данного отдела>
===== История отдела =====
<Текст истории данного отдела>
===== Действующие сотрудники =====
<html><a name='BegCurEmp'></a></html>
^ ФИО сотрудника ^ Должность ^ Примечание ^
[| <ФИО> | <Должность> | <Примечание отдела кадров> |]
[...]
<html><a name='EndCurEmp'></a></html>
===== Бывшие сотрудники =====
<html><a name='BegForEmp'></a></html>
^ ФИО сотрудника ^ Должность ^ Примечание ^
[| <ФИО> | <Должность> | <Примечание отдела кадров> |]
[...]
<html><a name='EndForEmp'></a></html>
===== Достижение отдела =====
<Список достижений отдела>
```
и доступ к ней осуществляется по ссылке вида `структура:<название подразделения>:<название отдела>`.
Значения заключенные в `<html>…</html>` содержит якоря, которые играют роль невидимых меток, которые используются скриптом для поиска начала и конца нужных таблиц:
- BegCurEmp и EndCurEmp для таблицы "Действующих сотрудников";
- BegForEmp и EndForEmp для таблицы "Бывших сотрудников".

Данные метки должны быть невидимыми для обычного пользователя. Если же теги отображаются, то значит пункт настройки *"htmlok"* не был включен.

Содержимое файла, на основе которого происходит обновление, должно иметь пять полей, разделенных одним символом табуляции (\t):
```
<Название отдела>\t<Название подразделения>\t<ФИО>\t<Должность>\t<Примечание отдела кадров>
...
```
Скрипт поддерживает вызов справки, которая имеет следующий вид:
```
python.exe .\update_dokuwiki.py -h
usage: update_dokuwiki.py [-a ADDRESS] [-h] user file

Выполняет обновление информации о сотрудниках в DokuWiki.

positional arguments:
  user                  Имя пользователя для доступа к DokuWiki
  file                  TSV-файл с информацией о сотрудниках

optional arguments:
  -a ADDRESS, --address ADDRESS
                        Адрес сервера DokuWiki
  -h, --help            Вызов справки

© Июнь 2021. Автор: Секунов Александр. Группа: 4832.
```
Адрес сервера можно указать как через необязательный параметр `address`, так и записав значение в самом скрипте через константную переменную `URL`.
В итоге, для использования скрипта нужно использовать команду:

    python.exe .\update_dokuwiki.py <имя пользователя> <имя файла>
После чего будет осуществлён запрос пароля и при его подтверждении будет выведен лог сделанных изменений.
