from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from .models import Poll, PollOption, Vote, Category, Campaign
from .serializers import (
    PollSerializer, CreatePollSerializer, VoteSerializer, 
    CategorySerializer, CampaignSerializer
)
from .pagination import StandardResultsSetPagination, LargeResultsSetPagination
from .cache_utils import cache_response, invalidate_cache_pattern
import logging

logger = logging.getLogger('voteapp')

class PollListCreateView(generics.ListCreateAPIView):
    queryset = Poll.objects.select_related('category', 'campaign', 'created_by').prefetch_related('options').all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "campaign", "is_active"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePollSerializer
        return PollSerializer

    @method_decorator(cache_page(settings.CACHE_TTL.get('polls_list', 300)))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            poll = serializer.save(created_by=self.request.user)
            logger.info(f"Poll created: {poll.title} by user {self.request.user.username}")
            invalidate_cache_pattern('polls')
        except Exception as e:
            logger.error(f"Error creating poll: {str(e)}", exc_info=True)
            raise


class PollDetailView(generics.RetrieveAPIView):
    queryset = Poll.objects.select_related('category', 'campaign', 'created_by').prefetch_related('options__votes').all()
    serializer_class = PollSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        # Create cache key
        cache_key = f"poll_detail_{kwargs.get('pk')}"
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get fresh data
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Cache the response
        cache.set(
            cache_key, 
            serializer.data, 
            settings.CACHE_TTL.get('poll_detail', 600)
        )
        
        return Response(serializer.data)


class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        try:
            vote = serializer.save()
            poll_id = vote.poll_option.poll.id
            logger.info(f"Vote recorded for poll {poll_id}")
            
            # Invalidate caches
            cache.delete(f"poll_detail_{poll_id}")
            cache.delete(f"poll_results_{poll_id}")
            invalidate_cache_pattern(f'polls')
        except Exception as e:
            logger.error(f"Error recording vote: {str(e)}", exc_info=True)
            raise


class PollResultsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        # Create cache key
        cache_key = f"poll_results_{pk}"
        
        # Try to get from cache
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(cached_results)
        
        # Get fresh results
        try:
            poll = Poll.objects.select_related('category').prefetch_related('options__votes').get(pk=pk)
        except Poll.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        results = poll.get_results()
        
        # Cache the results
        cache.set(
            cache_key, 
            results, 
            settings.CACHE_TTL.get('poll_results', 120)
        )
        
        return Response(results)


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories (cached)
    POST: Create a new category
    """
    queryset = Category.objects.select_related('created_by').all().order_by("-created_at")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    @method_decorator(cache_page(settings.CACHE_TTL.get('categories', 900)))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        # Invalidate categories cache
        invalidate_cache_pattern('categories')


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one category (cached)
    PUT/PATCH: Update category
    DELETE: Delete category
    """
    queryset = Category.objects.select_related('created_by').all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        cache_key = f"category_detail_{kwargs.get('pk')}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, settings.CACHE_TTL.get('categories', 900))
        
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Invalidate cache for this category
        cache.delete(f"category_detail_{instance.pk}")
        invalidate_cache_pattern('categories')

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        cache.delete(f"category_detail_{pk}")
        invalidate_cache_pattern('categories')


class CampaignListCreateView(generics.ListCreateAPIView):
    """
    GET: List all campaigns (cached)
    POST: Create a new campaign
    """
    queryset = Campaign.objects.select_related('created_by').all().order_by("-created_at")
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    @method_decorator(cache_page(settings.CACHE_TTL.get('campaigns', 900)))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        # Invalidate campaigns cache
        invalidate_cache_pattern('campaigns')


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one campaign (cached)
    PUT/PATCH: Update campaign
    DELETE: Delete campaign
    """
    queryset = Campaign.objects.select_related('created_by').all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        cache_key = f"campaign_detail_{kwargs.get('pk')}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, settings.CACHE_TTL.get('campaigns', 900))
        
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f"campaign_detail_{instance.pk}")
        invalidate_cache_pattern('campaigns')

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        cache.delete(f"campaign_detail_{pk}")
        invalidate_cache_pattern('campaigns')