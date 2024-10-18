import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_backtester.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as error:
        raise ImportError(
            "Django is either not installed or not available on your PYTHONPATH. "
            "Ensure it's installed and a virtual environment is activated."
        ) from error

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()