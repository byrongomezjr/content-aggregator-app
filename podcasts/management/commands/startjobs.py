# Standard Library
import logging
import sched

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Third Party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from pytz import timezone

# Models
from podcasts.models import Episode

logger = logging.getLogger(__name__)


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


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            fetch_planet_money_episodes,
            trigger="interval",
            minutes=2,
            id="Planet Money Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added Job: Planet Money Podcast")

        scheduler.add_job(
            fetch_the_indicator_episodes,
            trigger="interval",
            minutes=2,
            id="The Real Indicator Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added Job: Talk Python Feed")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added Weekly Job: Delete Old Job Executions.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
