from .default import list_view, detail_view, create_view, update_view


def includeme(config):
    """List of views to include for the config."""
    config.add_view(list_view, route_name="home")
    config.add_view(detail_view, route_name="entry")
    config.add_view(create_view, route_name="create")
    config.add_view(update_view, route_name="edit")
