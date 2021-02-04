import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graphene-django-crud", # Replace with your own username
    version="1.0.3",
    author="djipidi",
    author_email="djipidi.dev@gmail.com",
    description="deploy orm django to a graphql API easily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djipidi/graphene_django_crud",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'graphene>=2.1.8,<3',
        'graphene-django>=2.13.0',
        'graphene-subscriptions>=1.0.2'
    ],
    python_requires='>=3.6',
)
