"""
Allow running the package from the command line directly with:

``python -m swaggerconformance <url-or-path-to-schema> [-n num-tests-per-op]``

to run the basic conformance test of the API defined by the given schema.
"""
import argparse

from swaggercheck import api_conformance_test


def main():
    """Run a basic API conformance test with the supplied command line args."""
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

    parsed_args = parser.parse_args()
    api_conformance_test(
        parsed_args.schema_path,
        num_tests_per_op=parsed_args.num_tests_per_op,
        cont_on_err=parsed_args.cont_on_err,
    )
