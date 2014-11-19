from django.db import models
import random, string

def create_test_person(login="retro"):
    p = Person(login=login, hashedPassword="123123123", salt="abcabcabc")
    p.save()

class Person(models.Model):
    login          = models.CharField(max_length=16)
    hashedPassword = models.CharField(max_length=64)
    salt           = models.CharField(max_length=64)
    currentGame    = models.ForeignKey('Game', null=True, blank=True)
    bestResult     = models.BigIntegerField(default=0)
    gamesRemaining = models.IntegerField(default=0)
    #def __unicode__(self):
    #    return str(self.login)

#the wallet id will be the best way to uniquely identify transactions
class Transaction(models.Model):
    # created date
    # completed date
    # associated person
    # associated wallet id (for blockchain.info)
    # Transaction Secret
    # amount intended                                  #Note
    # amount recieved                                  #These two fields will have be limited to 18 digits in length
    # plays intended
    # plays recieved
    # change given
    
    _SECRET_LENGTH = 24
    _SECRET_VALID_CHARS = ''.join(string.digits + string.ascii_uppercase + string.ascii_lowercase)
    
    #fields that must have value on creation
    belongs_to         = models.ForeignKey('Person', null=False, blank=False)
    wallet_id          = models.CharField(max_length=35, blank=False)
    transaction_secret = models.CharField(max_length=_SECRET_LENGTH, blank=False)
    date_created       = models.DateTimeField(auto_now=False, auto_now_add=True) #automatically assigned on creation
    intended_currency  = models.DecimalField(decimal_places=8, max_digits=18, blank=False)
    intended_plays     = models.IntegerField(blank=False)
    
    #fields whose values will be filled in later
    date_completed     = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    recieved_currency  = models.DecimalField(decimal_places=8, max_digits=18, null=True)     #should this be made in to a reciept model so that if we recieve multiple payments by accident, we can still track them?
    recieved_plays     = models.IntegerField(null=True)
    
    def is_completed(self):
        return self.date_completed is not None
        
    @staticmethod
    def generate_secret():
        return ''.join([random.choice(Transaction._SECRET_VALID_CHARS) for i in range(Transaction._SECRET_LENGTH)])
        
    

class Tokena(models.Model):
    value      = models.CharField(max_length=64)
    active     = models.BooleanField(default=False)
    created    = models.DateTimeField()
    belongs_to = models.ForeignKey(Person)
    #def __unicode__(self):
    #    return str(self.value)

class Game(models.Model):
    gameid     = models.CharField(max_length=64)
    belongs_to = models.ForeignKey(Person, null=True)
    lastMove   = models.ForeignKey('Move', null=True, blank=True)
    gameover   = models.BooleanField(default=False)
    result     = models.BigIntegerField(null=True)

class Move(models.Model):
    belongs_to         = models.ForeignKey('Game', null=True, blank=True)
    moveNumber         = models.BigIntegerField()
    board              = models.CharField(max_length=200)
    allempty           = models.CharField(max_length=200)
    serverSecret       = models.CharField(max_length=64)
    serverSecretHashed = models.CharField(max_length=64)
    clientSecret       = models.CharField(max_length=64)
    clientSecretHashed = models.CharField(max_length=64)