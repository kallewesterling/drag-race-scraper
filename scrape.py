import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from IPython.display import clear_output

from utils import download_pages, get_html_cache, get_output, strip_from_wiki_refs

PAGES = [
    "RuPaul's Drag Race (season 1)",
    "RuPaul's Drag Race (season 2)",
    "RuPaul's Drag Race (season 3)",
    "RuPaul's Drag Race (season 4)",
    "RuPaul's Drag Race (season 5)",
    "RuPaul's Drag Race (season 6)",
    "RuPaul's Drag Race (season 7)",
    "RuPaul's Drag Race (season 8)",
    "RuPaul's Drag Race (season 9)",
    "RuPaul's Drag Race (season 10)",
    "RuPaul's Drag Race (season 11)",
    "RuPaul's Drag Race (season 12)",
    "RuPaul's Drag Race (season 13)",
    "RuPaul's Drag Race (season 14)",
    "RuPaul's Drag Race (season 15)",
    "RuPaul's Drag Race (season 16)",
    "RuPaul's Drag Race All Stars (season 1)",
    "RuPaul's Drag Race All Stars (season 2)",
    "RuPaul's Drag Race All Stars (season 3)",
    "RuPaul's Drag Race All Stars (season 4)",
    "RuPaul's Drag Race All Stars (season 5)",
    "RuPaul's Drag Race All Stars (season 6)",
    "RuPaul's Drag Race All Stars (season 7)",
    "RuPaul's Drag Race All Stars (season 8)",
    "RuPaul's Drag Race All Stars (season 9)",
    "RuPaul's Drag Race UK (series 1)",
    "RuPaul's Drag Race UK (series 2)",
    "RuPaul's Drag Race UK (series 3)",
    "RuPaul's Drag Race UK (series 4)",
    "RuPaul's Drag Race UK (series 5)",
    "RuPaul's Drag Race UK (series 6)",
    "RuPaul's Drag Race Down Under (season 1)",
    "RuPaul's Drag Race Down Under (season 2)",
    "RuPaul's Drag Race Down Under (season 3)",
    "RuPaul's Drag Race: UK vs. the World",
    "RuPaul's Drag Race: UK vs. the World series 2",
    # "The Switch Drag Race (season 1)", # Chile
    # "The Switch Drag Race (season 2)", # Chile
    "Drag Race Thailand (season 1)",  # Thailand
    "Drag Race Thailand (season 2)",  # Thailand
    "Drag Race Thailand (season 3)",  # Thailand
    "Canada's Drag Race (season 1)",  # Canada
    "Canada's Drag Race (season 2)",  # Canada
    "Canada's Drag Race (season 3)",  # Canada
    "Canada's Drag Race (season 4)",  # Canada
    "Drag Race Holland (season 1)",  # Netherlands
    "Drag Race Holland (season 2)",  # Netherlands
    "Drag Race España (season 1)",  # Spain
    "Drag Race España (season 2)",  # Spain
    "Drag Race España (season 3)",  # Spain
    "Drag Race España (season 4)",  # Spain
    "Drag Race Italia (season 1)",  # Italy
    "Drag Race Italia (season 2)",  # Italy
    "Drag Race Italia (season 3)",  # Italy
    "Drag Race France (season 1)",  # France
    "Drag Race France (season 2)",  # France
    "Drag Race France (season 3)",  # France
    "Drag Race Belgique (season 1)",  # Belgium
    "Drag Race Belgique (season 2)",  # Belgium
    "Drag Race Philippines season 1", # Philippines
    "Drag Race Philippines season 2", # Philippines
    "Drag Race Philippines season 3", # Philippines
    "Drag Race México season 1", # Mexico
    "Drag Race México season 2", # Mexico
    "Drag Race Brasil season 1", # Brazil
    "Drag Race Sverige",  # Sweden
    "Drag Race Germany", # Germany
]

# Download pages
download_pages(PAGES)


# Process pages
all_output = []

