from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet


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


@register_snippet
class Tarif(ClusterableModel):
    """Un pack de prestations (snippet), réutilisable sur la page des tarifs."""

    titre = models.CharField("Titre", max_length=100)
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Petit logo affiché en haut du pack.",
    )
    texte = models.TextField("Texte", blank=True)
    prix = models.CharField(
        "Tarif", max_length=100, help_text="Ex. : « À partir de 450 € »."
    )

    panels = [
        FieldPanel("titre"),
        FieldPanel("logo"),
        InlinePanel("elements", label="Ce qui est compris dans le pack"),
        FieldPanel("texte"),
        FieldPanel("prix"),
    ]

    class Meta:
        verbose_name = "Tarif"

    def __str__(self):
        return self.titre


class TarifElement(Orderable):
    """Une ligne de la liste « ce qui est compris » d'un pack."""

    tarif = ParentalKey(Tarif, on_delete=models.CASCADE, related_name="elements")
    texte = models.CharField("Élément compris", max_length=150)

    panels = [
        FieldPanel("texte"),
    ]


class TarifsPage(Page):
    """Page « Tarifs » : titre, sous-titre, les packs choisis et une remarque."""

    sous_titre = models.CharField("Sous-titre", max_length=255, blank=True)
    remarque = models.TextField(
        "Remarque",
        blank=True,
        help_text="Texte mis en avant sous les tarifs (ex. : tarifs indicatifs, devis sur mesure).",
    )

    content_panels = Page.content_panels + [
        FieldPanel("sous_titre"),
        InlinePanel("tarifs", label="Tarif", max_num=3),
        FieldPanel("remarque"),
    ]

    subpage_types = []

    class Meta:
        verbose_name = "Page des tarifs"


class TarifsPageTarif(Orderable):
    """Lien entre la page des tarifs et un snippet Tarif (permet de choisir l'ordre)."""

    page = ParentalKey(TarifsPage, on_delete=models.CASCADE, related_name="tarifs")
    tarif = models.ForeignKey(Tarif, on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("tarif"),
    ]


@register_snippet
class Etape(models.Model):
    """Une étape de la méthode de travail (snippet), affichée sur la page « Méthode »."""

    titre = models.CharField("Titre", max_length=100)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Pensez à remplir la description de l'image : "
        "elle est lue par les lecteurs d'écran.",
    )
    texte = models.TextField("Explications", blank=True)

    panels = [
        FieldPanel("titre"),
        FieldPanel("image"),
        FieldPanel("texte"),
    ]

    class Meta:
        verbose_name = "Étape de la méthode"
        verbose_name_plural = "Étapes de la méthode"

    def __str__(self):
        return self.titre


class MethodePage(Page):
    """Page « Ma méthode » : les étapes choisies, puis un texte complémentaire."""

    complement_titre = models.CharField(
        "Titre du texte complémentaire",
        max_length=150,
        blank=True,
        help_text="Ex. : « Les mairies et délais d'attente ».",
    )
    complement_texte = RichTextField(
        "Texte complémentaire",
        blank=True,
        features=["bold", "italic", "ul", "link"],
    )

    content_panels = Page.content_panels + [
        InlinePanel(
            "etapes",
            label="Étape",
            max_num=3,
            help_text="Les étapes sont numérotées dans l'ordre choisi ici.",
        ),
        FieldPanel("complement_titre"),
        FieldPanel("complement_texte"),
    ]

    subpage_types = []

    class Meta:
        verbose_name = "Page de la méthode"


class MethodePageEtape(Orderable):
    """Lien entre la page « Méthode » et un snippet Étape (permet de choisir l'ordre)."""

    page = ParentalKey(MethodePage, on_delete=models.CASCADE, related_name="etapes")
    etape = models.ForeignKey(Etape, on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("etape"),
    ]
