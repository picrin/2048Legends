from django.db import models

class Person(models.Model):
    login          = models.CharField(max_length=16)
    hashedPassword = models.CharField(max_length=64)
    salt           = models.CharField(max_length=64)
    currentGame    = models.ForeignKey('Game', null=True, blank=True)
    def __unicode__(self):
        return str(self.login)

class Tokena(models.Model):
    value      = models.CharField(max_length=64)
    active     = models.BooleanField()
    created    = models.DateTimeField()
    belongs_to = models.ForeignKey(Person)
    def __unicode__(self):
        return str(self.value)

class Game(models.Model):
    belongs_to = models.ForeignKey(Person)
    gameID     = models.CharField(max_length=64)
    latestMove = models.ForeignKey('Move', null=True, blank=True)

class Move(models.Model):
    moveID             = models.CharField(max_length=64)
    belongs_to         = models.ForeignKey(Game)
    moveNumber         = models.BigIntegerField()
    board              = models.CharField(max_length=200)
    serverSecret       = models.CharField(max_length=64)
    serverSecretHashed = models.CharField(max_length=64)
    clientSecret       = models.CharField(max_length=64)
    clientSecretHashed = models.CharField(max_length=64)