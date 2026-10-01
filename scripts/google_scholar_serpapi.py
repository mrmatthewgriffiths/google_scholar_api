# Add the project root to the path so we can include things from config
import sys
from pathlib import Path
DIR_ROOT = str(Path(__file__).parent.parent.resolve())
sys.path.insert(0, DIR_ROOT)

# Import required packages
import json
import serpapi
import re
import os
import urllib
import csv
from config import API_KEY_SERPAPI, GOOGLE_SCHOLAR_AUTHOR_PAGE_URLS

# Set output directories
DIR_DATA = os.path.join(DIR_ROOT, "data")
DIR_DATA_OUT = os.path.join(DIR_DATA, "out")
DIR_JSON_DATA = os.path.join(DIR_DATA_OUT, "json")
DIR_CSV_DATA = os.path.join(DIR_DATA_OUT, "csv")

# Set up the api client
client = serpapi.Client(api_key=API_KEY_SERPAPI)

# This should be replaced with some kind of file read to get a list of GS author pages
google_scholar_author_page_urls = GOOGLE_SCHOLAR_AUTHOR_PAGE_URLS

# Extract the author id from each url
data = {}
for url in google_scholar_author_page_urls:
    parsed = urllib.parse.urlsplit(url)
    user_id = urllib.parse.parse_qs(parsed.query)['user'][0]
    data[user_id] = {
        "author_url": url
    }

# Check for existing json data
json_data_files = [
    f for f 
    in os.listdir(DIR_JSON_DATA) 
    if os.path.isfile(os.path.join(DIR_JSON_DATA, f)) and ".json" in f]

for json_data_file in json_data_files:
    author_id = json_data_file.replace(".json", "")
    print(f"Loading JSON data for author_id: {author_id}")
    if author_id in data:
        with open(os.path.join(DIR_JSON_DATA, json_data_file), "r") as f:
            data[author_id]["json_data"] = json.load(f)


# For all author_ids without json data
for author_id, d in data.items():
    if not d.get("json_data"):
        try:
            # Call the api client to download the data
            print(f"Calling API for author_id: {author_id}")
            results = client.search({
                "engine": "google_scholar_author",
                "author_id": author_id,
                "sort": "pubdate",
                "num": "100"
            }).as_dict()

            # Extract some basic details about the author
            author_name = results["author"]["name"]
            author_name_for_regex = author_name.split(" ")[-1].lower().strip()
            author_name_regex = f"(?i){author_name_for_regex}"

            # Cycle through their articles and note if they are the first or last author
            for article in results["articles"]:
                authors = article["authors"]
                authors_list = authors.split(",")
                author_position = "middle"
                if re.search(author_name_regex, authors_list[0]):
                    author_position = "first"
                elif re.search(author_name_regex, authors_list[-1]):
                    author_position = "last"
                article["author_position"] = author_position

            # Save the data to a data object
            data[author_id]["json_data"] = results

        except:
            print(f"ERROR - CAN NOT GET API DATA FOR AUTHOR ID: {author_id}")


# Filter out any failed author IDs
data = {author_id: d for author_id, d in data.items() if d.get("json_data")}

# Write out the json data files
for author_id, d in data.items():
    print(f"Saving JSON for author_id: {author_id}")
    author_json_data_file_path = os.path.join(DIR_JSON_DATA, f"{author_id}.json")
    with open(author_json_data_file_path, "w") as f:
        json.dump(d["json_data"], f, indent=4)

# Write out the csv data files
csv_data_authors = [
    ["Name", "Website", "Interests", "Link"],
]

csv_data_papers_where_author_is_last = [
    ["Author", "Year", "Authors", "Title", "Link"],
]

csv_data_papers_where_author_is_first = [
    ["Author", "Year", "Authors", "Title", "Link"],
]

for author_id, author_details in data.items():
    author_obj = author_details["json_data"]["author"]
    csv_data_authors.append([
        author_obj["name"],
        author_obj.get("website"),
        ", ".join([_.get("title") for _ in author_obj.get("interests", []) if _]),
        f"https://scholar.google.com/citations?user={author_id}&hl=en"
    ])

    articles_obj = author_details["json_data"]["articles"]
    for article in articles_obj:
        if article.get("author_position") == "last":
            csv_data_papers_where_author_is_last.append([
                author_obj["name"],
                article["year"],
                article["authors"],
                article["title"],
                article["link"]
            ])
        if article.get("author_position") == "first":
            csv_data_papers_where_author_is_first.append([
                author_obj["name"],
                article["year"],
                article["authors"],
                article["title"],
                article["link"]
            ])

csv_data_authors_file_name = os.path.join(DIR_CSV_DATA, "authors.csv")
with open(csv_data_authors_file_name, "w") as f:
    writer = csv.writer(f)
    writer.writerows(csv_data_authors)

csv_data_papers_where_author_is_last_file_name = os.path.join(DIR_CSV_DATA, "papers_where_author_is_last.csv")
with open(csv_data_papers_where_author_is_last_file_name, "w") as f:
    writer = csv.writer(f)
    writer.writerows(csv_data_papers_where_author_is_last)

csv_data_papers_where_author_is_first_file_name = os.path.join(DIR_CSV_DATA, "papers_where_author_is_first.csv")
with open(csv_data_papers_where_author_is_first_file_name, "w") as f:
    writer = csv.writer(f)
    writer.writerows(csv_data_papers_where_author_is_first)
    