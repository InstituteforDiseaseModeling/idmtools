from distutils.core import setup

setup(
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Mostly GNU Make compatible make",
    include_package_data=True,
    entry_points={"console_scripts": ["pymake=pymake.make:main"]},
    name='pymake',
    python_requires='>=3.6.*, !=3.7.0, !=3.7.1, !=3.7.2',
    test_suite='tests',
    version="1.0.0",
    zip_safe=False
)