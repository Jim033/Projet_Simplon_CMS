from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
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
    accroche_titre = models.CharField(
        "Titre", max_length=120, default="Vos plans d'architecture en Gironde"
    )
    accroche_texte = models.CharField(
        "Phrase d'accroche",
        max_length=255,
        default="Plans, permis de construire et maquettes 2D et 3D "
        "pour les particuliers et les professionnels.",
    )
    accroche_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image de fond",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    metier_titre = models.CharField("Titre", max_length=120, default="Mon métier")
    metier_texte = RichTextField(
        "Texte",
        features=["bold", "italic", "link"],
        default="<p>Dessinateur en plans d'architecture, je réalise vos dossiers "
        "de permis de construire, vos maquettes numériques 2D et 3D, vos rendus "
        "et visites virtuelles ainsi que les métrés de vos rénovations.</p>",
    )
    metier_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Pensez à remplir la description de l'image : "
        "elle est lue par les lecteurs d'écran.",
    )
    metier_lien_texte = models.CharField(
        "Texte du bouton", max_length=50, default="En savoir plus"
    )
    metier_lien_page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name="Page du bouton",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    realisations_titre = models.CharField(
        "Titre", max_length=120, default="Mes réalisations"
    )
    realisations_lien_texte = models.CharField(
        "Texte du bouton", max_length=50, default="Voir toutes les réalisations"
    )
    realisations_lien_page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name="Page du bouton",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("accroche_titre"),
                FieldPanel("accroche_texte"),
                FieldPanel("accroche_image"),
            ],
            heading="Partie 1 : accroche",
        ),
        MultiFieldPanel(
            [
                FieldPanel("metier_titre"),
                FieldPanel("metier_texte"),
                FieldPanel("metier_image"),
                FieldPanel("metier_lien_texte"),
                FieldPanel("metier_lien_page"),
            ],
            heading="Partie 2 : métier",
        ),
        MultiFieldPanel(
            [
                FieldPanel("realisations_titre"),
                InlinePanel("realisations", label="Réalisation", max_num=4),
                FieldPanel("realisations_lien_texte"),
                FieldPanel("realisations_lien_page"),
            ],
            heading="Partie 3 : réalisations",
        ),
    ]


class HomeRealisation(Orderable):
    page = ParentalKey(
        "HomePage", on_delete=models.CASCADE, related_name="realisations"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    description = models.CharField(max_length=100)

    panels = [
        FieldPanel("image"),
        FieldPanel("description"),
    ]


class PageContenu(Page):
    contenu = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("contenu"),
    ]

    template = "home/page_contenu.html"
