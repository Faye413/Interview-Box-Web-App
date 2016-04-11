
"""
This module is the ORM for our database.
It creates an object-oriented view of the database, abstracted the details of the actual
SQL statements with the Peewee library.  Peewee has the added benefit of parameterizing all
queries, eliminating SQL injection attacks.

This can easily be switched to a different database by changing the 'database = ...' line.

The classes all represent a table in the database.  All class variables are columns in the database and should
be fairly self explanatory.  The Metaclass is used by Peewee internally to create the ORM link.
"""

from peewee import *

database = SqliteDatabase('../interviewbox.db')

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Interviewboxuser(BaseModel):
    email = CharField()
    firstname = CharField()
    lastname = CharField()
    num_ratings = IntegerField()
    password = CharField()
    education = CharField()
    employment = CharField()
    position = CharField()
    resume = BlobField(null=True)
    total_ratings = IntegerField()
    username = CharField(unique=True)
    is_interviewer = IntegerField()
    availability = CharField()

    class Meta:
        db_table = 'interviewboxuser'

class Interview(BaseModel):
    time = DateTimeField()
    user1 = ForeignKeyField(db_column='user1', null=True, rel_model=Interviewboxuser, to_field='id')
    user2 = ForeignKeyField(db_column='user2', null=True, rel_model=Interviewboxuser, related_name='interviewboxuser_user2_set', to_field='id')

    class Meta:
        db_table = 'interview'

class Interviewfeedback(BaseModel):
    feedback = CharField()
    interview_id = ForeignKeyField(db_column='interview_id', null=True, rel_model=Interview, to_field='id')

    class Meta:
        db_table = 'interviewfeedback'

class Userschedule(BaseModel):
    schedule = CharField()
    user = ForeignKeyField(db_column='user_id', null=True, rel_model=Interviewboxuser, to_field='id')

    class Meta:
        db_table = 'userschedule'

