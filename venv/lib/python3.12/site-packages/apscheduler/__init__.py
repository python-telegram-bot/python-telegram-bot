from pkg_resources import get_distribution, DistributionNotFound

try:
    release = get_distribution('APScheduler').version.split('-')[0]
except DistributionNotFound:
    release = '3.5.0'

version_info = tuple(int(x) if x.isdigit() else x for x in release.split('.'))
version = __version__ = '.'.join(str(x) for x in version_info[:3])
del get_distribution, DistributionNotFound
