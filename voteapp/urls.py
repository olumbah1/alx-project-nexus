from django.urls import path
from .views import (PollListCreateView, PollDetailView, VoteCreateView,
                    PollResultsView, CategoryListCreateView, CategoryDetailView,
                    CampaignListCreateView, CampaignDetailView)

urlpatterns = [
    path("polls/", PollListCreateView.as_view(), name="poll-list-create"),
    path("polls/<uuid:pk>/", PollDetailView.as_view(), name="poll-detail"),
    path("polls/<uuid:pk>/results/", PollResultsView.as_view(), name="poll-results"),
    path("votes/", VoteCreateView.as_view(), name="vote-create"),
    
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category-detail"),

    path("campaigns/", CampaignListCreateView.as_view(), name="campaign-list-create"),
    path("campaigns/<uuid:pk>/", CampaignDetailView.as_view(), name="campaign-detail"),

]

