from datetime import timedelta

from django.db import models
from django.utils import timezone

from users.models import Member


# TODO:
# Consider merging notifications of the same type. How do we do this???
# COULD MERGE BY URL

class NotifType:
    NEWSLETTER = 1
    MESSAGE = 2
    RPG_JOIN = 3
    RPG_LEAVE = 4
    RPG_KICK = 5
    RPG_ADDED = 6
    FORUM_REPLY = 7
    OTHER = 8


class SubType:
    NONE = 0
    WEB = 1
    SUMMARY = 2
    FULL = 3


class NotificationSubscriptions(models.Model):
    notification_types = [
        (NotifType.NEWSLETTER, 'Newsletter'),
        (NotifType.MESSAGE, 'PMs'),
        (NotifType.RPG_JOIN, 'RPG Gains Member'),
        (NotifType.RPG_LEAVE, 'RPG Looses Member'),
        (NotifType.RPG_KICK, 'Kicked from RPG'),
        (NotifType.RPG_ADDED, 'Added to RPG'),
        (NotifType.FORUM_REPLY, 'Forum Replies'),
        (NotifType.OTHER, 'Other Notification')
    ]
    subscription_types = [
        (SubType.NONE, 'None'),
        (SubType.WEB, 'Online Only'),
        (SubType.SUMMARY, 'Summary Email'),
        (SubType.FULL, 'Full Email'),
    ]
    reduced_subscription_types = subscription_types[:3]
    member = models.OneToOneField(Member, on_delete=models.CASCADE)

    newsletter = models.IntegerField(verbose_name='Newsletters', choices=subscription_types, default=SubType.WEB)
    message = models.IntegerField(verbose_name='Receive Direct Messages', choices=reduced_subscription_types,
                                  default=SubType.WEB)
    rpg_join = models.IntegerField(verbose_name='Someone Joins Your Event', choices=reduced_subscription_types,
                                   default=SubType.WEB)
    rpg_leave = models.IntegerField(verbose_name='Someone Leaves Your Event', choices=reduced_subscription_types,
                                    default=SubType.WEB)
    rpg_kick = models.IntegerField(verbose_name='Removal from an Event', choices=reduced_subscription_types,
                                   default=SubType.WEB)
    rpg_add = models.IntegerField(verbose_name='Addition to an Event', choices=reduced_subscription_types, default=SubType.WEB)
    forum_reply = models.IntegerField(verbose_name='Reply to a Forum Post You Participated in',
                                      choices=subscription_types,
                                      default=SubType.WEB)
    other = models.IntegerField(verbose_name='Miscellaneous', choices=reduced_subscription_types, default=SubType.NONE)

    def get_category_subscription(self, category):
        # Map setting value to its ID value
        mapping = {
            NotifType.NEWSLETTER: self.newsletter,
            NotifType.MESSAGE: self.message,
            NotifType.RPG_JOIN: self.rpg_join,
            NotifType.RPG_LEAVE: self.rpg_leave,
            NotifType.RPG_KICK: self.rpg_kick,
            NotifType.RPG_ADDED: self.rpg_add,
            NotifType.FORUM_REPLY: self.forum_reply,
            NotifType.OTHER: self.other
        }

        if category in mapping:
            return mapping[category]
        else:
            return SubType.NONE

    def __str__(self):
        return str(self.member.equiv_user.username)

    class Meta:
        verbose_name_plural = "Notifications Subscriptions"
        verbose_name = "Notifications Subscription"




class Notification(models.Model):
    notification_types = [
        (NotifType.NEWSLETTER, 'Newsletter'),
        (NotifType.MESSAGE, 'Message Received'),
        (NotifType.RPG_JOIN, 'Joined RPG'),
        (NotifType.RPG_LEAVE, 'Left RPG'),
        (NotifType.RPG_KICK, 'Kicked from RPG'),
        (NotifType.RPG_ADDED, 'Added to RPG'),
        (NotifType.FORUM_REPLY, 'Replied to Forum'),
        (NotifType.OTHER, 'Other Notification')
    ]
    member = models.ForeignKey(Member, related_name='notifications_owned', on_delete=models.CASCADE)
    notif_type = models.IntegerField(choices=notification_types, default=NotifType.OTHER)
    url = models.CharField(max_length=512)
    content = models.TextField(max_length=8192)
    # A value used to group notifications. Usually a relevant primary key (forum thread key, rpg key, etc.):
    merge_key = models.IntegerField(blank=True, null=True)
    is_unread = models.BooleanField()
    is_emailed = models.BooleanField()
    time = models.DateTimeField()

    def notify_icon(self):
        default_icon = 'fa-circle'
        icons = {
            NotifType.NEWSLETTER: 'fa-newspaper-o',
            NotifType.MESSAGE: 'fa-commenting-o',
            NotifType.RPG_JOIN: 'fa-sign-in',
            NotifType.RPG_LEAVE: 'fa-sign-out',
            NotifType.RPG_KICK: 'fa-times',
            NotifType.RPG_ADDED: 'fa-magic',
            NotifType.FORUM_REPLY: 'fa-quote-right',
            NotifType.OTHER: default_icon
        }
        if self.notif_type in icons:
            return icons[self.notif_type]
        else:
            return default_icon


def notify(member, notif_type, content, url, merge_key=None):
    sub, new = NotificationSubscriptions.objects.get_or_create(member=member)
    if sub.get_category_subscription(notif_type) != SubType.NONE:
        n = create_notification(member, notif_type, content, url, merge_key)
        n.full_clean()  # Not strictly needed as all data is generated, but good practice...
        n.save()
        delete_old(member)


def create_notification(member, notif_type, content, url, merge_key=None):
    return Notification(member=member, notif_type=notif_type, content=content, url=url, is_unread=True,
                        is_emailed=False, merge_key=merge_key,
                        time=timezone.now())


def create_notification_if_subbed(member, notif_type, content, url, merge_key=None):
    sub, new = NotificationSubscriptions.objects.get_or_create(member=member)
    if sub.get_category_subscription(notif_type) != SubType.NONE:
        return create_notification(member, notif_type, content, url, merge_key)
    else:
        return None


def delete_old(member):
    week_ago = timezone.now() - timedelta(days=7)
    Notification.objects.filter(member=member, is_unread=False, time__lt=week_ago).delete()


def delete_all_old():
    week_ago = timezone.now() - timedelta(days=7)
    Notification.objects.filter(is_unread=False, time__lt=week_ago).delete()


def notify_everybody(notif_type, content, url, merge_key=None):
    notifs = [create_notification_if_subbed(m, notif_type, content, url, merge_key) for m in Member.objects.all()]
    notifications = list(filter(None, notifs))
    Notification.objects.bulk_create(notifications)
    delete_all_old()
