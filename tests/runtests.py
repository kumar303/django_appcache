import os
import sys

import nose


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # project root
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    nose.main()
