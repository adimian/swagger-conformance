import sys
import argparse

from swaggercheck import api_conformance_test

from colorama import init, Fore, Style, Back

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

    try:
        api_conformance_test(
            parsed_args.schema_path,
            num_tests_per_op=parsed_args.num_tests_per_op,
            cont_on_err=parsed_args.cont_on_err,
            username=parsed_args.username,
            password=parsed_args.password,
            token=parsed_args.token,
            security_name=parsed_args.security_name,
        )
    except KeyboardInterrupt:
        print(
            Fore.WHITE
            + Back.RED
            + "Interrupted by user command"
            + Style.RESET_ALL
        )
        sys.exit(1)
