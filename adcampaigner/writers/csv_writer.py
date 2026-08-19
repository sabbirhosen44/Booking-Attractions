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

        self._file = None
        self._writer = None
        self._current_filename = None
        self._current_count = 0
        self._part = 0
        self._base_filename = None
        self._files = []

    def start(self, filename: str) -> None:
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._base_filename = filename
        self._part = 0
        self._files = []

        self._open_next_file()

    def write_row(self, row: dict) -> None:
        if self._file is None:
            raise RuntimeError(
                "CsvWriter has not been started. "
                "Call start() before write_row()."
            )

        if (
            self._current_count
            >= self.max_rows_per_file
        ):
            self._close_current_file()
            self._open_next_file()

        self._writer.writerow(
            self._get_row_values(row)
        )

        self._current_count += 1

    def finish(self) -> list[tuple[str, int]]:
        if self._file is None:
            return []

        self._close_current_file()

        return self._finalize_filenames()

    def _open_next_file(self) -> None:
        self._part += 1
        self._current_count = 0

        filename = self._build_part_filename(
            self._base_filename,
            self._part,
        )

        output_path = (
            self.output_dir / filename
        )

        self._file = output_path.open(
            "w",
            encoding="utf-8",
            newline="",
        )

        self._writer = csv.writer(
            self._file
        )

        self._writer.writerow(
            self.HEADERS
        )

        self._current_filename = filename

    def _close_current_file(self) -> None:
        if self._file is None:
            return

        self._file.close()

        self._files.append(
            (
                self._current_filename,
                self._current_count,
            )
        )

        self._file = None
        self._writer = None

    def _finalize_filenames(self):
        if not self._files:
            return []

        # If only one part was generated and it has
        # <= max_rows_per_file records, rename:
        #
        # *_part1.csv
        #
        # to:
        #
        # *.csv
        #
        if len(self._files) == 1:
            filename, count = self._files[0]

            if filename.endswith("_part1.csv"):
                final_filename = (
                    filename[:-len("_part1.csv")]
                    + ".csv"
                )

                source = (
                    self.output_dir / filename
                )

                destination = (
                    self.output_dir
                    / final_filename
                )

                if destination.exists():
                    destination.unlink()

                source.rename(destination)

                return [
                    (
                        final_filename,
                        count,
                    )
                ]

        return self._files

    @staticmethod
    def _build_part_filename(
        filename: str,
        part: int,
    ) -> str:
        path = Path(filename)

        return (
            f"{path.stem}_part{part}"
            f"{path.suffix}"
        )

    def _get_row_values(
        self,
        row: dict,
    ) -> list[str]:
        return [
            self._get_value(
                row,
                field,
            )
            for field in self.FIELD_KEYS
        ]

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