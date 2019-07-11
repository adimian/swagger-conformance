import argparse
import sys
from os import environ

from colorama import init, Fore, Style, Back

from swaggercheck import api_conformance_test

init()


def main():
    parser = argparse.ArgumentParser(
        description="Basic Swagger-defined API conformance test."
    )
    parser.add_argument("schema_path", help="URL or path to Swagger schema")
    parser.add_argument(
        "-n",
        dest="num_tests_per_op",
        metavar="N",
        type=int,
        default=20,
        help="number of tests to run per API operation",
    )

    parser.add_argument(
        "-c",
        "--continue-on-error",
        dest="cont_on_err",
        action="store_true",
        help="continue on error",
    )

    parser.add_argument(
        "-u", "--username", help="username (implies 'basic' auth)"
    )
    parser.add_argument(
        "-p", "--password", help="password (implies 'basic' auth)"
    )
    parser.add_argument(
        "-k", "--token", help="api key token (implies 'apiKey' auth)"
    )

    parser.add_argument(
        "--security-name",
        help="force a security name if not 'basic' or 'apiKey'",
    )

    parsed_args = parser.parse_args()

    test_kwargs = {
        "num_tests_per_op": (
            parsed_args.num_tests_per_op or environ.get("SC_TESTS")
        ),
        "cont_on_err": (
            parsed_args.cont_on_err or environ.get("SC_CONTINUE_ON_ERROR")
        ),
        "username": parsed_args.username or environ.get("SC_BASIC_USERNAME"),
        "password": parsed_args.password or environ.get("SC_BASIC_PASSWORD"),
        "token": parsed_args.token or environ.get("SC_API_TOKEN"),
        "security_name": (
            parsed_args.security_name or environ.get("SC_SECURITY_NAME")
        ),
    }

    try:
        api_conformance_test(parsed_args.schema_path, **test_kwargs)
    except KeyboardInterrupt:
        print(
            Fore.WHITE
            + Back.RED
            + "Interrupted by user command"
            + Style.RESET_ALL
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
