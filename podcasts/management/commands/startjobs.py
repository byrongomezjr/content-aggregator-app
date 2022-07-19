from django.core.management.base import BaseCommand

import feedparser
from dateutil import parser

from podcasts.models import Episode


def save_new_episodes(feed):
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries:
        if not Episode.objects.filter(guid=item.guid).exists():
            episode = Episode(
                title=item.title,
                description=item.description,
                pub_date=parser.parse(item.published),
                link=item.link,
                image=podcast_image,
                podcast_name=podcast_title,
                guid=item.guid,
            )
            episode.save()


def fetch_planet_money_episodes():
    _feed = feedparser.parse("https://feeds.npr.org/510289/podcast.xml")
    save_new_episodes(_feed)


def fetch_the_indicator_episodes():
    _feed = feedparser.parse("https://feeds.npr.org/510325/podcast.xml")
    save_new_episodes(_feed)


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_planet_money_episodes()
        fetch_the_indicator_episodes()
