import os
import sys
import tempfile
from urllib.error import URLError

import hypothesis
from colorama import init, Fore, Back, Style

from .client import Client
from .strategies import StrategyFactory


def api_conformance_test(
    schema_path,
    num_tests_per_op=20,
    cont_on_err=True,
    get_report=True,
    username=None,
    password=None,
    token=None,
    security_name=None,
    extra_headers=None,
):

    init()
    log_filename = "log.txt"

    print(Fore.BLUE + "Connecting to {}".format(schema_path) + Style.RESET_ALL)

    try:
        client = Client(
            schema_path,
            username=username,
            password=password,
            token=token,
            security_name=security_name,
            extra_headers=extra_headers,
        )
    except URLError as exc:
        print(
            Fore.WHITE
            + Back.RED
            + "Unable to connect Swagger client: "
            + str(exc)
            + Style.RESET_ALL
        )
        sys.exit(1)

    print(
        Fore.BLUE + "Swagger client... " + Fore.GREEN + " ok" + Style.RESET_ALL
    )

    method = " basic"
    if username is not None and password is not None:
        method = " authenticated"

    print(
        Fore.BLUE + "Authentication method : " + Fore.GREEN + method + Style.RESET_ALL
    )

    fd, watchdog_filename = tempfile.mkstemp()
    os.close(fd)
    os.remove(watchdog_filename)
    if os.path.isfile(log_filename):
        os.remove(log_filename)

    for operation in client.api.operations():
        try:
            operation_conformance_test(
                client,
                operation,
                num_tests_per_op,
                cont_on_err,
                watchdog_filename,
                get_report,
                log_filename,
            )
        except ValueError as exc:
            print(
                Fore.WHITE
                + Back.RED
                + 'Unable to run test: "{}"'.format(str(exc))
                + Style.RESET_ALL
            )
            sys.exit(1)

    if get_report:
        with open(log_filename, "r") as myfile:
            dic = {}
            nb_error = 0
            first = True
            for line in myfile:
                line = line.split(" ")
                line[-1] = line[-1].split("\n")[0]
                if line[0] == "test":
                    if not first:
                        print_report(dic, nb_error)
                        dic = {}
                        nb_error = 0

                    print(
                        Fore.BLUE
                        + "\n["
                        + Fore.YELLOW
                        + line[1]
                        + Fore.BLUE
                        + "] "
                        + Fore.CYAN
                        + line[2]
                        + Style.RESET_ALL
                    )
                    first = False

                elif line[0] == "ok":
                    if line[1] not in dic:
                        dic[line[1]] = 1
                    else:
                        dic[line[1]] += 1

                elif line[0] == "fail":
                    dic[nb_error] = line[1] + "\t" + line[2]

            print_report(dic, nb_error)


def print_report(dic, nb_error):
    for k, v in dic.items():
        if isinstance(k, str):
            print(
                "[ SUCCESS "
                + Fore.MAGENTA
                + "Code: {0} \ttests : {1}".format(k, v)
                + Style.RESET_ALL
                + " ] "
            )
    for i in range(0, nb_error):
        tmp = dic[i].split("\t")
        print(
            "[ FAIL "
            + Fore.RED
            + "\n\tResponse code {} not in documented codes: {}".format(tmp[0], tmp[1])
            + Style.RESET_ALL
            + " ] "
        )


def operation_conformance_test(
    client, operation, num_tests, cont_on_err, watchdog_filename, get_report, log_filename
):
    success = "\t[" + Fore.GREEN + " ok " + Style.RESET_ALL + "] "
    failed = "\t[" + Fore.RED + " fail " + Style.RESET_ALL + "] "
    skip = "\t[" + Fore.MAGENTA + " skip " + Style.RESET_ALL + "] "

    print(
        Fore.BLUE
        + "\n["
        + Fore.YELLOW
        + operation.method
        + Fore.BLUE
        + "] "
        + Fore.CYAN
        + operation.path
        + Style.RESET_ALL
    )

    if get_report:
        with open(log_filename, "a+") as myfile:
            myfile.write("test [" + str(operation.method) + "] " + operation.path + "\n")

    for name, op in operation._parameters.items():
        if not op.type:
            url = "https://github.com/adimian/swagger-check/labels/types%20support"
            print(
                skip
                + "unsupported input type for '{}'. See {}".format(name, url)
            )
            return

    strategy = operation.parameters_strategy(StrategyFactory())

    @hypothesis.settings(
        max_examples=num_tests,
        suppress_health_check=[hypothesis.HealthCheck.too_slow],
        deadline=None,
        verbosity=hypothesis.Verbosity.quiet,
    )
    @hypothesis.given(strategy)
    def single_operation_test(
        client, operation, cont_on_err, get_report, log_filename, watchdog_filename, params
    ):
        root = "Testing with params: {}".format(params) + Style.RESET_ALL
        result = client.request(operation, params)

        status_code = (
            "[ "
            + Fore.MAGENTA
            + "{}".format(result.status)
            + Style.RESET_ALL
            + " ] "
        )

        if result.status in operation.response_codes:
            print(success + status_code + root)
            if get_report:
                with open(log_filename, "a+") as myfile:
                    myfile.write("ok " + str(result.status) + "\n")
        else:
            outcome = (
                Fore.RED
                + "\n\tResponse code {} not in documented codes: {}".format(
                    result.status, operation.response_codes
                )
                + Style.RESET_ALL
            )
            print(failed + status_code + root + outcome)
            if get_report:
                with open(log_filename, "a+") as myfile:
                    myfile.write("failed " + str(result.status) + " " + str(operation.response_codes) + "\n")

            if not cont_on_err:
                # we use a file as a signal between inside and outside of
                # hypothesis since otherwise we'd see hypothesis extended help
                # but this is not what we're looking for here
                with open(watchdog_filename, "w"):
                    pass

    single_operation_test(client, operation, cont_on_err, get_report, log_filename, watchdog_filename)

    if os.path.isfile(watchdog_filename):
        print(Fore.RED + "Stopping after first failure" + Style.RESET_ALL)
        sys.exit(1)
