from django.conf import settings
from django_cron import CronJobBase, Schedule
from members.models import EmailItem, Family, Notification, EmailTemplate, ActivityParticipant
from django.db.models import Q, F
import datetime
from django.utils import timezone

# Send confirmations to Activity signups, which do not have failed payments
class SendActivitySignupConfirmationsCronJob(CronJobBase):
    RUN_EVERY_MINS = 5 # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'members.send_activity_signup_confirmation_cronjob'    # a unique code

    def do(self):
        unannounced_signups = ActivityParticipant.objects.exclude(notification__isnull=False).filter(payment__confirmed_dtm__isnull=False)

        for announcement in unannounced_signups:
            context = {
                'activity' : announcement.activity,
                'person' : announcement.member.person,
                'family' : announcement.member.person.family
            }
            emails = EmailTemplate.objects.get(idname='ACT_CONFIRM').makeEmail([announcement.member.person, announcement.member.person.family], context)
            for email in emails:
                notification = Notification(family=announcement.member.person.family, email=email, anounced_activity_participant=announcement)
                notification.save()


# Send out all queued emails
class EmailSendCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'members.email_send_cronjob'    # a unique code

    def do(self):
        for curEmail in EmailItem.objects.filter(sent_dtm=None):
            curEmail.send()

# Find families, which needs to update their information
class RequestConfirmationCronJob(CronJobBase):
    RUN_AT_TIMES = ['15:00',]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = 'members.request_confirmation_cronjob'    # a unique code


    def do(self):
        # Find all Families, which has an updated_dtm older than the specified time for updates from today.
        # Exclude the families which has already received a notification after they updated last.
        # (to avoid sending again)
        outdated_dtm = timezone.now() - datetime.timedelta(days=settings.REQUEST_FAMILY_VALIDATION_PERIOD)
        unconfirmed_families = Family.objects.filter(Q(confirmed_dtm__lt=outdated_dtm) | Q(confirmed_dtm=None)).exclude(Q(notification__update_info_dtm__gt=F('confirmed_dtm')) | Q(~Q(notification__update_info_dtm=None), confirmed_dtm=None))

        # send notification to all families asking them to update
        # their family details
        for family in unconfirmed_families:
            email = EmailTemplate.objects.get(idname='UPDATE_DATA').makeEmail(family, {})[0]
            notification = Notification(family=family, email=email, update_info_dtm=timezone.now())
            notification.save()


# TODO:Find created families/persons, which never clicked the link (spambots etc.)

# TODO:Find families which are about to get deleted from the list and send warning

# TODO:Find Members which are active, but have expired memberships

# TODO:Poll payments which did not recieve callback
