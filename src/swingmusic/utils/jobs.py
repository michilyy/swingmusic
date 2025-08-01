"""
Jobs are action which can run in the background and perform housekeeping tasks like,
* reading in all files
* creating track hashes
*

This Class is a singleton and manages all multithreading actions.
It is thread save and enforces a limit on how many tasks can run concurrent.
"""

import gc
from time import time

from swingmusic.lib.mapstuff import (
    map_album_colors,
    map_artist_colors,
    map_favorites,
    map_scrobble_data,
)
from swingmusic.lib.populate import CordinateMedia
from swingmusic.lib.recipes.recents import RecentlyAdded
from swingmusic.lib.tagger import IndexTracks
from swingmusic.store.albums import AlbumStore
from swingmusic.store.artists import ArtistStore
from swingmusic.store.folder import FolderStore
from swingmusic.store.tracks import TrackStore
from swingmusic.utils.threading import background
import logging

log = logging.getLogger("swingmusic")

# Job class.
# function for registering jobs - maybe like flask or with a decorator.
# function for stating jobs.
# config for amount limit concurrent jobs.
# multithreading support.
# api access.
# code access.
# maybe with lock file for global data.
# keep in mind that Python still has the GIL .


class Job:

    def __init__(self, independent=False):
        """

        :param independent: If function only accesses
        """

    def start(self, *args, **kwargs):
        raise NotImplementedError("start is not implemented of job")


class JobManager:

    def launch(self, job:Job):
        # Make really multithreaded.
        # Don't forget the GIL
        job.start()


class Index(Job):


    def __init__(self):
        pass

    def start(self):
        IndexTracks()

        key = str(time())
        TrackStore.load_all_tracks(key)
        AlbumStore.load_albums(key)
        ArtistStore.load_artists(key)
        FolderStore.load_filepaths()

        # NOTE: Rebuild recently added items on the homepage store
        RecentlyAdded()

        # map colors
        map_album_colors()
        map_artist_colors()

        map_scrobble_data()
        map_favorites()

        CordinateMedia(instance_key=str(time()))
        gc.collect()
        log.info("Indexing completed")
