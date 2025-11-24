from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Poll, PollOption, Vote, Category, Campaign
from .serializers import PollSerializer, CreatePollSerializer, VoteSerializer, CategorySerializer, CampaignSerializer

class PollListCreateView(generics.ListCreateAPIView):
    queryset = Poll.objects.all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "campaign", "is_active"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePollSerializer
        return PollSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PollDetailView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.AllowAny]

class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.AllowAny]  # allow anonymous voting if you collected IP

class PollResultsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(poll.get_results())
    

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories
    POST: Create a new category
    """
    queryset = Category.objects.all().order_by("-created_at")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one category
    PUT/PATCH: Update category
    DELETE: Delete category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CampaignListCreateView(generics.ListCreateAPIView):
    """
    GET: List all campaigns
    POST: Create a new campaign
    """
    queryset = Campaign.objects.all().order_by("-created_at")
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one campaign
    PUT/PATCH: Update campaign
    DELETE: Delete campaign
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
