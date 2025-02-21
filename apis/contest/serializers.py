from rest_framework import serializers

from apis.contest.models import Competition, PlayerEntry


class CompetitionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    entry_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    max_players = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    created_by = serializers.CharField(required=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        return data

    class Meta:
        model = Competition
        fields = '__all__'


class PlayerEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = PlayerEntry
        fields = '__all__'
