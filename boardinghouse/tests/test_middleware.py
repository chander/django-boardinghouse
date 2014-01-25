from django.test import TestCase

from ..schema import get_schema, TemplateSchemaActivation
from ..models import Schema
from .models import AwareModel, User

CREDENTIALS = {
    'username': 'test',
    'password': 'test'
}

class TestMiddleware(TestCase):
    def test_view_without_schema_aware_models_works_without_activation(self):
        resp = self.client.get('/')
        self.assertEquals(200, resp.status_code)
        self.assertEquals('None', resp.content)
    
    
    def test_unauth_cannot_change_schema(self):
        first = Schema.objects.create(name='first', schema='first')
        second = Schema.objects.create(name='second', schema='second')
        
        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='first')
        self.assertEquals('None', resp.content)
        
    
    def test_invalid_schema(self):
        first = Schema.objects.create(name='first', schema='first')
        second = Schema.objects.create(name='second', schema='second')
        
        user = User.objects.create_superuser(
            username="su",
            password="su",
            email="su@example.com"
        )
        self.client.login(username='su', password='su')
        
        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='third')
        self.assertEquals('None', resp.content)
        
        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='second')
        self.assertEquals('second', resp.content)
        
        self.client.get('/__change_schema__/third/')
        resp = self.client.get('/')
        self.assertEquals('None', resp.content)
    
    
    def test_only_one_available_schema(self):
        first = Schema.objects.create(name='first', schema='first')
        self.assertEquals(1, Schema.objects.count())
        
        user = User.objects.create_superuser(
            username="su",
            password="su",
            email="su@example.com"
        )
        self.client.login(username='su', password='su')
        resp = self.client.get('/')
        self.assertEquals('first', resp.content)

        
    def test_middleware_activation(self):
        first = Schema.objects.create(name='first', schema='first')
        second = Schema.objects.create(name='second', schema='second')
        
        user = User.objects.create_superuser(
            username="su",
            password="su",
            email="su@example.com"
        )
        
        self.client.login(username='su', password='su')
                
        self.client.get('/__change_schema__/second/')
        resp = self.client.get('/')
        self.assertEquals('second', resp.content)
        
        resp = self.client.get('/', {'__schema':'first'}, follow=True)
        self.assertEquals('first', resp.content)
        
        resp = self.client.get('/', {'__schema':'second', 'foo': 'bar'}, follow=True)
        self.assertEquals('second\nfoo=bar', resp.content)
        
        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='first')
        self.assertEquals('first', resp.content)
    
    def test_non_superuser_schemata(self):
        Schema.objects.mass_create('a','b','c')
        user = User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/', {'__schema': 'a'}, follow=True)
        self.assertEquals('None', resp.content)
        
        user.schemata.add(Schema.objects.get(schema='a'))
        resp = self.client.get('/')
        self.assertEquals('a', resp.content)
        
        user.schemata.add(Schema.objects.get(schema='c'))
        resp = self.client.get('/')
        self.assertEquals('a', resp.content)

    def test_exception_caused_by_no_active_schema(self):
        Schema.objects.create(schema='a', name='a').activate()
        AwareModel.objects.create(name='foo')
        AwareModel.objects.create(name='bar')
        
        user = User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/')
        self.assertEquals('None', resp.content)
        
        resp = self.client.get('/aware/')
        self.assertEquals(449, resp.status_code)
    
    def test_attempt_to_activate_template_schema(self):
        user = User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        
        resp = self.client.get('/', {'__schema': '__template__'}, follow=True)
        self.assertEquals(403, resp.status_code)
        
        resp = self.client.get('/__change_schema__/__template__/')
        self.assertEquals(403, resp.status_code)
        
        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='__template__')
        self.assertEquals(403, resp.status_code)
                
class TestContextProcessor(TestCase):
    def setUp(self):
        Schema.objects.mass_create('a','b','c')
    
    def test_no_schemata_if_anonymous(self):
        response = self.client.get('/change/')
        self.assertNotIn('schemata', response.context)
        self.assertNotIn('selected_schema', response.context)
    
    def test_schemata_in_context(self):
        user = User.objects.create_user(**CREDENTIALS)
        schemata = Schema.objects.exclude(schema='b')
        user.schemata.add(*schemata)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/change/')
        self.assertEquals(2, len(resp.context['schemata']))
        self.assertIn(schemata[0], resp.context['schemata'])
        self.assertIn(schemata[1], resp.context['schemata'])
        self.assertEquals(None, resp.context['selected_schema'])
        
        resp = self.client.get('/change/',  HTTP_X_CHANGE_SCHEMA='a')
        self.assertEquals(2, len(resp.context['schemata']))
        self.assertIn(schemata[0], resp.context['schemata'])
        self.assertIn(schemata[1], resp.context['schemata'])
        self.assertEquals('a', resp.context['selected_schema'])
    
    def user_has_no_schemata(self):
        user = User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/change/')
        self.assertEquals([], list(resp.context['schemata']))
        