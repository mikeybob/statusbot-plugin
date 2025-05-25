from setuptools import setup, find_packages

setup(
    name="statusbot",
    version="0.1.0",
    description="Set and maintain your Matrix presence status message",
    packages=find_packages(),
    entry_points={
        "maubot.plugins": [
            "statusbot = statusbot.plugin:StatusPlugin"
        ]
    },
    install_requires=[
        "maubot>=0.5.1",           # Maubot core plugin host (matches your 0.5.1 install)
        "mautrix>=0.20.0"
    ],
)

