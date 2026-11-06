from home.models import Footer, FooterLien, FooterReseau, Header, HeaderLien, HomePage, PageContenu

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
