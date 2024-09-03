from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Player(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    nickname = models.CharField(max_length=50)
    first_enterance = models.DateTimeField(auto_now_add=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nickname

    def add_points(self, points_amount: int):
        self.points += points_amount
        self.save()


class Boost(models.Model):
    BOOST_CHOICE = (
        ('double', 'Удвоить сегодняшние очки'),
        ('freeze', 'Заморозить стрик'),
        ('extra_points', 'Увеличить колличество очков в день')
    )

    boost_type = models.CharField(max_length=50, choices=BOOST_CHOICE)

    def __str__(self):
        return self.boost_type
    

class PlayerBoost(models.Model):
    '''Модель PlayerBoost связывает игрока с его бустами'''

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='boosts'
    )
    boost = models.ForeignKey(
        Boost,
        on_delete=models.CASCADE,
        related_name='players'
    )

    quantity = models.PositiveIntegerField(default=1)
