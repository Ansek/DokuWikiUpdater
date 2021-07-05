# DokuWikiUpdater
## Формулировка задания:
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
