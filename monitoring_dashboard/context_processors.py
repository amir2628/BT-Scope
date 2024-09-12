
def site_context(request):
    return {
        'site_title': 'My Site',
        'site_header': 'My Site Header',
        'is_popup': False,
        'is_nav_sidebar_enabled': True,
    }
