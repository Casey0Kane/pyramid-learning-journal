def includeme(config):
    config.add_static_view(name='static', path='learning_journal:static')
    config.add_route('home', '/')
    config.add_route('detail', '/journal/{id:\d+}')
    config.add_route('create', '/journal/new-entry')
    config.add_route('update', '/journal/{id:\d+}/edit-entry')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('api_list', '/api/v1/journal')
