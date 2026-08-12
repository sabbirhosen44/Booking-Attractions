from pathlib import Path
from html import escape


class HtmlIndexWriter:

    def __init__(
        self,
        output_dir: Path,
        feed_base_url: str,
    ):
        self.output_dir = Path(output_dir)
        self.feed_base_url = feed_base_url.rstrip("/")

    def write(self, feed_files):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = self.output_dir / "index.html"

        rows = self._build_rows(feed_files)

        html = self._build_html(rows)

        index_path.write_text(
            html,
            encoding="utf-8",
        )

        return index_path

    def _build_rows(self, feed_files):
        rows = []

        for filename in sorted(feed_files):
            feed_url = f"{self.feed_base_url}/{filename}"

            rows.append(
                {
                    "filename": filename,
                    "feed_url": feed_url,
                }
            )

        return rows

    def _build_html(self, rows):
        table_rows = []

        for index, row in enumerate(rows, start=1):
            filename = escape(row["filename"])
            feed_url = escape(row["feed_url"], quote=True)

            table_rows.append(
                f"""
                <tr>
                    <td>{index}</td>
                    <td>
                        <a href="{feed_url}" target="_blank">
                            {filename}
                        </a>
                    </td>
                </tr>
                """
            )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking.com Property Feed Index</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}

        h1 {{
            margin-bottom: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th,
        td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}

        th {{
            background: #f4f4f4;
        }}

        a {{
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>Booking.com Property Feed Index</h1>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Feed URL</th>
            </tr>
        </thead>

        <tbody>
            {"".join(table_rows)}
        </tbody>
    </table>
</body>
</html>
"""