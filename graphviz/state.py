def node(c, info, v):
    hostname = '{}-{}'.format(info['hostname'], str(v))

    ip = []
    if 'public_ip' in info:
        ip.append(info['public_ip'])
    if info['subnet']:
        ip.append('{}.{}'.format(info['subnet'], str(info['start_at'] + v - 1)))
    if not ip:
        ip.append('(hidden)')

    dns = []
    if 'dns' in info:
        if isinstance(info['dns'], list):
            dns = info['dns']

            for entry in dns:
                if entry == hostname:
                    dns = [entry]
                    break

        else:
            dns.append(info['dns'])

    if dns:
        formatted_dns = '\n' + '\n'.join(dns)
    else:
        formatted_dns = ''

    formatted_ip = '\n'.join(ip)

    c.node(
        hostname,
        label='{}\n{}{}'.format(hostname, formatted_ip, formatted_dns),
        rank='min'
    )

role_info = {
    'haproxy': {
        'hostname': 'haproxy',
        'subnet': False,
        'count': 4,
        'label': 'HAProxy'
    },
    'bastion': {
        'hostname': 'bastion',
        'subnet': '192.168.1',
        'start_at': 10,
        'public_ip': '144.217.245.111',
        'count': 1,
        'dns': 'bastion.hackerexperience.com'
    },
    'nginx_infra': {
        'hostname': 'nginx-infra',
        'subnet': '192.168.10',
        'start_at': 10,
        'count': 1,
        'label': 'Nginx Infra'
    },
    'nginx_build': {
        'hostname': 'nginx-build',
        'subnet': '192.168.19',
        'start_at': 10,
        'count': 1,
        'label': 'Nginx Build'
    },
    'jenkins': {
        'hostname': 'jenkins',
        'subnet': '192.168.20',
        'start_at': 10,
        'count': 1,
        'dns': 'ci.hackerexperience.com',
        'label': 'Jenkins Master'
    },
    'elixir': {
        'hostname': 'build-elixir',
        'subnet': '192.168.21',
        'start_at': 10,
        'count': 4,
        'label': 'Build (elixir)'
    },
    'build_helix': {
        'hostname': 'build-helix',
        'subnet': '192.168.22',
        'start_at': 10,
        'count': 1,
        'label': 'Build (Helix)'
    },
    'build_database': {
        'hostname': 'build-database',
        'subnet': '192.168.23',
        'start_at': 10,
        'count': 1,
        'label': 'Build database'
    },
    'elm': {
        'hostname': 'build-elm',
        'subnet': '192.168.24',
        'start_at': 10,
        'count': 1,
        'label': 'Build (Elm)'
    },
    'wiki': {
        'hostname': 'wiki',
        'subnet': '192.168.70',
        'start_at': 10,
        'count': 1,
        'dns': ['gd.', 'architecture.'],
        'label': 'Wiki'
    },
    'blog': {
        'hostname': 'blog',
        'subnet': '192.168.71',
        'start_at': 10,
        'count': 2,
        'dns': ['leaks.', 'engineering.'],
        'label': 'Blog'
    },
    'deployer': {
        'hostname': 'deployer',
        'subnet': '192.168.99',
        'start_at': 99,
        'count': 1
    },
    'helix': {
        'hostname': 'helix',
        'subnet': '192.168.101',
        'start_at': 10,
        'count': 1,
        'label': 'Helix'
    },
    'database': {
        'hostname': 'database',
        'subnet': '192.168.110',
        'start_at': 10,
        'count': 1,
        'label': 'Database'
    },
    'migration': {
        'hostname': 'migrate',
        'subnet': '192.168.179',
        'start_at': 10,
        'count': 1,
        'label': 'HEBorn Migration',
        'dns': 'migrate.hackerexperience.com'
    },
    'heborn': {
        'hostname': 'heborn',
        'subnet': '192.168.180',
        'start_at': 10,
        'count': 1,
        'dns': '1.hackerexperience.com',
        'label': 'HEBorn (HE1)'
    },
    'interactive': {
        'hostname': 'interactive',
        'subnet': '192.168.250',
        'start_at': 10,
        'count': 2,
        'label': 'Interactive Staging',
        'dns': ['interactive-1', 'interactive-2']
    }
}

