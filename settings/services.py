from settings.models import Setting


def get_settings():
    return Setting.objects.all()


def get_setting(property):
    return Setting.objects.get(property=property).value
