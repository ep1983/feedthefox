import os
import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible

from stdnum import imei


DEFAULT_DEVICE_TYPE = 'smartphone'


def _get_upload_file_name(instance, filename):
    return os.path.join(settings.USER_PHOTOS_DIR, str(uuid.uuid4()) + '.jpg')


def validate_imei(imei_number):
    if imei_number.strip() and not imei.is_valid(imei_number):
        raise ValidationError('Please enter a valid IMEI number.')
    return imei_number


@python_2_unicode_compatible
class Build(models.Model):
    """Model for FxOS builds."""

    name = models.CharField(max_length=120)
    date = models.DateField(auto_now_add=True)
    link = models.URLField(blank=True, default='')
    is_foxfooding = models.BooleanField(default=False)
    comment = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Device(models.Model):
    """Model for FxOS devices."""

    model = models.CharField(max_length=120)
    manufacturer = models.CharField(max_length=120)
    image = models.ImageField(upload_to=_get_upload_file_name, blank=True, null=True)
    comment = models.TextField(blank=True, default='')
    builds = models.ManyToManyField(Build, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='devices',
                                   through='DeviceInfo', blank=True)
    type = models.CharField(max_length=120, default=DEFAULT_DEVICE_TYPE)
    link = models.URLField(blank=True, default='')
    codename = models.CharField(max_length=120, blank=True, default='')

    def __str__(self):
        return u'{0} - {1}'.format(self.manufacturer, self.model)

    class Meta:
        ordering = ('manufacturer', 'model',)
        unique_together = ('manufacturer', 'model',)


@python_2_unicode_compatible
class DeviceInfo(models.Model):
    """Device Info model."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='devices_info')
    device = models.ForeignKey(Device)
    imei = models.CharField(max_length=17, blank=True, default='',
                            validators=[validate_imei])
    is_foxfooding = models.BooleanField(default=False)

    def __str__(self):
        return u'{0} {1}'.format(self.user, self.device)

    class Meta:
        verbose_name_plural = 'Devices Info'
