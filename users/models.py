import collections
import itertools
import os
import re
from os.path import join

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404

import users.identicon
from catalog.models import Course


class CustomUserManager(UserManager):
    PATTERN = re.compile(r'[\W_]+')

    def _create_user(self, netid, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not netid:
            raise ValueError('The given netid must be set')
        email = self.normalize_email(email)
        user = self.model(netid=netid, email=email, last_login=now, **extra_fields)
        if settings.IDENTICON:
            IDENTICON_SIZE = 120
            if not os.path.exists(join(settings.MEDIA_ROOT, "profile")):
                os.makedirs(join(settings.MEDIA_ROOT, "profile"))
            profile_path = join(settings.MEDIA_ROOT, "profile", f"{netid}.png")
            alpha_netid = self.PATTERN.sub('', netid)
            users.identicon.render_identicon(int(alpha_netid, 36), IDENTICON_SIZE / 3).save(profile_path)
            user.photo = 'png'
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, netid, email=None, password=None, **extra_fields):
        return self._create_user(netid, email, password, **extra_fields)

    def create_superuser(self, netid, email, password, **extra_fields):
        return self._create_user(netid, email, password, is_staff=True, **extra_fields)


class User(AbstractBaseUser):

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    DEFAULT_PHOTO = join(settings.STATIC_URL, "images/default.jpg")
    objects = CustomUserManager()

    netid = models.CharField(max_length=20, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=127)
    last_name = models.CharField(max_length=127)
    email = models.CharField(max_length=255, unique=True)
    registration = models.CharField(max_length=80, blank=True)
    photo = models.CharField(max_length=10, default="")
    welcome = models.BooleanField(default=True)
    comment = models.TextField(blank=True, default='')

    register_method = models.CharField(max_length=32)
    last_login_method = models.CharField(max_length=32)

    inferred_faculty = models.TextField(blank=True)
    inscription_faculty = models.TextField(blank=True)

    is_staff = models.BooleanField(default=False)
    is_academic = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)

    moderated_courses = models.ManyToManyField('catalog.Course', blank=True)

    notify_on_response = models.BooleanField(default=True)
    notify_on_new_doc = models.BooleanField(default=True)
    notify_on_new_thread = models.BooleanField(default=True)
    notify_on_upload = True

    def __init__(self, *args, **kwargs):
        self._following_courses = None
        self._moderated_courses = None
        super().__init__(*args, **kwargs)

    @property
    def get_photo(self):
        photo = self.DEFAULT_PHOTO
        if self.photo != "":
            photo = join(settings.MEDIA_URL, "profile/{0.netid}.{0.photo}".format(self))

        return photo

    @property
    def name(self):
        return "{0.first_name} {0.last_name}".format(self)

    def notification_count(self):
        return self.notification_set.filter(read=False).count()

    def following_courses(self):
        return self.courses_set.all()

    def is_following(self, course: Course):
        return self.courses_set.filter(slug=course.slug).exists()

    def has_module_perms(self, *args, **kwargs):
        return True # TODO : is this a good idea ?

    def has_perm(self, perm_list, obj=None):
        return self.is_staff

    def write_perm(self, obj):
        if self.is_staff:
            return True

        if obj is None:
            return False

        if self._moderated_courses is None:
            ids = [course.id for course in self.moderated_courses.only('id')]
            self._moderated_courses = ids

        return obj.write_perm(self, self._moderated_courses)

    def fullname(self):
        return self.name

    def get_short_name(self):
        return self.netid

    def update_inscription_faculty(self):
        inscription = self.inscription_set.order_by("-year").first()
        if inscription:
            self.inscription_faculty = inscription.faculty
            self.save()

    def update_inferred_faculty(self):
        courses = self.following_courses()
        categories = [x.categories.all() for x in courses]
        categories = list(itertools.chain.from_iterable(categories))

        faculties = [x.get_ancestors().filter(level=1).all() for x in categories]
        faculties = list(itertools.chain.from_iterable(faculties))

        counts = collections.Counter(faculties)
        if counts:
            faculty = counts.most_common()[0][0]
            self.inferred_faculty = faculty.name
            self.save()


class Inscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    faculty = models.CharField(max_length=80, blank=True, default='')
    section = models.CharField(max_length=80, blank=True, default='')
    year = models.PositiveIntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'section', 'faculty', 'year')
