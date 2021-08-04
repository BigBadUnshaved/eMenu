from rest_framework import serializers

from card.models import Card, Dish


class DishSerializer(serializers.HyperlinkedModelSerializer):
    cards = serializers.HyperlinkedRelatedField(
        many=True, view_name='card-detail', read_only=True)

    class Meta:
        model = Dish
        fields = [
            'url',
            'id',
            'name',
            'description',
            'creation_date',
            'last_change_date',
            'price',
            'preparation_time',
            'is_vegetarian',
            'cards'
        ]
        extra_kwargs = {'cards': {'required': False}}


class CardSerializer(serializers.HyperlinkedModelSerializer):
    dishes = serializers.HyperlinkedRelatedField(
        many=True, view_name='dish-detail', read_only=True)
    dishes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'url',
            'id',
            'name',
            'description',
            'creation_date',
            'last_change_date',
            'dishes',
            'dishes_count',
        ]
        extra_kwargs = {'dishes': {'required': False}}


