from django.db import models


# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=100)
    p_url = models.CharField(max_length=200)
    commenter = models.CharField(max_length=100)
    c_url = models.CharField(max_length=100)
    c_time = models.IntegerField()
    star = models.IntegerField()
    help = models.CharField(max_length=100)
    comment = models.TextField()
    hasImage = models.BooleanField()


class User(models.Model):
    username = models.CharField(max_length=100)
    u_url = models.CharField(max_length=200)
    p_name = models.CharField(max_length=100)
    star = models.IntegerField()
    suggestion = models.CharField(max_length=200)
    help = models.CharField(max_length=100)
    time = models.IntegerField()
    content = models.TextField()


class ProductNew(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500)
    price = models.CharField(max_length=20)
    rank = models.IntegerField()
    star = models.CharField(max_length=20)
    commentPageNum = models.IntegerField()
    comment_url = models.CharField(max_length=500)
    is_last_add = models.IntegerField()


class CommentNew(models.Model):
    pid = models.IntegerField()
    user_url = models.CharField(max_length=200)
    user_name = models.CharField(max_length=100)
    star = models.CharField(max_length=20)
    suggestion = models.CharField(max_length=200)
    sugg_sen_pos = models.DecimalField(max_digits=20,decimal_places=15)   # new
    sugg_sen_neg = models.DecimalField(max_digits=20,decimal_places=15)   # new
    isConfirmed = models.IntegerField()
    comment = models.TextField()
    comment_count = models.IntegerField()    # new
    hasImage = models.IntegerField()
    hasReply = models.IntegerField()         # new
    help = models.CharField(max_length=100)   # new
    comment_date = models.CharField(max_length=200)  # new
    is_last_add = models.IntegerField()

class UserNew(models.Model):
    cid = models.IntegerField()
    user_name = models.CharField(max_length=200)
    rank = models.IntegerField()
    help_receive = models.IntegerField()
    help_useful = models.IntegerField()
    pname = models.CharField(max_length=200)
    pstar = models.CharField(max_length=20)
    psuggestion = models.CharField(max_length=200)
    pcomment = models.TextField()
    is_last_add = models.IntegerField()

class CommentSentiment(models.Model):
    cid = models.IntegerField()
    comment = models.TextField()
    comment_count = models.IntegerField()    # new
    code = models.IntegerField()
    message = models.CharField(max_length=200)
    positive = models.DecimalField(max_digits=20, decimal_places=15)
    negative = models.DecimalField(max_digits=20, decimal_places=15)

