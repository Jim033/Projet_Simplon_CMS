from django import template

from home.models import Footer, Header

register = template.Library()


def page_courante(context):
    """Infos sur la page affichée, pour désactiver le lien vers la page où l'on est déjà."""
    return {
        "request": context.get("request"),
        "page_courante_id": getattr(context.get("page"), "id", None),
    }


@register.inclusion_tag("includes/header.html", takes_context=True)
def site_header(context):
    header = Header.objects.first()
    return {
        **page_courante(context),
        "header": header,
        "liens": header.liens.filter(page__live=True).select_related("page") if header else [],
    }


@register.inclusion_tag("includes/footer.html", takes_context=True)
def site_footer(context):
    footer = Footer.objects.first()
    return {
        **page_courante(context),
        "footer": footer,
        "liens": footer.liens.filter(page__live=True).select_related("page") if footer else [],
        "reseaux": footer.reseaux.select_related("logo") if footer else [],
    }
