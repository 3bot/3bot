# -*- coding: utf-8 -*-
from __future__ import print_function
import time

from django.contrib.auth import get_user_model
from django.test import Client
from django.core.urlresolvers import reverse
from django.test import TestCase

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger, FuzzyText
from threebot.models import Workflow, WorkflowLog
from organizations.models import Organization
from organizations.utils import create_organization
from tests.data import inputs, outputs

User = get_user_model()
NO_ORG = 10
NO_WF = 10
NO_WFL = 1000

class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = FuzzyText(length=12)
    slug = FuzzyText(length=12)


class WorkflowFactory(DjangoModelFactory):
    class Meta:
        model = Workflow

    owner_id = FuzzyInteger(0, 10)
    title = FuzzyText(length=12)


class WorkflowLogFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowLog

    workflow_id = FuzzyInteger(0, 10,)
    performed_by_id = FuzzyInteger(0, 10,)
    performed_on_id = FuzzyInteger(0, 10,)
    inputs = inputs
    outputs = outputs


class HelperTestCase(TestCase):
    def setUp(self):
        OrganizationFactory.create_batch(NO_ORG)
        # WorkflowFactory.create_batch(NO_WF)

        valid_user_name = "valid"
        valid_user_password = "pass"

        self.valid_user = User.objects.create_user(
            username=valid_user_name, email='foo@bar.com', password=valid_user_password
        )
        self.valid_user.save()
        self.organization = create_organization(self.valid_user, 'org', 'org')

        self.valid_client = Client()

        self.assertTrue(
            self.valid_client.login(username=valid_user_name, password=valid_user_password),
            'Logging in user "{}" failed.'.format(valid_user_name)
        )

        for i in range(0, 9):
            Organization.objects.create(name="org_{}".format(i))

        # WorkflowFactory.create_batch(1)
        WorkflowLogFactory.create_batch(NO_WFL)


    def test_index(self):
        response = self.valid_client.get(reverse('core_index'))
        assert "Configure, Build and Perform" in response.content
