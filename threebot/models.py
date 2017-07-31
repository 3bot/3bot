import re
import keyword
import hashlib
import datetime
import random
import logging

from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.validators import validate_email
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings

from organizations.models import Organization
from jsonfield import JSONField


logger = logging.getLogger('3bot')

VALID_IDENTIFIER = "An identifier is a letter or underscore, followed by an unlimited string of \
    letters, numbers, and underscores. Python Keywords are not allowed."

RESERVED_IDENTIFIERS = ['log', 'payload']


def is_valid_identifier(identifier):
    if not re.match('[_A-Za-z][_a-zA-Z0-9]*$', identifier) or keyword.iskeyword(identifier):
        return False
    return True


@python_2_unicode_compatible
class Worker(models.Model):
    ACCESS_REQUEST_TIMEOUT = 1
    STATUS_OFFLINE = 0
    STATUS_ONLINE = 1
    STATUS_BUSY = 9
    STATUS_MUTED = 10
    STATUS_CHOICES = (
        (STATUS_OFFLINE, 'offline'),
        (STATUS_ONLINE, 'online'),
        (STATUS_BUSY, 'busy'),
        (STATUS_MUTED, 'muted'),
    )

    owner = models.ForeignKey(Organization, help_text="Worker owner")
    title = models.CharField(max_length=255)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    ip = models.GenericIPAddressField("IP-Address",)
    addr = models.CharField(max_length=200, null=True, blank=True, help_text='For now we use the IP to connect to the worker')
    port = models.PositiveIntegerField(default=55555)
    secret_key = models.CharField(max_length=200, null=True, blank=True, help_text='The Secret Key. Never share yours.')

    muted = models.BooleanField(default=False, help_text="Mute a Worker to prevent accessibility checks and improve performance.")

    pre_task = models.TextField(null=True, blank=True, help_text='this will run as a Script before the worker performs a workflow')
    post_task = models.TextField(null=True, blank=True, help_text='this will run as a Script after the worker has performed a workflow')

    class Meta():
        ordering = ['owner', 'title']
        verbose_name = _("Worker")
        verbose_name_plural = _("Workers")

    def get_status_display(self):
        choices = dict(self.STATUS_CHOICES)
        return choices[self.status]

    @cached_property
    def status(self):
        if self.muted:
            return self.STATUS_MUTED
        if self.is_busy:
            return self.STATUS_BUSY
        if self.is_accessible:
            return self.STATUS_ONLINE
        else:
            return self.STATUS_OFFLINE

    @cached_property
    def is_busy(self):
        """Identifies is a Worfkflow is currently blocking this worker."""
        return WorkflowLog.objects.filter(exit_code=WorkflowLog.PENDING, performed_on=self).exists()

    @cached_property
    def is_accessible(self):
        if self.muted:
            return False

        try:
            from .botconnection import BotConnection
            from .tasks import send_script

            protocol = "tcp"
            WORKER_ENDPOINT = "%s://%s:%s" % (protocol, self.ip, str(self.port))
            WORKER_SECRET_KEY = str(self.secret_key)
            conn = BotConnection(WORKER_ENDPOINT, WORKER_SECRET_KEY)
            conn.connect()

            req = {'type': 'ACC'}
            resp = send_script(req, conn, REQUEST_TIMEOUT=1000, REQUEST_RETRIES=1)
            conn.close()

            if resp and resp['type'] == 'ACK':
                return True
        except Exception as e:
            logger.error(e, exc_info=True)
        return False

    def save(self, *args, **kwargs):
        if not self.pk:  # first save
            self.slug = random.randint(1000, 9999)
            super(Worker, self).save(*args, **kwargs)

        s = str(self.owner.id) + "-" + str(self.id) + "-" + slugify(self.title)
        self.slug = s[:50]
        super(Worker, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('core_worker_detail', (), {
            'slug': self.slug})

    def permalink(self):
        return reverse('core_worker_permalink', kwargs={'id': self.id})

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Task(models.Model):
    unique_identifier = models.CharField(max_length=255, null=True, blank=True, help_text="Unique Identifier to group multiple Task Versions")
    version_major = models.PositiveIntegerField(null=True, blank=True, default=0)
    version_minor = models.PositiveIntegerField(null=True, blank=True, default=0)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    is_readonly = models.BooleanField(default=False, help_text="Only Team-Admins can edit")
    is_builtin = models.BooleanField(default=False, help_text="Will be executed as Python Module on 3bot Platform")

    owner = models.ForeignKey(Organization, help_text="Task owner")
    title = models.CharField(max_length=255)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    desc = models.TextField(null=True, blank=True)

    template = models.TextField(default="#!/bin/sh\n", help_text="To declare an input, type: {{ <data type>.<identifier> }}")

    inputs_fingerprint = models.CharField(max_length=32, blank=True, null=True)
    changelog = models.TextField(blank=True, null=True)

    class Meta():
        ordering = ['owner', 'title']
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        unique_together = (('unique_identifier', 'version_major', 'version_minor'),)

    def clean(self):
        valid_data_types = 'Valid data types are: '
        for el in Parameter.DATA_TYPE_CHOICES:
            valid_data_types += '"%s", ' % el[0]

        valid_identifier = VALID_IDENTIFIER

        inputs = self.extract_inputs()

        if not inputs:
            return

        for name, data_type in inputs.iteritems():
            field = 'template'
            if not any(data_type == el[0] for el in Parameter.DATA_TYPE_CHOICES):
                msg = '"%s" is not a valid data type' % data_type
                raise ValidationError({field: [msg, valid_data_types, ]})
            if not is_valid_identifier(name):
                msg = '"%s" is not a valid identifier' % name
                raise ValidationError({field: [msg, valid_identifier, ]})

    def extract_inputs(self):
        """returns a dict of variables declared in the tempalte string"""
        """ {u'some_words': u'string', u'some_word': u'string'} """
        found_inputs = re.findall(r'\{{(.+?)\}}', self.template)
        inputs = {}
        field = 'template'

        for i in found_inputs:
            msg = '"%s" is not a valid input declaration.' % str(i.encode('utf-8').strip())
            inp = i.strip().split(".")
            if inp[0] not in RESERVED_IDENTIFIERS:
                try:
                    if not inp[0] or not inp[1]:
                        raise ValidationError({field: [msg, ]})
                    inputs[inp[1]] = inp[0]
                except IndexError:
                    raise ValidationError({field: [msg, ]})

        return inputs

    @property
    def required_inputs(self):
        return self.extract_inputs()

    @property
    def type(self):
        known_types = ['bash', 'sh', 'python', 'ruby', 'pearl', 'php', 'node', 'osascript']

        if self.is_builtin:
            return "built-in"
        if self.template.startswith('#!'):
            shebang = self.template.split('\n', 1)[0]
            for type in known_types:
                if shebang.find(type) > 0:
                    return type
        return "unknown"

    @property
    def version(self):
        return "%i.%i" % (self.version_major, self.version_minor)

    def save(self, *args, **kwargs):
        if not self.pk:  # first save
            self.slug = random.randint(1000, 9999)
            super(Task, self).save(*args, **kwargs)

        if not self.unique_identifier:
            md_hash = hashlib.md5()
            md_hash.update(self.title.encode('utf-8') + str(datetime.datetime.now()))
            self.unique_identifier = md_hash.hexdigest()

        s = str(self.owner.id) + "-" + str(self.id) + "-" + slugify(self.title)
        self.slug = s[:50]
        fingerprint = hashlib.md5()
        fingerprint.update(str(self.required_inputs).encode('utf-8'))
        self.inputs_fingerprint = fingerprint.hexdigest()
        super(Task, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('core_task_detail', (), {
            'slug': self.slug})

    def permalink(self):
        return reverse('core_task_permalink', kwargs={'id': self.id})

    def __str__(self):
        return self.title or self.desc or str(self.pk)


@python_2_unicode_compatible
class Workflow(models.Model):
    unique_identifier = models.CharField(max_length=255, null=True, blank=True, help_text="Unique Identifier to group multiple Workflow Versions")
    version_major = models.PositiveIntegerField(null=True, blank=True, default=0)
    version_minor = models.PositiveIntegerField(null=True, blank=True, default=0)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(Organization, help_text="Workflow owner")
    title = models.CharField(max_length=255)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    desc = models.TextField(null=True, blank=True)

    pre_task = models.TextField(null=True, blank=True, help_text='This will run as a Script before the worker runs a task of the current workflow. (Runs before each task)')
    post_task = models.TextField(null=True, blank=True, help_text='This will run as a Script after the worker has executed a task of the current workflow. (Runs after each task)')

    tasks = models.ManyToManyField(Task, through='WorkflowTask')

    class Meta():
        ordering = ['owner', 'title']
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")
        unique_together = (('unique_identifier', 'version_major', 'version_minor'),)

    def number_of_tasks(self):
        return WorkflowTask.objects.filter(workflow=self).count()

    def save(self, *args, **kwargs):
        if not self.pk:  # first save
            self.slug = random.randint(1000, 9999)
            super(Workflow, self).save(*args, **kwargs)

        if not self.unique_identifier:
            md_hash = hashlib.md5()
            md_hash.update(self.title.encode('utf-8') + str(datetime.datetime.now()))
            self.unique_identifier = md_hash.hexdigest()

        s = str(self.owner.id) + "-" + str(self.id) + "-" + slugify(self.title)
        self.slug = s[:50]
        super(Workflow, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('core_workflow_detail', (), {
            'slug': self.slug})

    def permalink(self):
        return reverse('core_workflow_permalink', kwargs={'id': self.id})

    def __str__(self):
        return self.title or self.desc or str(self.pk)


@python_2_unicode_compatible
class WorkflowPreset(models.Model):
    workflow = models.ForeignKey(Workflow, verbose_name=_("Workflow"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=("User"))
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    defaults = JSONField(null=True, blank=True, default={})

    class Meta():
        ordering = ['date_modified', 'workflow', 'user', ]
        unique_together = (('workflow', 'user',), )
        verbose_name = _("Workflow Preset")
        verbose_name_plural = _("Workflow Presets")

    def all_presets_set(self):
        wf_tasks = WorkflowTask.objects.filter(workflow=self.workflow)

        # skip empty workflows
        if not wf_tasks:
            return False

        errors = False
        org = self.workflow.owner

        for workflow_task in wf_tasks:

            for param_name, param_data_type in workflow_task.task.required_inputs.iteritems():
                wanted_key = '%s.%s' % (param_data_type, param_name)

                if str(workflow_task.id) in self.defaults:
                    if not wanted_key in self.defaults[str(workflow_task.id)]:
                        errors = True
                    else:
                        parameter_path = self.defaults[str(workflow_task.id)][wanted_key]
                        path_units = parameter_path.strip().split('.')
                        if path_units[0] == 'user':
                            if not UserParameter.objects.filter(name=path_units[2], data_type=path_units[1], owner=self.user).exists():
                                errors = True
                        elif path_units[0] == 'global':
                            if not OrganizationParameter.objects.filter(name=path_units[2], data_type=path_units[1], owner=org).exists():
                                errors = True
                        elif path_units[0] == 'output':
                                errors = False
                        else:
                            errors = True
                else:
                    errors = True

        return not errors

    def __str__(self):
        return "Preset for %s (%s)" % (self.workflow, self.user)


@python_2_unicode_compatible
class WorkflowTask(models.Model):
    workflow = models.ForeignKey(Workflow, verbose_name=_("Workflow"))
    task = models.ForeignKey(Task, verbose_name=_("Task"))
    prev_workflow_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("The previous Workflow Task"), related_name="prev_wt")
    next_workflow_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("The next Workflow Task"), related_name="next_wt")

    class Meta():
        ordering = ['workflow', 'task', ]
        verbose_name = _("Workflow Task")
        verbose_name_plural = _("Workflow Tasks")

    def delete(self, *args, **kwargs):
        if self.prev_workflow_task and self.next_workflow_task:  # between
            self.prev_workflow_task.next_workflow_task = self.next_workflow_task
            self.next_workflow_task.prev_workflow_task = self.prev_workflow_task
        elif self.prev_workflow_task and not self.next_workflow_task:  # last element
            self.prev_workflow_task.next_workflow_task = None
        elif not self.prev_workflow_task and self.next_workflow_task:  # first element
            self.next_workflow_task.prev_workflow_task = None
        else:  # one and only element
            pass

        super(WorkflowTask, self).delete(*args, **kwargs)  # Call the "real" save() method

    def __str__(self):
        if self.prev_workflow_task:
            s = str(self.prev_workflow_task.task.slug)
        else:
            s = "START"
        if self.next_workflow_task:
            n = str(self.next_workflow_task.task.slug)
        else:
            n = "END"
        return "%s: %s -(%s)-> %s" % (str(self.workflow), str(s), str(self.task.slug), str(n))


@python_2_unicode_compatible
class WorkflowLog(models.Model):
    SUCCESS = 0
    ERROR = 1
    PENDING = 2

    EXIT_CODE_CHOICES = (
        (SUCCESS, 'Success'),
        (ERROR, 'Error'),
        (PENDING, 'Pending'),
    )

    workflow = models.ForeignKey(Workflow, verbose_name=_("Workflow"))
    date_created = models.DateTimeField(auto_now_add=True, help_text='Date the workflow was performed')
    date_started = models.DateTimeField(help_text='Date the workflow was performed', blank=True, null=True)
    date_finished = models.DateTimeField(help_text='Date the workflow was performed', blank=True, null=True)
    exit_code = models.PositiveIntegerField(choices=EXIT_CODE_CHOICES, default=PENDING)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, help_text="The User who performed the Worfkflow")
    performed_on = models.ForeignKey(Worker, help_text="The Worker Worfkflow was performed on")

    inputs = JSONField()
    outputs = JSONField(null=True, blank=True)

    class Meta():
        ordering = ['-date_created', ]
        verbose_name = _("Workflow Log")
        verbose_name_plural = _("Workflow Logs")

    @models.permalink
    def get_absolute_url(self):
        return ('core_workflow_log_detail', (), {
            'slug': self.workflow.slug,
            'id': self.id})

    def permalink(self):
        return reverse('core_workflow_log_permalink', kwargs={'id': self.id})

    def __str__(self):
        return "%s - %s logged %s" % (self.date_created.strftime('%d.%m.%y %H:%M'), str(self.performed_by), self.workflow.title, )


class Parameter(models.Model):
    STRING = 'string'
    EMAIL = 'email'
    PASSWORD = 'password'
    BOOLEAN = 'bool'
    INT = 'int'
    FLOAT = 'float'
    IPv4 = 'ipv4'
    IPv6 = 'ipv6'

    DATA_TYPE_CHOICES = (
        (STRING, 'String'),
        (EMAIL, 'Email'),
        #(PASSWORD, 'Password'),
        (BOOLEAN, 'Boolean'),
        # (INT, 'Integer'),
        # (FLOAT, 'Floating Number'),
        # (IPv4, 'IP 4'),
        # (IPv6, 'IP 6'),
    )

    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default=STRING)
    name = models.CharField("identifier", max_length=255, blank=False, null=False)
    value = models.CharField(max_length=255, blank=False, null=False)

    def clean(self):
        field = 'name'
        if not is_valid_identifier(self.name):
            valid_identifier = VALID_IDENTIFIER
            msg = '"%s" is not a valid identifier' % self.name
            raise ValidationError({field: [msg, valid_identifier, ]})

        # Checks that the parameters validates for the selected data type
        if self.data_type == self.EMAIL and self.value is not None:
            validate_email(self.value)

        elif self.data_type == self.BOOLEAN and not (self.value == 'True' or self.value == 'False'):
            raise ValidationError("Boolean Parameter can be either True or False")

        elif self.data_type == self.STRING and self.value is not None:
            pass


