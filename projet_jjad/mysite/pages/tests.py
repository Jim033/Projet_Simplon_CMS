from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from pages.models import Tarif, TarifElement, TarifsPage, TarifsPageTarif


class TarifsPageTests(WagtailPageTestCase):
    """Tests de la page des tarifs et des snippets Tarif."""

    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", root_page=self.homepage, is_default_site=True)

        self.page = TarifsPage(
            title="Tarifs",
            slug="tarifs",
            sous_titre="Des packs adaptés à votre projet",
            remarque="Tarifs indicatifs, devis sur mesure.",
        )
        self.homepage.add_child(instance=self.page)

        self.tarif = Tarif.objects.create(titre="Pack permis", texte="Pour votre maison", prix="À partir de 450 €")
        TarifElement.objects.create(tarif=self.tarif, texte="Plans 2D", sort_order=0)
        TarifElement.objects.create(tarif=self.tarif, texte="Dossier de permis", sort_order=1)
        TarifsPageTarif.objects.create(page=self.page, tarif=self.tarif, sort_order=0)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.page)

    def test_template_used(self):
        response = self.client.get(self.page.url)
        self.assertTemplateUsed(response, "pages/tarifs_page.html")

    def test_contenu_affiche(self):
        response = self.client.get(self.page.url)
        for texte in [
            "Tarifs",
            "Des packs adaptés à votre projet",
            "Pack permis",
            "Plans 2D",
            "Dossier de permis",
            "Pour votre maison",
            "À partir de 450 €",
            "Tarifs indicatifs, devis sur mesure.",
        ]:
            self.assertContains(response, texte)

    def test_sans_tarif(self):
        TarifsPageTarif.objects.all().delete()
        self.assertContains(self.client.get(self.page.url), "Aucun tarif pour le moment.")
