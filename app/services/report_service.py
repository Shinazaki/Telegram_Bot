from datetime import datetime
from pathlib import Path
from tempfile import gettempdir

from openpyxl import Workbook


HEADER = [
    "ФИО студента",
    "Дата пропуска",
    "Тип причины",
    "Наличие справки",
]


def _reason_label(reason_type: str) -> str:
    mapping = {
        "official": "Официальная",
        "unofficial": "Неофициальная",
    }
    return mapping.get(reason_type, reason_type)


def build_group_report(rows: list[dict], group_number: int | None) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Пропуски"

    sheet.append(HEADER)

    for row in rows:
        sheet.append(
            [
                row["full_name"],
                row["absence_date"].strftime("%Y-%m-%d"),
                _reason_label(row["reason_type"]),
                "Да" if row["has_document"] else "Нет",
            ]
        )

    for column_cells in sheet.columns:
        column_width = max(len(str(cell.value or "")) for cell in column_cells) + 2
        sheet.column_dimensions[column_cells[0].column_letter].width = min(column_width, 50)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    group_label = group_number if group_number is not None else "unknown"
    file_name = f"absence_report_group_{group_label}_{stamp}.xlsx"
    output_path = Path(gettempdir()) / file_name
    workbook.save(output_path)

    return output_path
