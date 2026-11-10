import shutil
import tempfile

from django.test import override_settings

from home.models import (
    Footer,
    FooterLien,
    FooterReseau,
    Header,
    HeaderLien,
    HomePage,
    HomeRealisation,
    PageContenu,
)

from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase


class HomeSetUpTests(WagtailPageTestCase):
    """
    Tests for basic page structure setup and HomePage creation.
    """

    def test_root_create(self):
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_create(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home").exists())


class HomeTests(WagtailPageTestCase):
    """
    Tests for homepage functionality and rendering.
    """

    def setUp(self):
        """
        Create a homepage instance for testing.
        """
        root_page = Page.get_first_root_node()
        Site.objects.create(hostname="testsite", root_page=root_page, is_default_site=True)
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)

    def test_homepage_is_renderable(self):
        self.assertPageIsRenderable(self.homepage)

    def test_homepage_template_used(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")


class HeaderFooterTests(WagtailPageTestCase):
    """
    Tests for the dynamic header and footer shown on every page.
    """

    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", root_page=self.homepage, is_default_site=True)
        self.mentions = PageContenu(title="Mentions", slug="mentions", contenu="<p>Editeur</p>")
        self.homepage.add_child(instance=self.mentions)

        self.header = Header.objects.create(nom="Nom du header")
        HeaderLien.objects.create(header=self.header, titre="Lien header", page=self.mentions)
        self.footer = Footer.objects.create(texte="Texte du footer", page_mentions_legales=self.mentions)
        FooterLien.objects.create(footer=self.footer, titre="Lien footer", page=self.mentions)
        FooterReseau.objects.create(footer=self.footer, nom="Instagram", url="https://instagram.com/test")

    def assertHeaderFooter(self, response, status_code=200):
        for text in ["Nom du header", "Lien header", "Texte du footer", "Lien footer", "Instagram", "Mentions légales"]:
            self.assertContains(response, text, status_code=status_code)

    def test_shown_on_every_page(self):
        self.assertHeaderFooter(self.client.get(self.homepage.url))
        self.assertHeaderFooter(self.client.get(self.mentions.url))
        self.assertHeaderFooter(self.client.get("/search/"))
        self.assertHeaderFooter(self.client.get("/page-inexistante/"), status_code=404)

    def test_copyright(self):
        from datetime import date

        self.assertContains(
            self.client.get(self.homepage.url),
            f"&copy; {date.today().year} JARDIM JIM ARCHITECTURAL DESIGN. Tous droits réservés.",
        )

    def test_sans_copyright(self):
        self.footer.copyright = ""
        self.footer.save()
        self.assertNotContains(self.client.get(self.homepage.url), "footer-copyright")

    def test_stylesheet_loaded(self):
        self.assertContains(self.client.get(self.homepage.url), "css/mysite.css")

    def test_unpublished_page_is_hidden(self):
        self.mentions.unpublish()
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Lien header")
        self.assertNotContains(response, "Lien footer")
        self.assertNotContains(response, "Mentions légales")

    def test_without_header_and_footer(self):
        Header.objects.all().delete()
        Footer.objects.all().delete()
        response = self.client.get(self.homepage.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<footer>")


class HomeContentTests(WagtailPageTestCase):
    """
    Tests for the content of the homepage, editable from Wagtail.
    """

    def setUp(self):
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root, ignore_errors=True)
        media_settings = override_settings(MEDIA_ROOT=media_root)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", root_page=self.homepage, is_default_site=True)
        self.methode = PageContenu(title="Methode", slug="methode")
        self.homepage.add_child(instance=self.methode)
        self.image = get_image_model().objects.create(
            title="photo.png", file=get_test_image_file(), description="Maison en bois"
        )

    def test_empty_homepage_has_no_broken_parts(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "<h1>Vos plans d&#x27;architecture en Gironde</h1>", html=True)
        self.assertContains(response, "metier-sans-image")
        self.assertNotContains(response, 'class="bouton"')
        self.assertNotContains(response, "<ul>")

    def test_filled_homepage(self):
        self.homepage.accroche_image = self.image
        self.homepage.metier_image = self.image
        self.homepage.metier_lien_page = self.methode
        self.homepage.realisations_lien_page = self.methode
        self.homepage.save()
        HomeRealisation.objects.create(page=self.homepage, image=self.image, description="Extension bois")

        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'alt=""', count=1)
        self.assertContains(response, 'alt="Maison en bois"', count=2)
        self.assertContains(response, "srcset=", count=3)
        self.assertContains(response, "<figcaption>Extension bois</figcaption>")
        self.assertContains(response, 'href="/methode/"', count=2)

    def test_button_hidden_when_page_is_unpublished(self):
        self.homepage.metier_lien_page = self.methode
        self.homepage.save()
        self.methode.unpublish()
        self.assertNotContains(self.client.get(self.homepage.url), 'class="bouton"')
