from __future__ import print_function
import urllib2, os, sys, time
from datetime import datetime
import feedparser

def get_playlist_id(webcast_url):
    return webcast_url.split("#")[1].split(",")[-1]

def get_yt_url(webcast_url):
    """
        Returns the full url to the YT Atom feed, given the webcast url
    """
    playlist_id = get_playlist_id(webcast_url)
    return "http://gdata.youtube.com/feeds/api/playlists/%s" % playlist_id

def fetch_feed(webcast_url):
    """
        Returns the feedparser representation of the Atom feed.
    """
    yt_url = get_yt_url(webcast_url)

    try:
        response = urllib2.urlopen(yt_url)
    except urllib2.HTTPError as e:
        print("Failed to fetch Atom feed; error was:")
        print(e)
        return False

    return feedparser.parse(response.read())

def get_cache_path(playlist_id):
    return os.path.join(os.path.dirname(__file__), ".%s" % playlist_id)

def get_last_updated_time(webcast_url):
    pl_id = get_playlist_id(webcast_url)
    path = get_cache_path(pl_id)

    if not os.path.exists(path):
        return datetime.min

    with open(path) as f:
        ts = datetime.fromtimestamp(float(f.read()))
    return ts

def update_cache_time(webcast_url):
    pl_id = get_playlist_id(webcast_url)
    path = get_cache_path(pl_id)

    with open(path, "w") as f:
        f.write(str(time.time()))


def check_new(webcast_url):
    feed = fetch_feed(webcast_url)

    last_updated = get_last_updated_time(webcast_url)
    num_new = 0

    for entry in feed.entries:
        if datetime.fromtimestamp(time.mktime(entry.updated_parsed)) > last_updated:
            num_new += 1

    if num_new > 0:
        print("%s new ones!" % num_new)

    update_cache_time(webcast_url)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Provide the url to the webcast.")
    else:
        check_new(sys.argv[1])