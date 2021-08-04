from rest_framework import serializers

from card.models import Card, Dish


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = [
            'id', 'description', 'creation_date', 'last_change_date',
            'price', 'preparation_time', 'is_vegetarian', 'cards'
        ]
        extra_kwargs = {'cards': {'required': False}}


class CardSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'description', 'creation_date', 'last_change_date', 'dishes'
        ]
        extra_kwargs = {'dishes': {'required': False}}


