import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graphene-django-crud",  # Replace with your own username
    version="2.0.0",
    author="djipidi",
    author_email="djipidi.dev@gmail.com",
    description="Turns the django ORM into a graphql API",
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
        "Django>=3.2",
        "graphene>=3.0,<4",
        "graphene-django>=3.0,<4",
    ],
    python_requires=">=3.6",
)