@python_2_unicode_compatible
class UserParameter(Parameter):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, help_text="Parameter owner")

    class Meta():
        ordering = ['owner', 'data_type', ]
        verbose_name = _("Parameter for User")
        verbose_name_plural = _("Parameters for Users")

    def save(self, *args, **kwargs):
        super(UserParameter, self).save(*args, **kwargs)

    def validate_unique(self, *args, **kwargs):
        # this is called every time the obj gets updated or saved
        # the try/except is needed to prevent DoesNotExist errors for the owner field.
        try:
            self.owner
        except:
            return
        # Checks that no two parameters have the same name, data_type and owner
        if UserParameter.objects.filter(name=self.name, data_type=self.data_type, owner=self.owner).exists():
            same_param = UserParameter.objects.get(name=self.name, data_type=self.data_type, owner=self.owner)
            if not same_param.id == self.id:
                raise ValidationError(
                    {
                        NON_FIELD_ERRORS:
                        ('Parameter with this name and data type already exists',)
                    }
                )

    def __str__(self):
        return "%s:%s (%s)" % (self.data_type, self.name, self.owner)

    @models.permalink
    def get_absolute_url(self):
        return ('core_user_parameter_detail', (), {
            'id': self.id})


@python_2_unicode_compatible
class OrganizationParameter(Parameter):
    owner = models.ForeignKey(Organization, help_text="Parameter owner")

    class Meta():
        ordering = ['owner', 'data_type', ]
        verbose_name = _("Parameter for Team")
        verbose_name_plural = _("Parameters for Team")

    def save(self, *args, **kwargs):
        super(OrganizationParameter, self).save(*args, **kwargs)

    def validate_unique(self, *args, **kwargs):
        # this is called every time the obj gets updated or saved
        # the try/except is needed to prevent DoesNotExist errors for the owner field.
        try:
            self.owner
        except:
            return
        # Checks that no two parameters have the same name, data_type and owner
        if OrganizationParameter.objects.filter(name=self.name, data_type=self.data_type, owner=self.owner).exists():
            same_param = OrganizationParameter.objects.get(name=self.name, data_type=self.data_type, owner=self.owner)
            if not same_param.id == self.id:
                raise ValidationError(
                    {
                        NON_FIELD_ERRORS:
                        ('Parameter with this name and data type already exists',)
                    }
                )

    def __str__(self):
        return "%s:%s (%s)" % (self.data_type, self.name, self.owner)

    @models.permalink
    def get_absolute_url(self):
        return ('core_organization_parameter_detail', (), {
            'slug': self.owner.slug,
            'id': self.id})


@python_2_unicode_compatible
class ParameterList(models.Model):
    """
    ParameterList
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(Organization, help_text="Parameter List owner")
    parameters = models.ManyToManyField(OrganizationParameter, related_name="lists", help_text="Select Parameters for this Team.")

    class Meta():
        ordering = ['title', 'date_created', ]
        verbose_name = _("Parameter List")
        verbose_name_plural = _("Parameter Lists")

    def __str__(self):
        return self.title
