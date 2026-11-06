from django import template

from home.models import Footer, Header

register = template.Library()


@register.inclusion_tag("includes/header.html", takes_context=True)
def site_header(context):
    header = Header.objects.first()
    return {
        "request": context.get("request"),
        "header": header,
        "liens": header.liens.filter(page__live=True).select_related("page") if header else [],
    }


@register.inclusion_tag("includes/footer.html", takes_context=True)
def site_footer(context):
    footer = Footer.objects.first()
    return {
        "request": context.get("request"),
        "footer": footer,
        "liens": footer.liens.filter(page__live=True).select_related("page") if footer else [],
        "reseaux": footer.reseaux.select_related("logo") if footer else [],
    }
