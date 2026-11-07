from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel


# Modèles des pages du site (hors page d'accueil, qui reste dans l'app "home").
# Chaque modèle de page utilise le template pages/templates/pages/<nom_du_modele>.html


class RealisationsPage(Page):
    """Page « Mes réalisations » : liste les projets (pages enfants)."""

    introduction = RichTextField(
        "Introduction",
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Texte facultatif affiché sous le titre.",
    )
    lien_texte = models.CharField(
        "Texte du bouton des projets", max_length=50, default="En savoir plus"
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("lien_texte"),
    ]

    # Seuls des projets peuvent être créés sous cette page
    subpage_types = ["pages.RealisationPage"]

    class Meta:
        verbose_name = "Page des réalisations"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["projets"] = (
            RealisationPage.objects.child_of(self).live().specific()
        )
        return context


class RealisationPage(Page):
    """Un projet réalisé, affiché en détail."""

    infos = models.CharField(
        "Infos courtes",
        max_length=150,
        blank=True,
        help_text="Affichées dans la liste des réalisations "
        "(ex. : Maison individuelle, Bordeaux, 2025).",
    )
    texte = RichTextField(
        "Explication du projet",
        blank=True,
        features=["h2", "h3", "bold", "italic", "ol", "ul", "link"],
    )

    content_panels = Page.content_panels + [
        FieldPanel("infos"),
        InlinePanel(
            "images",
            label="Image",
            min_num=1,
            help_text="La première image sert de vignette dans la liste.",
        ),
        FieldPanel("texte"),
    ]

    parent_page_types = ["pages.RealisationsPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Réalisation"

    @property
    def vignette(self):
        premiere = self.images.first()
        return premiere.image if premiere else None


class RealisationImage(Orderable):
    page = ParentalKey(
        "RealisationPage", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Pensez à remplir la description de l'image : "
        "elle est lue par les lecteurs d'écran.",
    )

    panels = [
        FieldPanel("image"),
    ]
