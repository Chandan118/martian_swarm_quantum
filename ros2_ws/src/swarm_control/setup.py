from setuptools import setup

package_name = 'swarm_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/mars_swarm.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Martian Swarm Team',
    maintainer_email='team@martianswarm.space',
    description='Swarm Control - Main rover spawner and coordinator',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'swarm_node = swarm_control.swarm_node:main',
        ],
    },
)
