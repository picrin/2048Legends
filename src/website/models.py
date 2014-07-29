from django.db import models

class Person(models.Model):
    login          = models.CharField(max_length=16)
    hashedPassword = models.CharField(max_length=64)
    salt           = models.CharField(max_length=64)
    def __unicode__(self):
        return str(self.login)

class Tokena(models.Model):
    value      = models.CharField(max_length=64)
    active     = models.BooleanField()
    created    = models.DateTimeField()
    belongs_to = models.ForeignKey(Person)
    def __unicode__(self):
        return str(self.value)

class RandomNegotiation(models.Model):
    serverSecret       = models.CharField(max_length=64)
    serverSecretHashed = models.CharField(max_length=64)
    clientSecret       = models.CharField(max_length=64)
    clientSecretHashed = models.CharField(max_length=64)
    
class Game(models.Model):
    pass
    
class Move(models.Model):
    pass
    


















