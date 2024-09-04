import csv

from django.http import HttpResponse
from django.db import models
from django.db.models import Prefetch
from django.utils import timezone


class Player(models.Model):
    player_id = models.CharField(max_length=100)
    
    
class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
        
    
class Prize(models.Model):
    title = models.CharField(max_length=255)
    
    
class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def complete_level(self):
        '''Помечает уровень как пройденный и дает игроку награду, если она существует'''

        if self.is_completed:
            raise ValueError('Уровень уже пройден')
        
        self.is_completed = True
        self.completed = timezone.now()
        self.save()

        prize = LevelPrize.objects.select_related('prize').filter(
            level=self.level
        ).first()

        if not prize:
            raise ValueError('Нет награды за этот уровень')

        LevelPrize.objects.create(
            level=self.level,
            prize=prize.prize,
            received=timezone.now()
        )

        return f'Игрок {self.player.player_id} прошел уровень {self.level.title} и получил в награду {prize.prize.title}'
    
    @staticmethod
    def export_to_csv():
        '''
        Метод выгрузки данных в csv 
        путь в браузере /csv
        2 запроса в бд
        '''
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="player_levels.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Id игрока',
            'Название уровня',
            'Уровень пройден',
            'Награда'
        ])

        queryset = PlayerLevel.objects.select_related(
            'player', 'level'
        ).prefetch_related(
            Prefetch('level__levelprize_set', queryset=LevelPrize.objects.select_related('prize'))
        ).all()
        
        for player_level in queryset:
            level_prize = player_level.level.levelprize_set.all()
            prize = level_prize[0].prize.title if level_prize else 'Нет награды'

            writer.writerow([
                player_level.player.player_id,
                player_level.level.title,
                player_level.is_completed,
                prize
            ])

        return response

class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField(null=True)