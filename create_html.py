import csv
import sys
from typing import List, Set

from minify_html import minify  # type: ignore # pylint: disable=no-name-in-module


def minify_asset(
    filepath: str, minify_js: bool = False, minify_css: bool = False
) -> None:
    with open(filepath, encoding="utf-8") as f:
        minified = minify(
            f.read(),
            minify_js=minify_js,
            minify_css=minify_css,
            remove_processing_instructions=True,
        )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(minified)


def main() -> None:
    YT_PREFIX = "https://www.youtube.com/watch?v="

    LI_TEMPLATE = (
        '<li><a href="https://youtu.be/{youtube}" class="YT"></a>'
        '<b>{artist}</b> - <i>{album}</i><span class="rating">{rating}/5</span>'
        '<span class="genre">{genre}</span></li>'
    )

    html_albums: List[str] = []
    all_youtubes: Set[str] = set()

    with open("albums.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        prev_rating = 5

        for row in reader:
            try:
                assert len(row) == 5
                assert row["Artist"].strip() != ""
                assert row["Album"].strip() != ""
                assert row["Rating"].strip() != ""
                assert 1 <= float(row["Rating"].strip()) <= 5
                assert float(row["Rating"].strip()) <= prev_rating
                assert row["Genre"].strip() != ""
                assert row["Youtube"].strip() != ""
                assert row["Youtube"].startswith(YT_PREFIX)
                assert row["Youtube"].strip() not in all_youtubes
            except (AssertionError, ValueError):
                print("Error while parsing the following album:")
                print(row)
                sys.exit(1)

            all_youtubes.add(row["Youtube"].strip())
            prev_rating = float(row["Rating"].strip())

            html_albums.append(
                LI_TEMPLATE.format(
                    youtube=row["Youtube"].strip().removeprefix(YT_PREFIX),
                    artist=row["Artist"].strip(),
                    album=row["Album"].strip(),
                    rating=row["Rating"].strip(),
                    genre=row["Genre"].strip(),
                )
            )

    with open("template.html", "r", encoding="utf-8") as fin:
        html_template = fin.read()

    assert html_template.count("<!--PLACEHOLDER_ALBUM_LIST-->") == 1

    with open("index.html", "w", encoding="utf-8") as fout:
        fout.write(
            minify(
                html_template.replace(
                    "<!--PLACEHOLDER_ALBUM_LIST-->", "\n".join(html_albums)
                ),
                minify_js=True,
                minify_css=True,
                remove_processing_instructions=True,
            )
        )

    minify_asset("style.css", minify_css=True)
    minify_asset("main.js", minify_js=True)


if __name__ == "__main__":
    main()
