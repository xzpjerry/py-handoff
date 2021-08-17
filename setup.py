from setuptools import find_packages, setup

import versioneer

reqrs = []
try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements
install_reqs = parse_requirements("requirements.txt", session=PipSession())
try:
    reqrs = [str(ir.req) for ir in install_reqs]
except Exception:
    reqrs = [str(ir.requirement) for ir in install_reqs]

with open("README.md") as f:
    readme = f.read()

with open("HISTORY.md") as f:
    history = f.read()


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Like Handoff, but in Python",
    long_description=readme + "\n\n" + history,
    author="xzpjerry",
    author_email="xzpjerry@gmail.com",
    keywords="py_handoff",
    url="https://github.com/xzpjerry/py-handoff",
    include_package_data=True,
    packages=find_packages(include=["py_handoff", "py_handoff.*"]),
    install_requires=reqrs,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    zip_safe=False,
    entry_points={"console_scripts": ["py-handoff=py_handoff.main:entrypoint"]},
    long_description_content_type="text/markdown",
)
