import csv
from html import escape
from pathlib import Path

from adcampaigner.config import AdCampaignerConfig


class HtmlIndexWriter:

    def __init__(self):
        self.output_dir = AdCampaignerConfig.OUTPUT_DIR
        self.feed_base_url = AdCampaignerConfig.FEED_BASE_URL

    def write(self, feed_entries):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = (
            self.output_dir
            / AdCampaignerConfig.INDEX_FILE_NAME
        )

        rows = self._build_rows(feed_entries)

        html = self._build_html(rows)

        index_path.write_text(
            html,
            encoding="utf-8",
        )

        return index_path

    def _build_rows(self, feed_entries):
        rows = []

        for filename, campaign_type in sorted(
            feed_entries,
            key=lambda entry: entry[0],
        ):
            file_path = self.output_dir / filename

            if not file_path.exists():
                continue

            count = self._get_row_count(file_path)

            feed_url = (
                AdCampaignerConfig.get_remarketing_feed_url(filename)
                if campaign_type == AdCampaignerConfig.REMARKETING_CAMPAIGN_TYPE
                else AdCampaignerConfig.get_feed_url(filename)
            )

            rows.append(
                {
                    "campaign_type": campaign_type,
                    "route": AdCampaignerConfig.ROUTE,
                    "feed_url": feed_url,
                    "location_names": (
                        AdCampaignerConfig.LOCATION_NAMES
                    ),
                    "count": count,
                    "status": AdCampaignerConfig.STATUS,
                }
            )

        return rows

    @staticmethod
    def _get_row_count(file_path: Path) -> int:
        count = 0

        with file_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.reader(file)

            # Skip CSV header.
            next(reader, None)

            for _ in reader:
                count += 1

        return count

    @staticmethod
    def _build_html(rows):
        table_rows = []

        for row in rows:
            campaign_type = escape(
                str(row["campaign_type"])
            )

            route = escape(
                str(row["route"])
            )

            feed_url = escape(
                row["feed_url"],
                quote=True,
            )

            feed_filename = escape(
                row["feed_url"].rsplit("/", 1)[-1]
            )

            location_names = escape(
                str(row["location_names"])
            )

            count = row["count"]

            status = row["status"]

            table_rows.append(
                f"""
                <tr>
                    <td>{campaign_type}</td>
                    <td>{route}</td>
                    <td>
                        <a
                            href="{feed_url}"
                            target="_blank"
                        >
                            {feed_filename}
                        </a>
                    </td>
                    <td>{location_names}</td>
                    <td>{count}</td>
                    <td>{status}</td>
                </tr>
                """
            )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Feed Index</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 8px;
            font-size: 14px;
        }}

        table {{
            border-collapse: collapse;
            width: auto;
        }}

        th,
        td {{
            border: 1px solid #999;
            padding: 2px 4px;
            text-align: left;
            white-space: nowrap;
        }}

        th {{
            font-weight: bold;
            background: #f5f5f5;
        }}

        a {{
            color: #0000ee;
        }}
    </style>
</head>

<body>

<table>
    <thead>
        <tr>
            <th>Campaign Type</th>
            <th>Route</th>
            <th>Feed Url</th>
            <th>Location Names</th>
            <th>Count</th>
            <th>Status</th>
        </tr>
    </thead>

    <tbody>
        {"".join(table_rows)}
    </tbody>
</table>

</body>
</html>
"""