import datetime

from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat, Cast
from django.utils import timezone
from rest_framework import permissions, views, response, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.throttling import SimpleRateThrottle

from .models import Competition, PlayerEntry
from .serializers import CompetitionSerializer, PlayerEntrySerializer
from ..helpers.pagination import StandardResultsSetPagination


class ContestThrottle(SimpleRateThrottle):
    scope = "contest"

    def get_cache_key(self, request, view):
        return f"throttle_contest_{request.user.id}"


class CompetitionCreateView(views.APIView, StandardResultsSetPagination):
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                data = self.serializer_class(data=request.data)
                data.is_valid(raise_exception=True)
            except ValidationError as e:
                raise serializers.ValidationError({
                    "status": False,
                    "message": str(e.__str__()),
                })

            try:
                competition = Competition(**data.validated_data)
                competition.save()
                data = CompetitionSerializer(competition).data

                domain = get_current_site(self.request).domain
                http_scheme = self.request.scheme
                base_url = f"{http_scheme}://{domain}"

                if data["image"]:
                    data["image"] = base_url + data["image"]

                response_data = {
                    "status": True,
                    "message": "Contest created",
                    "data": data,
                }
                return response.Response(response_data)
            except Exception as e:
                return response.Response({
                    "status": False,
                    "message": str(e.__str__()),
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JoinCompetitionView(views.APIView):
    serializer_class = PlayerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ContestThrottle]
    throttle_scope = "contest"

    def post(self, request, competition_id):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return response.Response({
                "status": False,
                "message": "You are not allowed to join this contest.",
            }, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            try:
                data = self.request.data
                paid_entry_fee: bool = bool(data["paid_entry_fee"])
                payment_reference =data["payment_reference"]
            except KeyError as e:
                return response.Response({
                    "status": False,
                    "message": f"{e} is required",
                }, status=status.HTTP_400_BAD_REQUEST)

            if not Competition.objects.filter(id=competition_id).exists():
                return response.Response({
                    "status": False,
                    "message": f"{competition_id} does not exist",
                }, status=status.HTTP_404_NOT_FOUND)

            if not paid_entry_fee:
                return response.Response({
                    "status": False,
                    "message": "Please provide paid entry fee for this competition",
                })
            try:
                competition = Competition.objects.get(id=competition_id)
                if competition.end_date < datetime.datetime.now().date():
                    return response.Response({
                        "status": False,
                        "message": f"Competition: {competition_id}, has expired",
                    }, status=status.HTTP_400_BAD_REQUEST)

                if PlayerEntry.objects.filter(competition=competition).count() == competition.max_players:
                    return response.Response({
                        "status": False,
                        "message": f"Maximum number of players allowed for competition has been reached: {competition.max_players}",
                    }, status=status.HTTP_400_BAD_REQUEST)

                entry = PlayerEntry.objects.create(
                    user=user,
                    competition=competition,
                    payment_reference=payment_reference,
                    paid_entry_fee=paid_entry_fee,
                )
                entry.save()
                response_data = {
                    "status": True,
                    "message": "Joined competition",
                    "data": PlayerEntrySerializer(entry).data
                }
                return response.Response(response_data)
            except Exception as e:
                return response.Response({
                    "status": False,
                    "message": str(e),
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitScoreView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, entry_id):
        try:
            entry = PlayerEntry.objects.get(id=entry_id)
        except PlayerEntry.DoesNotExist:
            raise serializers.ValidationError({
                "status": False,
                "message": "No entry with that ID.",
            })
        try:
            data = self.request.data
            score_entry = int(data["score_entry"])
        except KeyError as e:
            return response.Response({
                "status": False,
                "message": f"{e} is required",
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return response.Response({
                "status": False,
                "message": f"invalid value: {e}",
            }, status=status.HTTP_400_BAD_REQUEST)

        if entry.submitted_at:
            return response.Response({
                "status": False,
                "message": "You have already submitted this entry",
            }, status=status.HTTP_400_BAD_REQUEST)

        total_score = abs(score_entry - 0)
        entry.score = total_score
        entry.submitted_at = timezone.now()
        entry.save()
        response_data = {
            "status": True,
            "message": "Score submitted.",
        }
        return response.Response(response_data)


class LeaderboardView(views.APIView):

    @staticmethod
    def get(request, competition_id):
        top_scores = PlayerEntry.objects.filter(competition_id=competition_id).order_by('-score')[:10]
        data = [{"user": score.user.get_full_name(), "score": score.score} for score in top_scores]
        return response.Response({
            "status": True,
            "message": "Scores retrieved successfully",
            "data": data,
        })


class CompetitionsAPIView(views.APIView, StandardResultsSetPagination):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        competition_id = self.request.query_params.get("competition_id")
        active = bool(self.request.query_params.get("active", True))

        domain = get_current_site(self.request).domain
        http_scheme = self.request.scheme
        base_url = f"{http_scheme}://{domain}/media/"

        if competition_id:
            competition = Competition.objects.get(id=competition_id)
            data = CompetitionSerializer(competition).data

            base_url = f"{http_scheme}://{domain}"

            if data["image"]:
                data["image"] = base_url + data["image"]

            response_data = {
                "status": True,
                "message": "Success",
                "data": data,
            }
            return response.Response(response_data)

        if not active:
            competitions = Competition.objects.filter(end_date__lt=timezone.now())

            data = competitions.annotate(
                image_url=Concat(
                    Value(base_url),
                    Cast(F('image'), CharField()),  # Convert ImageField to CharField
                    output_field=CharField()
                )
            ).values()
            results = self.paginate_queryset(data, request, view=self)
            return self.get_paginated_response(results)

        else:
            competitions = Competition.objects.filter(end_date__gt=timezone.now())

            data = competitions.annotate(
                image_url=Concat(
                    Value(base_url),
                    Cast(F('image'), CharField()),  # Convert ImageField to CharField
                    output_field=CharField()
                )
            ).values()
            results = self.paginate_queryset(data, request, view=self)
            return self.get_paginated_response(results)


class CompetitionEntryAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, competition_id):
        user = self.request.user

        if not Competition.objects.filter(id=competition_id).exists():
            return response.Response({
                "status": False,
                "message": "No competition with this ID.",
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            entry = PlayerEntry.objects.get(competition_id=competition_id, user=user)
        except PlayerEntry.DoesNotExist:
            return response.Response({
                "status": False,
                "message": "No entry for this competition.",
            }, status=status.HTTP_404_NOT_FOUND)

        data = PlayerEntrySerializer(entry).data
        response_data = {
            "status": True,
            "message": "Competition entry retrieved.",
            "data": data,
        }
        return response.Response(response_data)
