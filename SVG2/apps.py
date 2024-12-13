from django.apps import AppConfig


class Svg2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SVG2'

    def ready(self):
        import SVG2.signals