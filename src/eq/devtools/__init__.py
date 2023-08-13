try:
    from ._version import __version__
except ModuleNotFoundError:
    try:
        # https://github.com/maresb/hatch-vcs-footgun-example/
        from setuptools_scm import get_version
        __version__ = get_version(root='../../..', relative_to=__file__)
    except (ImportError, LookupError):
        __version__ = "0.0.0.dev0+unknown"
