from rest_framework import serializers

from card.models import Card, Model

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'description', 'creation_date', 'last_change_date']
