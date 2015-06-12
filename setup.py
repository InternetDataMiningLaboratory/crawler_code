# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = company_service.settings']},
)
