"""
Module responsible for assembling movie-related information from various IMDb TSV files.
"""
import os
import json
import pandas as pd

DATA_DIR = "data"
IMDB_DIR = "imdb_data"

def select_movies():
    """
    Read the title.basics.tsv file and extract 500 valid movie entries with essential metadata.
    """
    df = pd.read_csv(
        f"{IMDB_DIR}/title.basics.tsv",
        sep="\t",
        na_values="\\N",
        dtype=str,
    )
    valid_movies = df[
        (df["titleType"] == "movie") &
        df["tconst"].notna() &
        df["originalTitle"].notna() &
        df["startYear"].notna() &
        df["runtimeMinutes"].notna() &
        df["genres"].notna()
    ]
    valid_500_movies = valid_movies.iloc[:500]
    valid_500_movies.to_csv(f"{DATA_DIR}/valid_500_movies.csv", index=False)

def extract_locale_info():
    """
    Map movie IDs to their primary language and country using title.akas.tsv.
    """
    movies = pd.read_csv(f"{DATA_DIR}/valid_500_movies.csv")
    movie_ids = set(movies["tconst"])

    language_map = {}
    country_map = {}

    # Memory issues
    chunk_iter = pd.read_csv(
        f"{IMDB_DIR}/title.akas.tsv",
        sep="\t",
        na_values="\\N",
        dtype=str,
        chunksize=100_000
    )

    for chunk in chunk_iter:
        matched = chunk[chunk["titleId"].isin(movie_ids)]
        lang = matched.groupby("titleId")["language"].first().dropna().to_dict()
        country = matched.groupby("titleId")["region"].first().dropna().to_dict()
        language_map.update(lang)
        country_map.update(country)

    with open(f"{DATA_DIR}/language_map.json", "w", encoding="utf-8") as f:
        json.dump(language_map, f, indent=2)
    with open(f"{DATA_DIR}/country_map.json", "w", encoding="utf-8") as f:
        json.dump(country_map, f, indent=2)


def associate_people():
    """
    Link people to movies with their roles and attach names from name.basics.tsv.
    """
    movies = pd.read_csv(f"{DATA_DIR}/valid_500_movies.csv")
    movie_ids = set(movies["tconst"])

    grouped = {}

    # Memory issues
    chunk_iter = pd.read_csv(
        f"{IMDB_DIR}/title.principals.tsv",
        sep="\t",
        na_values="\\N",
        dtype=str,
        chunksize=100_000
    )

    for chunk in chunk_iter:
        relevant = chunk[chunk["tconst"].isin(movie_ids)]
        grouped_chunk = relevant.groupby("tconst")[["nconst", "category", "job"]].apply(
            lambda df: df[df["nconst"].notna() & df["category"].notna()].to_dict(orient="records")
        ).to_dict()
        grouped.update(grouped_chunk)

    name_lookup = {}
    needed_nconsts = set()
    for people in grouped.values():
        for person in people:
            needed_nconsts.add(person["nconst"])

    # Memory issues
    chunk_iter = pd.read_csv(
        f"{IMDB_DIR}/name.basics.tsv",
        sep="\t",
        na_values="\\N",
        dtype=str,
        chunksize=100_000
    )

    for chunk in chunk_iter:
        relevant_names = chunk[chunk["nconst"].isin(needed_nconsts)]
        name_lookup.update(relevant_names.set_index("nconst")["primaryName"].to_dict())

    for people in grouped.values():
        for person in people:
            person["name"] = name_lookup.get(person["nconst"], None)

    with open(f"{DATA_DIR}/movie_people.json", "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=2)


def generate_dataset():
    """
    Merge all information and export the final structured dataset to a JSON file.
    """
    movies = pd.read_csv(f"{DATA_DIR}/valid_500_movies.csv")
    with open(f"{DATA_DIR}/language_map.json", encoding="utf-8") as f:
        languages = json.load(f)
    with open(f"{DATA_DIR}/country_map.json", encoding="utf-8") as f:
        countries = json.load(f)
    with open(f"{DATA_DIR}/movie_people.json", encoding="utf-8") as f:
        people = json.load(f)

    all_genres, langs, regions, unique_people = set(), set(), set(), {}
    full_movie_list = []

    for _, row in movies.iterrows():
        mid = row["tconst"]
        genres = row["genres"].split(",")
        all_genres.update(genres)

        lang = languages.get(mid)
        region = countries.get(mid)
        if lang: langs.add(lang)
        if region: regions.add(region)

        persons = people.get(mid, [])
        for p in persons:
            unique_people[p["nconst"]] = p["name"]

        full_movie_list.append({
            "id": mid,
            "originalTitle": row["originalTitle"],
            "duration": row["runtimeMinutes"],
            "releaseYear": row["startYear"],
            "genres": genres,
            "originalLanguage": lang,
            "originalCountry": region,
            "peopleInvolved": persons
        })

    result = {
        "movies": full_movie_list,
        "genres": list(all_genres),
        "languages": list(langs),
        "countries": list(regions),
        "people": unique_people
    }

    with open("data/movies.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


def main():
    """
    Coordinates the full data processing workflow.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    print("selecting 500 valid movies...")
    select_movies()
    print("extracting language and country data...")
    extract_locale_info()
    print("resolving people and their roles...")
    associate_people()
    print("generating final dataset...")
    generate_dataset()


if __name__ == "__main__":
    main()
