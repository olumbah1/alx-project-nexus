# Online Poll & Election System — README
## Project overview

An extensible backend for running polls and elections across organizations (schools, departments, clubs, companies). It provides secure vote capture, campaign and poll management, real-time result aggregation, and APIs for frontend clients. This repository only contains the backend (Django + DRF) and does not include any frontend UI, mobile app, or third-party hosted services.


# What this backend actually does 

This service provides APIs and database models to manage the entire lifecycle of polls and elections:

## Create and manage campaigns (elections)
Administrators can create elections or campaigns, schedule start/end times, attach contestants, and track the campaign status (upcoming, active, ended).

## Manage polls and poll options
Create single-question polls or polls with multiple options. Each poll belongs to a category and (optionally) a campaign, and has an expiry time.

## Vote collection and validation
Accept votes from authenticated users and/or anonymous voters. Prevent duplicate votes using configurable rules: authenticated user votes, IP-based checks, or a supplied voter identifier (e.g., student/employee ID). Transactions are stored reliably and vote counts are updated atomically.

## Real-time results and aggregation
Compute vote counts and option percentages efficiently using DB aggregation. Provide endpoints that return current totals, percentages and ranking for each poll or contestant.

## Comments and lightweight interaction
Allow users to comment on polls to foster discussion (optional, non-blocking to voting).


# Features

Campaign management with scheduling (start/end) and status flags

Poll creation, expiry, and multiple-option support

Category organization for polls & campaigns

Secure voting with duplicate prevention (user, IP, identifier)

Optional anonymous voting (with IP checks)

Denormalized option vote counts + aggregated results endpoint

Comment model and endpoints (read/write)


# API quick reference 
## Accounts endpoints
POST /api/auth/signup/ — register user

POST /api/auth/login/ — obtain JWT tokens

POST /api/auth/reset-password

POST /api/auth/verify/<uuid:uid>/<str:token>/

POST /api/auth/resend-verification/

POST /api/token/refresh/

POST /api/auth/forgot-password/

POST /api/profile/

POST /api/profile/change-password

## Voteapp endpoints
GET  /api/p/categories/ — list categories

POST /api/p/categories/ — create category (auth)

GET /api/p/categories/<uuid:pk>/ - details

GET  /api/p/campaigns/ — list campaigns

POST /api/p/campaigns/ — create campaign (auth)

GET /api/p/campaigns/<uuid:pk>/ - details

GET  /api/p/polls/ — list polls (filter by category/campaign/is_active)

POST /api/p/polls/ — create poll (auth)

GET  /api/p/polls/<uuid:pk>/results/ — poll results (counts & percentages)

POST /api/p/votes/ — cast a vote (auth or anonymous depending on settings)

## Notification endpoints
GET  /api/notifications/ — user notifications (if enabled)



# Data model highlights

CustomUser — UUID primary key user record

Category — groups polls/campaigns (e.g., School, Department)

Campaign — multi-poll elections with schedule & status

Poll — single poll with options, expiry and flags (allow_multiple_votes/is_active)

PollOption — choice tied to a poll; stores vote_count for quick reads

Vote — recorded vote (voter_user or voter_ip) with uniqueness constraints

Comment — user comments on polls


# from voteapp.models import Category, Campaign, Poll, PollOption, Vote, Comment
# create objects as needed using timezone.now() and uuid.uuid4()


# Security & integrity considerations

Duplicate prevention: model-level unique constraints for Vote plus application checks for anonymous IP-based voting.

Atomicity: use DB transactions when creating votes and updating denormalized counts (e.g., F('vote_count') + 1).

Auth: JWT or session-based auth for user actions; endpoints like signup/login must be AllowAny but protected ones use IsAuthenticated.


# Deployment notes

Database: PostgreSQL recommended for production (atomic operations, robust indexing).

Workers: Celery + Redis for background tasks (email, notifications, heavy reports).

Environment: store secrets in .env or environment variables via django-environ.

CORS: configure django-cors-headers for frontend domains.

Installation
# create venv
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# set env vars (or create .env)
# SECRET_KEY, DATABASE_URL, DEBUG, etc.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

