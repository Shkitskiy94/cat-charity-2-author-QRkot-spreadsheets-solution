import io
from datetime import datetime
from typing import List
import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient
from app.models import CharityProject


def format_time_delta(td) -> str:
    """Форматирует timedelta в читаемый вид"""
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60

    if days > 0:
        return f"{days} дн. {hours} ч."
    else:
        return f"{hours} ч. {minutes} мин."


async def create_simple_report(
        yandex_client: YandexDiskClient,
        projects: List[CharityProject]
) -> str:
    """
    Создаёт Excel файл с отчётом на Яндекс.Диске
    """
    now_date_time = datetime.now().strftime(settings.report_format)
    safe_filename = f"QRKot_report_{now_date_time}".replace(':', '-').replace(' ', '_')

    # Получаем ссылку для загрузки и путь к файлу
    upload_url, file_path = await yandex_client.create_excel_file(safe_filename)

    # Создаём Excel файл в памяти
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Проекты")

    # Добавляем заголовок
    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    worksheet.merge_range('A1:C1', f"Отчёт от {now_date_time}", title_format)

    # Формат для заголовков таблицы
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2F75B5',
        'font_color': 'white',
        'border': 1
    })

    # Заголовки колонок (начинаем со 2 строки, т.к. 1-я занята заголовком)
    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    # Формат для данных
    cell_format = workbook.add_format({'border': 1})

    # Данные проектов
    for row, project in enumerate(projects, start=2):
        close_time = project.close_date - project.create_date
        worksheet.write(row, 0, project.name, cell_format)
        worksheet.write(row, 1, format_time_delta(close_time), cell_format)
        worksheet.write(row, 2, project.description, cell_format)

    # Добавляем итог
    last_row = len(projects) + 3
    total_format = workbook.add_format({'bold': True, 'border': 1})
    worksheet.merge_range(f'A{last_row}:C{last_row}',
                          f"Всего проектов: {len(projects)}",
                          total_format)

    # Автоматически подгоняем ширину колонок
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 40)

    workbook.close()
    output.seek(0)

    # Загружаем файл на Яндекс.Диск
    await yandex_client.upload_file(upload_url, output.getvalue())

    # Делаем файл публичным и возвращаем ссылку
    public_url = await yandex_client.publish_file(file_path)
    return public_url