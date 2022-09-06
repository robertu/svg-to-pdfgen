# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=import-error

from django.apps import AppConfig


class Svg2PdfConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "svg2pdf"
