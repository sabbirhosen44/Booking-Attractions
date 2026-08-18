import csv
from pathlib import Path

class CsvWriter:

    HEADERS = [
        "Page URL",
        "Custom label",
    ]

    FIELD_KEYS = [
        "page_url",
        "custom_label",
    ]

    def __init__(
        self,
        output_dir: Path,
        max_rows_per_file: int,
    ):
        self.output_dir = Path(output_dir)
        self.max_rows_per_file = max_rows_per_file

    def write(
        self,
        rows,
        filename: str,
    ) -> list[str]:

        rows = list(rows)

        if not rows:
            return []

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        files = []
        total_rows = len(rows)

        for start in range(
            0,
            total_rows,
            self.max_rows_per_file,
        ):
            chunk = rows[
                start:start + self.max_rows_per_file
            ]

            part = start // self.max_rows_per_file + 1

            output_filename = self._build_filename(
                filename,
                part,
                total_rows,
            )

            output_path = self.output_dir / output_filename

            self._write_file(
                output_path,
                chunk,
            )

            files.append(output_filename)

        return files

    def _write_file(
        self,
        output_path: Path,
        rows: list[dict],
    ) -> None:

        with output_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(self.HEADERS)

            for row in rows:
                writer.writerow(
                    [
                        self._get_value(row, key)
                        for key in self.FIELD_KEYS
                    ]
                )

    @staticmethod
    def _get_value(
        row: dict,
        field: str,
    ) -> str:

        value = row.get(field)

        if value is None:
            return "void"

        value = str(value).strip()

        return value if value else "void"

    @staticmethod
    def _build_filename(
        filename: str,
        part: int,
        total_rows: int,
    ) -> str:

        if total_rows <= 700000 or part == 1:
            return filename

        path = Path(filename)

        return (
            f"{path.stem}_part{part}"
            f"{path.suffix}"
        )