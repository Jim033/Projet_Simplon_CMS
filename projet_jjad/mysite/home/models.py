from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Header(ClusterableModel):
    nom = models.CharField(
        "Nom de l'entreprise",
        max_length=100,
        default="JARDIM JIM ARCHITECTURAL DESIGN",
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("nom"),
        FieldPanel("logo"),
        InlinePanel("liens", label="Lien de navigation"),
    ]

    def __str__(self):
        return self.nom


class HeaderLien(Orderable):
    header = ParentalKey(
        "Header", on_delete=models.CASCADE, related_name="liens"
    )
    titre = models.CharField(max_length=50)
    page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        FieldPanel("titre"),
        FieldPanel("page"),
    ]


@register_snippet
class Footer(ClusterableModel):
    texte = models.TextField(
        "Texte", default="JARDIM JIM\nARCHITECTURAL DESIGN"
    )
    texte_mentions_legales = models.CharField(
        "Texte du lien des mentions légales",
        max_length=50,
        default="Mentions légales",
    )
    page_mentions_legales = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("texte"),
        InlinePanel("liens", label="Lien de navigation"),
        InlinePanel("reseaux", label="Réseau social"),
        FieldPanel("texte_mentions_legales"),
        FieldPanel("page_mentions_legales"),
    ]

    def __str__(self):
        return "Footer"


class FooterLien(Orderable):
    footer = ParentalKey(
        "Footer", on_delete=models.CASCADE, related_name="liens"
    )
    titre = models.CharField(max_length=50)
    page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        FieldPanel("titre"),
        FieldPanel("page"),
    ]


class FooterReseau(Orderable):
    footer = ParentalKey(
        "Footer", on_delete=models.CASCADE, related_name="reseaux"
    )
    nom = models.CharField(max_length=50)
    url = models.URLField()
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("nom"),
        FieldPanel("url"),
        FieldPanel("logo"),
    ]


class HomePage(Page):
    pass


class PageContenu(Page):
    contenu = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("contenu"),
    ]

    template = "home/page_contenu.html"
