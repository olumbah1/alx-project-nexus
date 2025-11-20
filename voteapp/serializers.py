from rest_framework import serializers
from .models import Poll, PollOption, Vote, Category, Campaign, Comment

class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ["id", "text", "order", "vote_count"]

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Poll
        fields = ["id", "title", "description", "campaign",
                  "category", "created_at", "expires_at", "is_active", 
                  "allow_multiple_votes", "options"]

class CreatePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ["title", "description", "campaign", "category", 
                  "expires_at", "is_active", "allow_multiple_votes"]

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "poll", "option", "voter_ip", "voter_user", "voted_at"]
        read_only_fields = ["voter_user", "voter_ip", "voted_at"]

    def validate(self, attrs):
        poll = attrs.get("poll")
        option = attrs.get("option")
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        ip = request.META.get("REMOTE_ADDR") if request else None

        if option.poll_id != poll.id:
            raise serializers.ValidationError("Option does not belong to poll.")

        if not poll.is_active or poll.is_expired:
            raise serializers.ValidationError("Poll is not active.")

        if not poll.allow_multiple_votes:
            if user and Vote.has_voted(poll, voter_user=user):
                raise serializers.ValidationError("User has already voted in this poll.")
            if not user and ip and Vote.has_voted(poll, voter_ip=ip):
                raise serializers.ValidationError("This IP has already voted in this poll.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        ip = request.META.get("REMOTE_ADDR") if request else None
        validated_data["voter_user"] = user
        validated_data["voter_ip"] = None if user else ip

        from django.db import transaction
        from django.db.models import F
        with transaction.atomic():
            vote = Vote.objects.create(**validated_data)
            # update denormalized count
            PollOption.objects.filter(pk=vote.option.pk).update(vote_count=F("vote_count") + 1)
        return vote

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "description", "created_at"]

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ["id", "title", "description", "start_date",
                  "end_date", "is_active", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "poll", "user", "body", "created_at"]