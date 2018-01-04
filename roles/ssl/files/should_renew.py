from datetime import datetime
import socket
import time
import ssl
import sys

def get_cert_expiration(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    conn.settimeout(5.0)
    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    conn.close()
    return datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)


def should_renew(hostname, attempts = 0):
    try:
        diff = get_cert_expiration(hostname) - datetime.now()
        return diff.days <= 30

    # It's already expired
    except ssl.SSLError, e:
            return True

    # Some other exception, possibly a timeout
    except Exception, e:
        if e.message == 'timed out' and attempts < 3:
            time.sleep(1)
            return should_renew(hostname, attempts + 1)

        raise e

def usage():
    print "USAGE: should_renew.py site1 site2 siteN"
    sys.exit()

params = sys.argv[1:]

if not params:
    usage()

for site in params:
    if 'https://' in site:
        site = site[8:]

    if should_renew(site):
        print 'yes'
    else:
        print 'no'
