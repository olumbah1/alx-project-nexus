# notifications/signals.py
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from django.conf import settings
from .utils import create_notification

# don't import polls.models at top level; get models lazily inside handlers

@receiver(post_save, sender=None)  # we'll attach proper senders at runtime
def poll_created_notify(sender, instance, created, **kwargs):
    # run only for Poll model saves
    Poll = apps.get_model('voteapp', 'Poll')
    if sender is not Poll:
        return
    if created:
        create_notification(
            recipient=instance.created_by,
            actor_user=instance.created_by,
            verb="created a poll",
            target=instance,
            description=instance.description,
            link=f"/polls/{instance.pk}",
            email=False,
        )

@receiver(post_save, sender=None)
def vote_created_notify(sender, instance, created, **kwargs):
    Poll = apps.get_model('voteapp', 'Poll')
    Vote = apps.get_model('voteapp', 'Vote')
    Comment = apps.get_model('voteapp', 'Comment')
    # handle Vote saves
    if sender is Vote and created:
        poll = instance.poll
        voter = instance.voter_user
        if poll.created_by != voter:
            create_notification(
                recipient=poll.created_by,
                actor_user=voter,
                verb="voted on your poll",
                target=poll,
                description=f"{voter} voted on poll '{poll.title}'",
                link=f"/polls/{poll.pk}/results",
                email=False,
            )
    # handle Comment saves
    if sender is Comment and created:
        poll = instance.poll
        create_notification(
            recipient=poll.created_by,
            actor_user=instance.user,
            verb="commented on your poll",
            target=poll,
            description=instance.body[:300],
            link=f"/polls/{poll.pk}",
            email=False,
        )
