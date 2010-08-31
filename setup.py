from setuptools import setup, find_packages
 
version = '0.5.99'
 
setup(
    name = "EForge",
    version = version,
    description = "Project management that rocks",
    long_description = "Project management system, powered by Django",
    keywords = 'web django cms forge',
    license = 'ISC',
    author = 'Element43 & Contributors',
    author_email = 'support@e43.eu',
    url = 'http://eforge.e43.eu/p/eforge',
    zip_safe = False,
    include_package_data = True,
    packages = find_packages(),
    package_data = {
        '' : ['LICENSE', 'README', 'CONTRIBUTORS', '*.png', '*.css', '*.html', '*.js'],
    },
    install_requires = [
        "django>=1.2.1",
        "PIL>=1.1.7",
        "dulwich>=0.6.1",
        "TCWiki>=0.1.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: ISC License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: Django",
        "Topic :: Internet :: WWW/HTTP :: Forge",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
