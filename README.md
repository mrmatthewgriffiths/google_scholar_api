# Google Scholar API Playgroud 

## Introduction

This packages is designed to allow you to query the google scholar api for a list of authors and to organise their listed publications into two buckets:

- Bucket 1: Where they are *very likley* to the be the PI supporting either PhD or MSc Student(s) 
    - In this case they are listed as the last author on the paper
- Bucket 2: Where they are *very likley* to be the lead researcher on the paper (ie. this is their work)
    - In this case they are lsited as the first autheor on the paper

## Instructions

### Running the script to pull down articles from Google Scholar by Author

To download the repo from github and run the basic script that goes to Google Scholar and downloads the last 100 articles associated with a list of authors do the following:

> Note that the data files are checked into the repo so you actually don't need to do this, you can just read the files if you like =)

```sh
git clone https://github.com/mrmatthewgriffiths/google_scholar_api.git
cd google_scholar_api
```

Edit the config file adding your SERPAPI api key (sign up for a free account)

```sh
uv sync
uv run scripts/google_scholar_serpapi.py
```

### Reading the data

Usable data in csv format is located in this following directory: 

```sh
./data/out/csv/...
```

- **papers_where_author_is_last.csv** 
    - Containing a list of papers (with titles and links) where the Author is listed last and so *very likley* to be the PI.
- **papers_where_author_is_first.csv**
    - Containing a list of papers where the Autheor is listed first and so *very likley* to be the lead researcher (ie. this is their main area of interest)

## Known issues and limitations

1. You need an API key from SERPAPI 
1. Not a lot of error handling so if you add new google scholar pages to the config list and run the script, you may get errors - sorry =)