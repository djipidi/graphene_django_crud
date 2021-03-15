from django.apps import AppConfig


class GDCTestConfig(AppConfig):
    label = 'gdc_test'
    name = 'tests'

    
    def ready(self):
        from . import signals