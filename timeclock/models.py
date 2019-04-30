from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Create your models here.

# class UserDayTime(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL)
#     today = models.DateField(default=timezone.now)

USER_ACTIVITY_CHOICES = (
        ('checkin', 'Check In'),
        ('checkout', 'Check Out'),
    )

class UserActivityManager(models.Manager):
    def current(self, user=None):
        if user is None:
            return None
        current_obj = self.get_queryset().filter(user=user).order_by('-timestamp').first()
        return current_obj

    def toggle(self, user=None):
        if user is None:
            return None
        last_item = self.current(user)
        activity = "checkin"
        if last_item is not None:
            if last_item.activity == "checkin":
                activity = "checkout"

        obj = self.model(
                user = user,
                activity = activity
            )
        obj.save()
        return obj



class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    activity = models.CharField(max_length=120, default='checkin', choices=USER_ACTIVITY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = UserActivityManager()

    def __unicode__(self):
        return str(self.activity)

    def __str__(self):
        return str(self.activity)

    class Meta:
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"

    def clean(self, *args, **kargs):
        if self.user:
            user_activities = UserActivity.objects.exclude(
                                    id=self.id
                                ).filter(
                                    user=self.id
                                ).order_by('-timestamp')
            if user_activities.exists():
                recent_ = user_activities.first
                if self.activity == recent_.activity:
                    message = f"{self.get_activity_display()} is not a valid activity for this user"
                    raise ValidationError(message)
            else:
                if self.activity != "checkin":
                    message = f"{self.get_activity_display()} is not a valid activity for this user as a first activity"
                    raise ValidationError(message)

            return super(UserActivity, *args, **kargs)