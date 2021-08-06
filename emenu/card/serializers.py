from rest_framework import serializers

from card.models import Card, Dish


class DishSerializer(serializers.HyperlinkedModelSerializer):
    cards = serializers.HyperlinkedRelatedField(
        queryset=Card.objects.all(),
        many=True,
        view_name='card-detail'
    )

    class Meta:
        model = Dish
        fields = [
            'id',
            'url',
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


class DishListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dish
        fields = [
            'id',
            'url',
            'name',
        ]

class CardListSerializer(serializers.HyperlinkedModelSerializer):
    dishes = DishListSerializer(many=True, read_only=True)
    dishes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id',
            'url',
            'name',
            'description',
            'creation_date',
            'last_change_date',
            'dishes',
            'dishes_count',
        ]
        extra_kwargs = {'dishes': {'required': False}}


class CardSerializer(serializers.HyperlinkedModelSerializer):
    dishes = serializers.HyperlinkedRelatedField(
        queryset=Dish.objects.all(),
        many=True,
        view_name='dish-detail',
    )
    dishes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id',
            'url',
            'name',
            'description',
            'creation_date',
            'last_change_date',
            'dishes',
            'dishes_count',
        ]
        extra_kwargs = {'dishes': {'required': False}}


class CardDetailSerializer(serializers.HyperlinkedModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)
    linked_dishes = serializers.HyperlinkedRelatedField(
        queryset=Dish.objects.all(),
        many=True,
        view_name='dish-detail',
        source='dishes',
    )
    dishes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id',
            'url',
            'name',
            'description',
            'creation_date',
            'last_change_date',
            'dishes_count',
            'linked_dishes',
            'dishes',
        ]
        extra_kwargs = {'dishes': {'required': False}}

