from skbuild import setup

setup(name='watchoptical',
      version='0.1',
      description='WATCHMAN Optical Calibration Analysis Software',
      url='https://github.com/davehadley/watchoptical',
      author='David Hadley',
      author_email='dave.richard.hadley@gmail.com',
      license='MIT',
      packages=['watchoptical', 'watchoptical.watchopticalcpp'],
      zip_safe=False,
      )