def color_link_internet():
    return 'red'

def color_link_google():
    return 'blue'

def color_link_cloudflare():
    return 'orange'

def color_link_lan():
    return 'green4'

def color_link_bastion():
    return 'grey'

def color_link_deployer():
    return 'magenta'

def color_link_office():
    return 'gray15'

env_links = {
    'prod': [
        ('helix', 'database', 'mn', ('cluster_helix', 'cluster_database', ''), ['all']),
        ('migration', 'database', 'mn', ('cluster_migration', 'cluster_database', ''), ['all'])
    ],
    'infra': [
        ('nginx_infra', 'wiki', 'mn', ('cluster_nginx_infra', 'cluster_wiki', ''), ['all']),
        ('nginx_infra', 'blog', 'mn', ('cluster_nginx_infra', 'cluster_blog', ''), ['all'])
    ],
    'build': [
        ('build_helix', 'build_database', 'mn', ('cluster_build_helix', 'cluster_build_database', ''), ['all']),
        ('nginx_build', 'jenkins', 'mn', ('', 'cluster_jenkins', ''), ['all']),
        ('jenkins', 'elm', 'mn', ('cluster_jenkins', 'cluster_elm', ''), ['all']),
        ('jenkins', 'build_helix', 'mn', ('cluster_jenkins', 'cluster_build_helix', ''), ['all']),
        ('jenkins', 'elixir', 'mn', ('cluster_jenkins', 'cluster_elixir', ''), ['all']),
    ],
    'cloud': [
        ('gclb', 'haproxy', 'n', ('', 'cluster_haproxy', color_link_google()), ['all'])
    ],
    'global': [

        # Internet
        ('internet', 'gclb', '1', ('', '', color_link_internet()), ['all']),
        ('internet', 'cloudflare', '1', ('', '', color_link_internet()), ['all']),
        ('internet', 'bastion', 'n', ('', '', color_link_internet()), ['all']),

        ('office', 'bastion', 'n', ('', '', color_link_office()), ['all']),

        # Gclb
        ('haproxy', 'helix', 'mn', ('cluster_haproxy', 'cluster_helix', color_link_google()), ['all']),

        # Cloudflare
        ('cloudflare', 'heborn', 'n', ('', 'cluster_heborn', color_link_cloudflare()), ['all']),
        ('cloudflare', 'migration', 'n', ('', 'cluster_migration', color_link_cloudflare()), ['all']),
        ('cloudflare', 'nginx_infra', 'n', ('', 'cluster_nginx_infra', color_link_cloudflare()), ['all']),
        ('cloudflare', 'nginx_build', 'n', ('', 'cluster_nginx_build', color_link_cloudflare()), ['all']),
        ('cloudflare', 'interactive', 'n', ('', 'cluster_interactive', color_link_cloudflare()), ['all']),

        # Bastion
        ('bastion', 'nginx_infra', 'mn', ('', 'cluster_infra', color_link_bastion()), ['all']),
        ('bastion', 'nginx_build', 'mn', ('', 'cluster_build', color_link_bastion()), ['all']),
        ('bastion', 'helix', 'mn', ('', 'cluster_prod', color_link_bastion()), ['all']),
        ('bastion', 'interactive', 'mn', ('', 'cluster_dev', color_link_bastion()), ['all']),
        ('bastion', 'deployer', 'mn', ('', '', color_link_bastion()), ['all']),
        ('bastion', 'jenkins', 'mn', ('', 'cluster_build', color_link_bastion()), ['freeform']),
        ('bastion', 'database', 'mn', ('', 'cluster_database', color_link_bastion()), ['freeform']),
        ('bastion', 'elixir', 'mn', ('', 'cluster_elixir', color_link_bastion()), ['freeform']),
        ('bastion', 'build_helix', 'mn', ('', 'cluster_build_helix', color_link_bastion()), ['freeform']),
        ('bastion', 'elm', 'mn', ('', 'cluster_elm', color_link_bastion()), ['freeform']),
        ('bastion', 'blog', 'mn', ('', 'cluster_blog', color_link_bastion()), ['freeform']),
        ('bastion', 'wiki', 'mn', ('', 'cluster_wiki', color_link_bastion()), ['freeform']),
        ('bastion', 'build_database', 'mn', ('', 'cluster_build_database', color_link_bastion()), ['freeform']),
        ('bastion', 'heborn', 'mn', ('', 'cluster_heborn', color_link_bastion()), ['freeform']),
        ('bastion', 'migration', 'mn', ('', 'cluster_migration', color_link_bastion()), ['freeform']),

        # Deployer
        ('elixir', 'deployer', 'mn', ('cluster_elixir', '', ''), ['all']),
        ('elm', 'deployer', 'mn', ('cluster_elm', '', ''), ['all']),
        ('deployer', 'deployer', 'mn', ('', '', color_link_deployer()), ['all']),
        ('deployer', 'helix', 'mn', ('', 'cluster_helix', color_link_deployer()), ['all']),
        ('deployer', 'migration', 'mn', ('', 'cluster_migration', color_link_deployer()), ['all']),
        ('deployer', 'interactive', 'mn', ('', 'cluster_interactive', color_link_deployer()), ['all']),
        ('deployer', 'heborn', 'mn', ('', 'cluster_heborn', color_link_deployer()), ['all']),
    ]
}

