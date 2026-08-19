from html import escape

from adcampaigner.config import AdCampaignerConfig


class HtmlIndexWriter:

    def __init__(self):
        self.output_dir = (
            AdCampaignerConfig.OUTPUT_DIR
        )

    def write(self, feed_entries):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = (
            self.output_dir
            / AdCampaignerConfig.INDEX_FILE_NAME
        )

        with index_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            self._write_html_start(file)
            self._write_table_header(file)

            for (
                filename,
                campaign_type,
                count,
            ) in sorted(
                feed_entries,
                key=lambda entry: entry[0],
            ):
                self._write_table_row(
                    file,
                    filename,
                    campaign_type,
                    count,
                )

            self._write_html_end(file)

        return index_path

    @staticmethod
    def _write_html_start(file):
        file.write(
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Feed Index</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 8px;
            font-size: 14px;
        }

        table {
            border-collapse: collapse;
            width: auto;
        }

        th,
        td {
            border: 1px solid #999;
            padding: 2px 4px;
            text-align: left;
            white-space: nowrap;
        }

        th {
            font-weight: bold;
            background: #f5f5f5;
        }

        a {
            color: #0000ee;
        }
    </style>
</head>

<body>

<table>
"""
        )

    @staticmethod
    def _write_table_header(file):
        file.write(
            """    <thead>
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
"""
        )

    @staticmethod
    def _write_table_row(
        file,
        filename,
        campaign_type,
        count,
    ):
        if (
            campaign_type
            == AdCampaignerConfig.REMARKETING_CAMPAIGN_TYPE
        ):
            feed_url = (
                AdCampaignerConfig
                .get_remarketing_feed_url(
                    filename
                )
            )
        else:
            feed_url = (
                AdCampaignerConfig
                .get_feed_url(
                    filename
                )
            )

        campaign_type = escape(
            str(campaign_type)
        )

        route = escape(
            str(AdCampaignerConfig.ROUTE)
        )

        feed_url = escape(
            feed_url,
            quote=True,
        )

        feed_filename = escape(
            filename
        )

        location_names = escape(
            str(
                AdCampaignerConfig
                .LOCATION_NAMES
            )
        )

        count = escape(
            str(count)
        )

        status = escape(
            str(
                AdCampaignerConfig.STATUS
            )
        )

        file.write(
            f"""        <tr>
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

    @staticmethod
    def _write_html_end(file):
        file.write(
            """    </tbody>
</table>

</body>
</html>
"""
        )