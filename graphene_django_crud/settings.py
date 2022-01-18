from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

DEFAULTS = {
    # Customize
    "DEFAULT_CONNECTION_NODES_FIELD_NAME": "data",
    "FILE_TYPE_CONTENT_FIELD_ACTIVE": False,
    "CONVERT_ENUM_FIELDS": True,
    # Compatibility with old version
    "SCALAR_FILTERS_ADD_EQUALS_FIELD": False,
    "BOOLEAN_FILTER_USE_BOOLEAN_FIELD": False,
}

IMPORT_STRINGS = ()


def perform_import(value, setting_name):
    if isinstance(value, str):
        return import_from_string(value, setting_name)
    if isinstance(value, (list, tuple)):
        return [import_from_string(item, setting_name) for item in value]
    return value


def import_from_string(value, setting_name):
    try:
        return import_string(value)
    except ImportError as e:
        msg = (
            f"Could not import `{value}` for GRAPHENE_DJANGO_CRUD setting `{setting_name}`."
            f"{e.__class__.__name__}: {e}."
        )
        raise ImportError(msg)


class GDCSettings:
    def __init__(self, defaults, import_strings):
        self.defaults = defaults
        self.import_strings = import_strings
        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid setting: `{attr}`")

        value = self.user_settings.get(attr, self.defaults[attr])

        if attr in self.import_strings:
            value = perform_import(value, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, value)
        return value

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "GRAPHENE_DJANGO_CRUD", {})
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)

        self._cached_attrs.clear()

        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


def reload_settings(*args, **kwargs):
    setting = kwargs["setting"]

    if setting == "GRAPHENE_DJANGO_CRUD":
        gdc_settings.reload()


setting_changed.connect(reload_settings)

gdc_settings = GDCSettings(DEFAULTS, IMPORT_STRINGS)
