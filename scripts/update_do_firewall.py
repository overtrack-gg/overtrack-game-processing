import os
import socket

import digitalocean

DO_ACCESS_KEY = os.environ['DO_ACCESS_KEY']
FIREWALL_ID = os.environ.get('FIREWALL_ID', '6dd53f97-bd41-4ebd-974e-bab6782d0790')


def main() -> None:
    firewall = digitalocean.Firewall.get_object(api_token=DO_ACCESS_KEY, firewall_id=FIREWALL_ID)

    for addresses in [i.sources.addresses for i in firewall.inbound_rules]:
        if len(addresses) == 1 and '/' not in addresses[0]:
            print('removing', addresses)
            firewall.get_data(
                f'firewalls/{firewall.id}/rules',
                'DELETE',
                {
                    'inbound_rules': [
                        {
                            'protocol': 'tcp',
                            'ports': 'all',
                            'sources': {
                                'addresses': addresses
                            }
                        }
                    ]
                }
            )

    my_ip = socket.gethostbyname('home.uint8.me')
    print('adding', my_ip)
    firewall.get_data(
        f'firewalls/{firewall.id}/rules',
        'POST',
        {
            'inbound_rules': [
                {
                    'protocol': 'tcp',
                    'ports': 'all',
                    'sources': {
                        'addresses': [
                            my_ip
                        ]
                    }
                }
            ]
        }
    )


if __name__ == '__main__':
    main()
