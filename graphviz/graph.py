import sys
from graphviz import Digraph
from state import *


def usage():
    print 'USAGE: graph.py -c cluster|freeform'
    sys.exit()

if len(sys.argv) < 3:
    usage()

context = sys.argv[2]

if context == 'cluster':
    namespace = 'cluster_'
    output = 'cluster'
elif context == 'freeform':
    namespace = 'group_'
    output = 'freeform'
else:
    print('Invalid context')
    usage()


g = Digraph('G', filename=output + '.gv')
g.attr(compound='true')
g.edge_attr.update(minlen='2')

g.node('internet', shape='doublecircle')
g.node('cloudflare', shape='star')

with g.subgraph(name=namespace + 'cloud') as cloud:
    cloud.attr(label='Cloud')

    render_gclb(cloud)

    with cloud.subgraph(name=namespace + 'haproxy') as haproxy:
        haproxy.attr(label='HAProxy')
        render(haproxy, 'haproxy')

    gen_links(cloud, 'cloud', context=context)

render(g, 'bastion')
render(g, 'deployer')


with g.subgraph(name=namespace + 'build') as build:

    with build.subgraph(name=namespace + 'slaves') as slaves:
        slaves.attr(label='Build Slaves')
        slaves.node(namespace + 'slaves_ref', shape='point', style='invis')

        with slaves.subgraph(name=namespace + 'elixir') as elixir:
            def node_elixir(c, v):
                c.node('build-elixir-' + str(v))
            render(elixir, 'elixir')

        with slaves.subgraph(name=namespace + 'build_helix') as build_helix:
            render(build_helix, 'build_helix')

        with slaves.subgraph(name=namespace + 'elm') as elm:
            render(elm, 'elm')

    with build.subgraph(name=namespace + 'build_database') as build_database:
        render(build_database, 'build_database')

    with build.subgraph(name=namespace + 'nginx_build') as nginx_build:
        render(nginx_build, 'nginx_build')

    with build.subgraph(name=namespace + 'jenkins') as jenkins:
        render(jenkins, 'jenkins')

    gen_links(build, 'build', context=context)

    build.attr(label='Build')


with g.subgraph(name=namespace + 'prod') as prod:
    prod.attr(label='Production')

    with prod.subgraph(name=namespace + 'migration') as migration:
        render(migration, 'migration')

    with prod.subgraph(name=namespace + 'helix') as helix:
        render(helix, 'helix')

    with prod.subgraph(name=namespace + 'database') as database:
        render(database, 'database')

    with prod.subgraph(name=namespace + 'heborn') as heborn:
        render(heborn, 'heborn')

    gen_links(prod, 'prod', context=context)

with g.subgraph(name=namespace + 'dev') as dev:
    dev.attr(label='Development')

    with dev.subgraph(name=namespace + 'interactive') as interactive:
        render(interactive, 'interactive')

with g.subgraph(name=namespace + 'infra') as infra:
    infra.attr(label='Infra')

    with infra.subgraph(name=namespace + 'nginx_infra') as nginx_infra:
        render(nginx_infra, 'nginx_infra')

    with infra.subgraph(name=namespace + 'wiki') as wiki:
        render(wiki, 'wiki')

    with infra.subgraph(name=namespace + 'blog') as blog:
        render(blog, 'blog')

    gen_links(infra, 'infra', context=context)


gen_links(g, 'global', context=context)


g.view()

