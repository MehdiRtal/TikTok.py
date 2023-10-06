from setuptools import setup


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="tiktok_py",
    version="0.1",
    packages=["tiktok_py"],
    package_dir={"tiktok_py": "."},
    install_requires=requirements,
)
