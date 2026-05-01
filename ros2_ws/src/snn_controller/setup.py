from setuptools import setup

package_name = 'snn_controller'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Martian Swarm Team',
    maintainer_email='team@martianswarm.space',
    description='SNN Controller - Spiking Neural Network for Neuromorphic Obstacle Avoidance',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'snn_node = snn_controller.snn_node:main',
        ],
    },
)
