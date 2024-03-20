import dns.resolver

def host2ipv6(hostname):
    try:
        results = dns.resolver.resolve(hostname, 'AAAA')
        ipv6_addresses = [result.address for result in results]
        return ipv6_addresses
    except Exception as e:
        return False
    

hostname = 'free-unlimited.hideservers.net'
ipv6 = host2ipv6(hostname)
print(ipv6)