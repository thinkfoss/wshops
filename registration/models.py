from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from mail_templated import send_mail

# Create your models here.
GENDER = (('M', _('Male')), ('F', _('Female')))


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, email and password.
        """
        if not email:raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email, username and password.
        """
        user = self.create_user(email, username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Extends the default User profiles of Django. The fields of this model can be obtained by the
    user.get_profile method and it's extended by the django-profile application.
    """
    user_id = models.AutoField(primary_key=True)
    user_first_name = models.CharField(_('First Name'), max_length=32, blank=True, null=True,
                                  validators=[RegexValidator(regex='^[A-Za-z]*$')])
    user_last_name = models.CharField(_('Last Name'), max_length=32, blank=True, null=True,
                                    validators=[RegexValidator(regex='^[A-Za-z]*$')])
    email = models.EmailField(_('Email'), db_index=True, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(_('username'), max_length=32, blank=False, unique=True)
    user_gender = models.CharField(_('Gender'), max_length=1, choices=GENDER, blank=True, null=True)
    user_github = models.CharField(_('Github Profile'),max_length=100,blank=True )
    user_linkedin = models.CharField(_('Linkedin Profile'),max_length=100,blank=True )
    user_bio = models.CharField(_('Short Bio'), max_length=1000,blank=True )
    user_occupation = models.CharField(_('Occupation'), max_length=100,blank=True )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def get_name(self):
        return self.email

    def get_first_name(self):
        return (self.email)

    def get_short_name(self):
        return self.email

    def get_email(self):
        return self.email

    def get_full_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_user_id(self):
        return self.user_id

    @property
    def is_staff(self):
        return self.is_admin

    def __unicode__(self):
        return self.email


DIFFICULTY = (('Easy', _('Easy')), ('Medium', _('Medium')), ('Advanced', _('Advanced')))
LANGUAGE = (('English', _('English')), ('Malayalam', _('Malayalam')), ('Hindi', _('Hindi')))
class Course(models.Model):
    """
    Course model
    """
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(_('Course Name'), max_length=100, blank=False, unique=True)
    course_bio = models.CharField(_('Course Description'), max_length=1000, blank=True, null=True)
    course_language = models.CharField(_('Course Language'), max_length=25, choices=LANGUAGE, blank=False, unique=False)
    course_difficulty = models.CharField(_('Course Difficulty'), max_length=20, choices=DIFFICULTY, blank=False, unique=False)
    course_fees = models.IntegerField(_('Course Fees'),
                                  validators=[MaxValueValidator(99999),MinValueValidator(0)],
                                  help_text=_('5 digits maximum'), blank=True, null=True)
    course_created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    course_user = models.ForeignKey(User, blank=False, null=False)

    def get_mentor(self):
        return self.course_user

    def get_course_name(self):
        return self.course_name

    def get_course_fees(self):
        return self.course_fees

    def get_enrolled_users(self):
        return CourseEnrollment.objects.filter(course=self.course_id, course_enrolled=True).count()

    def save(self):
        if self.approved:
            old_status = Course.objects.get(pk=self.course_id)
            if old_status.approved == False and self.approved == True:
                send_mail('emails/course_approved.html', {'user': self.course_user, 'course': self.course_name }, 'admin@thinkfoss.com', [self.course_user.email, 'admin@thinkfoss.com'])
        super(Course, self).save()

    def __unicode__(self):
        return self.course_name


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    name = models.CharField( max_length=500, blank=True, null=True)
    location = models.CharField( max_length=500, blank=True, null=True)
    description = models.CharField( max_length=500, blank=True, null=True)
    start_date = models.DateField(_('Event From'), blank=True, null=True)
    end_date = models.DateField(_('Event From'), blank=True, null=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, blank=False, null=False)

    def get_owner(self):
        return self.user

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class EventModules(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event,blank=False, null=False)
    name = models.CharField( max_length=500, blank=True, null=True)
    description = models.CharField(_('Module Description'), max_length=1000, blank=True, null=True)
    module_day = models.IntegerField(_('Day when taken'),
                                     validators=[MaxValueValidator(99),MinValueValidator(1)],
                                      help_text=_('2 digits maximum'), blank=True, null=True)
    start_time = models.TimeField(_('Time from'), blank=True, null=True)
    end_time = models.TimeField(_('Time to'), blank=True, null=True)

    def get_event(self):
        return self.event

    def __str__(self):
        return self.event.name + " - " + self.name

    def __unicode__(self):
        return self.name

class ReviewManager(models.Manager):
    def create_review(self,reviewed_module,user):
        created_progress_item = self.create(module=reviewed_module, user=user,is_completed=False)
        return created_progress_item


class EventModuleReview(models.Model):
    module = models.ForeignKey(EventModules,blank=False, null=False)
    user = models.ForeignKey(User,blank=False,null=False)
    remarks = models.CharField( max_length=500, blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    objects = ReviewManager()

    def get_reviewer(self):
        return self.user

    def __str__(self):
        return self.user

    class Meta:
        unique_together = ("user", "module")




class ModuleCompletion(models.Model):
    module = models.ForeignKey(EventModules, blank=False, null=False)
    user = models.ForeignKey(User,blank=False,null=False)
    remarks = models.CharField( max_length=500, blank=True, null=True)
    is_completed = models.BooleanField(default=False)