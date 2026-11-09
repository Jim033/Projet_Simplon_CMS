from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from django.core import mail

from pages.models import (
    ContactChamp,
    ContactHoraire,
    ContactPage,
    Etape,
    MethodePage,
    MethodePageEtape,
    Tarif,
    TarifElement,
    TarifsPage,
    TarifsPageTarif,
)


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


class MethodePageTests(WagtailPageTestCase):
    """Tests de la page « Méthode » et des snippets Étape."""

    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", root_page=self.homepage, is_default_site=True)

        self.page = MethodePage(
            title="Ma méthode",
            slug="methode",
            complement_titre="Les mairies et délais d'attente",
            complement_texte="<p>Comptez deux mois d'instruction.</p>",
        )
        self.homepage.add_child(instance=self.page)

        premiere = Etape.objects.create(titre="Rencontre", texte="On parle du projet")
        deuxieme = Etape.objects.create(titre="Plans", texte="Je dessine les plans")
        MethodePageEtape.objects.create(page=self.page, etape=premiere, sort_order=0)
        MethodePageEtape.objects.create(page=self.page, etape=deuxieme, sort_order=1)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.page)

    def test_template_used(self):
        self.assertTemplateUsed(self.client.get(self.page.url), "pages/methode_page.html")

    def test_contenu_affiche(self):
        response = self.client.get(self.page.url)
        for texte in [
            "Ma méthode",
            "Étape 1",
            "Rencontre",
            "On parle du projet",
            "Étape 2",
            "Plans",
            "Je dessine les plans",
            "Les mairies et délais d&#x27;attente",
            "Comptez deux mois d'instruction.",
        ]:
            self.assertContains(response, texte)

    def test_sans_etape(self):
        MethodePageEtape.objects.all().delete()
        self.assertContains(self.client.get(self.page.url), "Aucune étape pour le moment.")


class ContactPageTests(WagtailPageTestCase):
    """Tests de la page « Contact » : affichage, envoi du formulaire et remerciement."""

    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", root_page=self.homepage, is_default_site=True)

        self.page = ContactPage(
            title="Contact",
            slug="contact",
            telephone="06 12 34 56 78",
            email_contact="contact@exemple.fr",
            texte_remerciement="<p>Merci pour votre message !</p>",
            to_address="jim@exemple.fr",
            from_address="site@exemple.fr",
            subject="Nouveau message",
        )
        self.homepage.add_child(instance=self.page)

        ContactChamp.objects.create(page=self.page, label="Nom", field_type="singleline", required=True, sort_order=0)
        ContactChamp.objects.create(page=self.page, label="Email", field_type="email", required=True, sort_order=1)
        ContactChamp.objects.create(page=self.page, label="Message", field_type="multiline", required=True, sort_order=2)
        ContactHoraire.objects.create(page=self.page, jour="Lundi", heures="9h/12h - 13h30/17h30", sort_order=0)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.page)

    def test_contenu_affiche(self):
        response = self.client.get(self.page.url)
        self.assertTemplateUsed(response, "pages/contact_page.html")
        for texte in [
            "Nom",
            "Email",
            "Message",
            'href="tel:0612345678"',
            "06 12 34 56 78",
            "mailto:contact@exemple.fr",
            "Lundi",
            "9h/12h - 13h30/17h30",
            "conservées 3 ans maximum",
        ]:
            self.assertContains(response, texte)

    def test_envoi_du_formulaire(self):
        response = self.client.post(
            self.page.url, {"nom": "Jean", "email": "jean@exemple.fr", "message": "Bonjour"}
        )
        self.assertTemplateUsed(response, "pages/contact_page_landing.html")
        self.assertContains(response, "Merci pour votre message !")
        self.assertEqual(self.page.get_submission_class().objects.filter(page=self.page).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["jim@exemple.fr"])

    def test_formulaire_incomplet(self):
        response = self.client.post(self.page.url, {"nom": "Jean"})
        self.assertTemplateUsed(response, "pages/contact_page.html")
        self.assertContains(response, "contact-erreur")
        self.assertEqual(len(mail.outbox), 0)