def render(c, role_name):
    info = role_info[role_name]

    if 'label' in info:
        c.attr(label=info['label'])

    for i in range(0, info['count']):
        node(c, info, i + 1)

def render_gclb(c):
    c.node('gclb',
           label='Google Cloud Load Balancer\nAnycast\napi.hackerexperience.com',
           shape='diamond')


def render_cloudflare(c):
    c.node('cloudflare',
           label='Cloudflare\nAnycast',
           shape='star')

def render_internet(c):
    c.node('internet',
           label='Internet\nWild Wild Web',
           shape='doublecircle')

def render_office(c):
    c.node('office',
           label='Office VPN\nLocal ISP',
           shape='folder')


def link(c, src, dest, ltail, lhead, **attr):
    c.edge(src, dest, ltail=ltail, lhead=lhead, **attr)

def link_1(c, src, dest, ltail='', lhead='', **attr):
    link(c, src, dest, ltail, lhead, **attr)

def link_n(c, src, dest_role, ltail='', lhead='', **attr):
    dest = role_info[dest_role]
    for i in range(0, dest['count']):
        dest_id = '{}-{}'.format(dest['hostname'], str(i + 1))
        link(c, src, dest_id, ltail=ltail, lhead=lhead, **attr)

def link_mn(c, src_role, dest_role, ltail='', lhead='', **attr):
    src = role_info[src_role]
    dest = role_info[dest_role]
    for s in range(0, src['count']):
        src_id = '{}-{}'.format(src['hostname'], str(s + 1))
        for d in range(0, dest['count']):
            dest_id = '{}-{}'.format(dest['hostname'], str(d + 1))
            link(c, src_id, dest_id, ltail, lhead, **attr)


def gen_links(c, env, context):
    links = env_links[env]
    for link_entry in links:
        (src, dest, mode, (ltail, lhead, color), allowed_ctx) = link_entry
        if mode == 'mn':
            f = link_mn
        elif mode == 'n':
            f = link_n
        else:
            f = link_1

        if context == 'freeform':
            ltail = lhead = ''
        elif context == 'cluster':
            f = link
            src = get_first_element(src)
            dest = get_first_element(dest)

        # Skip links that are not allowed within that context
        if 'all' not in allowed_ctx and context not in allowed_ctx:
            continue

        if color == '':
            color = color_link_lan()

        f(c, src, dest, ltail, lhead, **{'color': color})


def get_first_element(role):
    if role in ['cloudflare', 'gclb', 'internet', 'office']:
        return role

    hostname = role_info[role]['hostname']

    return hostname + '-1'
