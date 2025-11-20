import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    allow_multiple_votes = models.BooleanField(default=False)

    class Meta:
        db_table = 'polls'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active', 'expires_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def total_votes(self):
        return self.votes.count()   # note: Vote now has poll FK (see below)

    def get_results(self):
        from django.db.models import Count
        results = self.options.annotate(vote_count=Count('votes')).values('id', 'text', 'vote_count')
        total = sum(r['vote_count'] for r in results)
        return {
            'poll_id': str(self.id),
            'title': self.title,
            'total_votes': total,
            'options': [
                {
                    'id': r['id'],
                    'text': r['text'],
                    'votes': r['vote_count'],
                    'percentage': round((r['vote_count'] / total * 100), 2) if total > 0 else 0
                }
                for r in results
            ]
        }


class PollOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # optional
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'poll_options'
        ordering = ['order', 'id']
        unique_together = ['poll', 'text']
        indexes = [
            models.Index(fields=['poll', 'order']),
        ]

    def __str__(self):
        return f"{self.poll.title} - {self.text}"

    @property
    def vote_count(self):
        return self.votes.count()


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')          # ADDED
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    voter_ip = models.GenericIPAddressField(null=True, blank=True)                         # MAKE OPTIONAL
    voter_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='votes'
    )
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        indexes = [
            models.Index(fields=['poll', 'option']),
            models.Index(fields=['poll', 'voter_ip']),
            models.Index(fields=['poll', 'voter_user']),
            models.Index(fields=['-voted_at']),
        ]
        # Enforce single vote per poll per authenticated user
        constraints = [
            models.UniqueConstraint(
                fields=['poll', 'voter_user'],
                condition=models.Q(voter_user__isnull=False),
                name='unique_user_vote_per_poll'
            ),
            # Enforce single vote per poll per IP for anonymous voters
            models.UniqueConstraint(
                fields=['poll', 'voter_ip'],
                condition=models.Q(voter_user__isnull=True),
                name='unique_ip_vote_per_poll'
            ),
        ]

    def __str__(self):
        return f"Vote for {self.option.text}"

    @classmethod
    def has_voted(cls, poll, voter_ip=None, voter_user=None):
        qs = cls.objects.filter(poll=poll)
        if voter_user:
            return qs.filter(voter_user=voter_user).exists()
        if voter_ip:
            return qs.filter(voter_ip=voter_ip).exists()
        return False

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("created_by", "title")  # each user can reuse title but avoid dupes if desired

class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)