for page in PAGES:
    clear_output()
    text = get_html_cache(page).read_text()
    sections = text.split('<h2 id="')

    contestants = pd.DataFrame()
    contestant_progress = None
    episodes = []
    ratings = None
    guest_judges = None
    lipsyncs = None
    infobox = None
    for ix, section in enumerate(sections):
        if ix == 0:
            print(f"[INFO] Processing first section for {page}")
            soup = BeautifulSoup(section, "lxml")
            if soup.find("table", {"class": "infobox"}):
                infobox_elem = soup.find("table", {"class": "infobox"})
                infobox = dict(
                    zip(
                        [
                            x.text
                            for x in infobox_elem.find_all(
                                "th", {"class": "infobox-label"}
                            )
                        ],
                        [
                            x.text.strip().split("\n")
                            for x in infobox_elem.find_all(
                                "td", {"class": "infobox-data"}
                            )
                        ],
                    )
                )
                infobox = {k: v[0] if len(v) == 1 else v for k, v in infobox.items()}
                infobox = {
                    k: v.replace("\xa0", " ") if isinstance(v, str) else v
                    for k, v in infobox.items()
                }

                try:
                    infobox["release_dates"] = re.findall(
                        r"\d{4}-\d{2}-\d{2}", infobox["Original release"]
                    )
                except KeyError:
                    infobox["release_dates"] = []
            continue

        end = section.find('">')
        section_title = section[0:end]

        soup = BeautifulSoup(section, "lxml")
        has_table = soup.find("table", {"class": "wikitable"})
        if not has_table:
            skip_cols = ["references", "external_links", "see_also"]

            if section_title.lower() in skip_cols:
                continue

            print(f"[INFO] Processing sections without tables for {page}")
            if "guest_judges" in section_title.lower():
                guest_judges = [
                    strip_from_wiki_refs(x.text)
                    for x in soup.find_all("li")
                    if x.parent == soup.find_all("ul")[0]
                ]
                continue

            if not section_title.lower() in skip_cols:
                # print(f"{page} {section_title} has no table!")
                continue

        tables = soup.find_all("table", {"class": "wikitable"})
        if "contestant" in section_title.lower():
            print(f"[INFO] Processing contestants for {page}")
            # html__ = str(tables[0])
            try:
                html_table = pd.read_html(str(tables[0]).replace("”", '"'))[0]
            except ValueError as e:
                raise ValueError(e)
            df = pd.DataFrame(html_table)
            if "progress" in section_title.lower():
                df.fillna("", inplace=True)
                df.drop(
                    columns=[col for col in df.columns if "unnamed" in col[1].lower()],
                    inplace=True,
                )
                # contestant_progress = df.copy()
                contestant_progress = {}
                for ix, rows in df.iterrows():
                    contestant = None
                    for ix2, data in rows.items():
                        ix2, ix3 = ix2
                        if ix2 == "Contestant":
                            contestant = data
                            continue
                        if ix2 == "Episode":
                            episode = strip_from_wiki_refs(ix3)

                        if contestant not in contestant_progress:
                            contestant_progress[contestant] = {}

                        contestant_progress[contestant][f"Episode {episode}"] = data
                continue
            else:
                contestants = df.copy()
                # try:
                #     contestants.set_index("Contestant", inplace=True)
                # except KeyError:
                #     try:
                #         contestants.set_index("Contestant[4]", inplace=True)
                #     except KeyError as e:
                #         raise KeyError(e)
                continue

        if "ratings" in section_title.lower():
            print(f"[INFO] Processing ratings for {page}")
            html_table = pd.read_html(str(tables[0]))[0]
            df = pd.DataFrame(html_table)
            df.dropna(inplace=True)
            try:
                df["Episode"] = df["Episode"].astype(int)
                df.set_index("Episode", inplace=True)
            except KeyError:
                try:
                    df["Episode no."] = df["Episode no."].astype(int)
                    df.set_index("Episode no.", inplace=True)
                except KeyError:
                    try:
                        df["No."] = df["No."].astype(int)
                        df.set_index("No.", inplace=True)
                    except KeyError as e:
                        print(df.columns)
                        raise KeyError(e)

            ratings = df
            continue

        if "lip_syncs" in section_title.lower():
            print(f"[INFO] Processing lipsyncs for {page}")

            def join_contestants(row, contestants_cols):
                val = []
                for col in contestants_cols:
                    if not row[col] or isinstance(row[col], type(np.nan)):
                        continue

                    if row[col].strip().strip(".") != "vs":
                        val.append(row[col])

                val = [y for x in val for y in x.split(" vs. ")]
                val = sorted(list(set(val)))
                return val

            df = pd.DataFrame(pd.read_html(str(tables[0]))[0]).drop_duplicates()
            df.drop(
                df[df.Episode == "Episode"].index, axis="rows", inplace=True
            ) if "Episode" in df.columns else None

            try:
                df.dropna(subset=["Song", "Eliminated"], inplace=True)
            except KeyError:
                print(f"[WARN] ['Song', 'Eliminated'] not in {df.columns}")
                try:
                    df.dropna(subset=["Song", "Winner"], inplace=True)
                except KeyError:
                    print(f"[WARN] ['Song', 'Winner'] not in {df.columns}")
                    try:
                        df.dropna(subset=["Song", "Winner(s)"], inplace=True)
                    except KeyError:
                        print(f"[WARN] ['Song', 'Winner(s)'] not in {df.columns}")
                        try:
                            df.dropna(
                                subset=["Song", "Eliminated(Team mates)"], inplace=True
                            )
                        except KeyError:
                            print(
                                f"[WARN] ['Song', 'Elimited(Team mates)'] not in {df.columns}"
                            )
                            try:
                                df.dropna(
                                    subset=["Song or Media", "Winner"], inplace=True
                                )
                            except KeyError:
                                print(
                                    f"[WARN] ['Song or Media', 'Winner'] not in {df.columns}"
                                )
                                pass
                                # raise KeyError(e)

            contestants_cols = (
                [col for col in df.columns if "Contestants" in col]
                + [col for col in df.columns if "Lip syncers" in col]
                + [
                    col
                    for col in df.columns
                    if "Top All Star" in col or "Lip Sync Assassin" in col
                ]
            )
            df__ = df.copy()
            if len(contestants_cols) > 1:
                df["Contestants_fixed"] = df.apply(
                    join_contestants, contestants_cols=contestants_cols, axis=1
                )
            df.drop(columns=contestants_cols, inplace=True)
            df.rename(
                {"Contestants_fixed": "Contestants"}, inplace=True, axis="columns"
            )

            lipsyncs = df.copy()
            continue

        if "episodes" in section_title.lower():
            print(f"[INFO] Processing episodes for {page}")
            table = tables[0]
            saved = table

            categories = [
                re.sub(
                    r"\s+",
                    " ",
                    " ".join([strip_from_wiki_refs(x.text) for x in tag.contents]),
                )
                for tag in table.find_all("tr")[0].find_all("th")
            ]

            lst = table.find_all("tr")[1:]
            lst = [lst[n : n + 2] for n in range(0, len(lst), 2)]

            for x in lst:
                soup = BeautifulSoup(str(x[0]) + str(x[1]), "lxml")
                content = soup.find_all("th") + soup.find_all("td")

                if len(content) == len(categories) + 1:
                    metadata = dict(
                        zip(
                            categories,
                            [
                                unicodedata.normalize(
                                    "NFKD", str(strip_from_wiki_refs(x.text))
                                )
                                for x in content[:4]
                            ],
                        )
                    )
                    description = content[-1]  # assume last one is the desc

                    uls = description.find_all("ul")
                    uls = [ul for ul in uls if ul.parent == description]
                    if len(uls) > 1:
                        ul = uls[-1]
                    elif len(uls) == 1:
                        ul = uls[0]
                    else:
                        ul = None

                    if ul:
                        # we have a list!
                        lst = ul.find_all("li")
                        lst = [li for li in lst if li.parent == ul]

                        keys, values = [], []
                        for l in lst:
                            key = l.find("b")
                            key = (
                                strip_from_wiki_refs(key.text)
                                .lstrip(":")
                                .rstrip(":")
                                .strip()
                            )
                            value = (
                                strip_from_wiki_refs(l.text)
                                .replace(key, "")
                                .lstrip(":")
                                .rstrip(":")
                                .strip()
                            )
                            keys.append(key)
                            values.append(value)

                        metadata2 = dict(zip(keys, values))

                        metadata.update(metadata2)

                    description = "\n\n".join(
                        [
                            strip_from_wiki_refs(x.text)
                            for x in description.find_all("p")
                            if x.parent == description
                        ]
                    )
                    episodes.append({"description": description, "metadata": metadata})
                    continue
                else:
                    print("handle this!")
                    raise RuntimeError()
            continue

        # print(page, section_title)

    print(f"[INFO] Fixing results for {page}")
    for col in contestants.columns:
        contestants[col] = contestants[col].apply(strip_from_wiki_refs)

    if isinstance(ratings, pd.DataFrame):
        for col in ratings.columns:
            ratings[col] = ratings[col].apply(strip_from_wiki_refs)

    if isinstance(lipsyncs, pd.DataFrame):
        for col in lipsyncs.columns:
            lipsyncs[col] = lipsyncs[col].apply(strip_from_wiki_refs)

    summary = {
        "show": page,
        "infobox": infobox,
        "contestants": json.loads(contestants.to_json(orient="index")),
        "contestant_progress": contestant_progress,
        "episodes": episodes,
        "ratings": json.loads(ratings.to_json(orient="index"))
        if isinstance(ratings, pd.DataFrame)
        else None,
        "guest_judges": guest_judges,
        "lipsyncs": json.loads(lipsyncs.to_json(orient="records"))
        if isinstance(lipsyncs, pd.DataFrame)
        else None,
    }

    output = get_output(page)
    output.write_text(json.dumps(summary))

    all_output.append(summary)

Path("./output").mkdir(parents=True, exist_ok=True)
Path("./output/all_shows.json").write_text(json.dumps(all_output))
