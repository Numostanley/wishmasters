from django.urls import path

from . import views

urlpatterns = [
    path('create', views.CompetitionCreateView.as_view(), name='create_competition'),
    path('join/<str:competition_id>', views.JoinCompetitionView.as_view(), name='join_competition'),
    path('submit/<str:entry_id>', views.SubmitScoreView.as_view(), name='submit_score'),
    path('leaderboard/<str:competition_id>', views.LeaderboardView.as_view(), name='leaderboard'),
    path('get', views.CompetitionsAPIView.as_view(), name='get_competitions'),
    path('entry/<str:competition_id>', views.CompetitionEntryAPIView.as_view(), name='entry_competition'),

]
