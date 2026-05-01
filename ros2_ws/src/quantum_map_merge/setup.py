from setuptools import setup

package_name = 'quantum_map_merge'

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
    description='Quantum Map Merge - NP-Hard Map Merging via Google Quantum AI',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'quantum_node = quantum_map_merge.quantum_node:main',
        ],
    },
)
