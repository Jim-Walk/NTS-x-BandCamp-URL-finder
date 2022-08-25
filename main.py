import requests
import argparse
from bs4 import BeautifulSoup as bs
from rich.console import Console
from rich.table import Table
from rich.progress import track as progress_tracker


def tracklist(url: str) -> list:
    '''
    Args: url - direct url to NTS episode
    Returns: a list of (Track Name, Track Artist) tuples
    '''
    rtr = []
    soup = bs(requests.get(url).content, "html.parser")
    tracks = soup.select('.track')
    for track in tracks:
        rtr += [
            (f"{track.select('.track__artist')[0].get_text()}",
             f"{track.select('.track__title')[0].get_text()}")
            ]
    return rtr


def get_bandcamp_url(artist: str, title: str) -> str:
    bc_search_url = 'http://bandcamp.com/search?q=' \
                    + artist.replace(' ', '+') \
                    + '+' + title.replace(' ', '+') + '&item_type='
    soup = bs(requests.get(bc_search_url).content, "html.parser")
    # results = soup.select('result-info')
    try:
        result = soup.find("div", class_="itemurl")
        href = result.find('a')
        return href.string
    except AttributeError:
        return '-'


def main():
    parser = argparse.ArgumentParser(
                        description='Gets bandcamp urls from NTS shows')
    parser.add_argument('url', type=str,
                        help='NTS episode url')
    args = parser.parse_args()
    url = args.url
    tracks = tracklist(url)
    table = Table()
    table.add_column("Title", style="green", no_wrap=True)
    table.add_column("Artist", style="magenta")
    table.add_column("Bandcamp URL", justify="right", style="cyan")
    for track in progress_tracker(tracks, description='Getting URLs...'):
        artist, title = track
        bc_url = get_bandcamp_url(artist, title)
        table.add_row(title, artist, bc_url)

    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
