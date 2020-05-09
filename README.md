<div align="center">
  <img alt="Banter.ly Logo" src="assets/logo.png" width="250px">
  <h1><a href="">Banter.ly</a></h1>
</div>

![Python](https://img.shields.io/badge/Python-^3.8-yellow.svg?logo=python&longCache=true&logoColor=white&colorB=3774ac&style=flat-square&colorA=4c566a)
![Dash](https://img.shields.io/badge/Dash-v1.12.0-blue.svg?longCache=true&logo=python&longCache=true&style=flat-square&logoColor=white&colorB=3774ac&colorA=4c566a)

Banter.ly's goal is simply to be _the world's most comprehensive open source chat analytics 🔎 and visualization app 📊_

We want to make it easy and safe for anyone to get the most advanced insights from their text conversations with the click of a button

## Features
Banter.ly currently only supports Whatsapp chat exports - more messengers and formats are on the [roadmap](https://github.com/sahaab-io/banter.ly/projects/2) (feature requests and cool ideas are welcome!)

- Frequency analysis
- Sentiment, emotion, and profanity analysis
- Named entity extraction

## Getting Started

Banter.ly is built on top of [Dash](https://plotly.com/dash/), which provides a fantastic python environment for creating dashboards

### Prerequisites

- [Python](https://www.python.org/downloads/)
- [MongoDB](https://mongodb.com) running locally or one their free hosts

### Running the App

``` bash
# install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# clone this repo and go into it
git clone https://github.com/sahaab-io/banter.ly.git && cd banter.ly

# create and activate the virtualenv + install dependencies
poetry install && poetry update

# run the one-time setup script and download Spacy data
python setup.py && python -m spacy download en_core_web_sm

# start the application
python index.py
```

If you don't wish to use [`Poetry`](https://python-poetry.org/) as your package manager, a `requirements.txt` file **without the dev dependencies** is also included

## Acknowledgements

* Icons made by [Freepik](https://www.flaticon.com/authors/freepik) from [Flaticon](www.flaticon.com) 
* [NRC Emotional Lexicon](https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm)
