# =======================================================================
# Contributor - @lumenpearson
# https://github.com/lumenpearson
# =======================================================================
"""
This module provides a synchronous availability checker for TCP, UDP, and GGC servers.
It verifies connectivity by performing network requests and reports availability status.

Features:
- Uses synchronous programming for network checks.
- Supports middleware for request validation.
- Includes three checker types:
  - TCPChecker: Checks TCP connection availability.
  - UDPChecker: Sends UDP packets to test connectivity.
  - GGCChecker: Performs HTTPS requests to verify server reachability.
- Middleware ensures request data integrity before checks.
- Configuration options allow setting timeout, default ports, and output mode.
- Results are printed in JSON format with type, address, and state fields.

Usage:
1. Provide lists of target servers for TCP, UDP, and GGC checks.
2. Run `AvailabilityChecker.run_checks()` to execute all tests.
3. Results can be printed immediately or collected.

This module is designed for simplicity and ease of use in synchronous environments.
"""

import json
import os
import platform
import socket
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from subprocess import SubprocessError
from subprocess import run as subprocess_run
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from icmplib import ping  # use synchronous ping
from pydantic import BaseModel, Field

cluster_decode_array = {
    "a": [
        "u",
        "z",
        "p",
        "k",
        "f",
        "a",
        "5",
        "0",
        "v",
        "q",
        "l",
        "g",
        "b",
        "6",
        "1",
        "w",
        "r",
        "m",
        "h",
        "c",
        "7",
        "2",
        "x",
        "s",
        "n",
        "i",
        "d",
        "8",
        "3",
        "y",
        "t",
        "o",
        "j",
        "e",
        "9",
        "4",
        "-",
    ],
    "b": [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "-",
    ],
}


def is_root() -> bool:
    """
    Check if the script is running with root privileges.
    :return: True if running as root, False otherwise
    :rtype: bool
    """
    if platform.system() == "Windows":
        return True  # on Windows, assume the user has sufficient privileges to ping commandlet
    else:
        return os.geteuid() == 0


def _extract_domain(url: str) -> str:
    """
    Extracts the domain from a given URL.

    :param url: The full URL (e.g., "https://www.example.com/path?query=1").
    :type url: str
    :return: The extracted domain name (e.g., "example.com").
    :rtype: str
    :raises InvalidURLException: If the URL is invalid or empty.
    """
    if not url or not isinstance(url, str):
        raise InvalidURLException("Provided URL is not valid.")

    parsed_url = urlparse(url)
    domain = parsed_url.hostname

    if not domain:
        raise InvalidURLException(
            "Unable to extract a valid domain from the provided URL."
        )

    return domain


def _convert_cluster_to_url(codename):
    decoded_codename = ""
    for letter in codename:
        if letter in cluster_decode_array["a"]:
            index = cluster_decode_array["a"].index(letter)
            decoded_codename += cluster_decode_array["b"][index]

    return f"https://rr1---sn-{decoded_codename}.googlevideo.com"


GGC_SERVER = _extract_domain(
    _convert_cluster_to_url(
        requests.get("https://redirector.gvt1.com/report_mapping?di=no").text.split()[2]
    )
)


class DefaultHosts:
    @staticmethod
    def tcp_host() -> List[str]:
        return [
            "google.com",
            "googlevideo.com",
            "gvt1.com",
            "ytimg.com",
            "youtube.com",
        ]

    @staticmethod
    def udp_host() -> List[str]:
        return [
            "127.0.0.1",
            "127.0.0.1:3000",
            "8.8.8.8",
            "0.0.0.0",
            "0.0.0.0:3000",
        ]

    @staticmethod
    def ggc_host() -> List[str]:
        return [GGC_SERVER]


class Options(BaseModel):
    """Stores configuration options for checkers, including port, timeout, and IO settings."""

    tcp_hosts: List[str] = Field(
        default_factory=DefaultHosts.tcp_host,
        description="list of hostnames or IP addresses for TCP connections.",
    )
    tcp_port: int = Field(
        443, ge=1, le=65535, description="sets the default port for TCP requests."
    )
    tcp_timeout: int = Field(
        300, gt=0, description="sets the timeout for TCP requests in milliseconds."
    )
    udp_hosts: List[str] = Field(
        default_factory=DefaultHosts.udp_host,
        description="list of hostnames or IP addresses for UDP connections.",
    )
    udp_port: int = Field(
        443, ge=1, le=65535, description="sets the default port for UDP requests."
    )
    udp_timeout: int = Field(
        300, gt=0, description="sets the timeout for UDP requests in milliseconds."
    )
    ggc_hosts: List[str] = Field(
        default_factory=DefaultHosts.ggc_host,
        description="list of hostnames or IP addresses for GGC servers.",
    )
    ggc_count: int = Field(
        1, ge=1, le=100, description="sets the number of ICMP requests."
    )
    ggc_timeout: int = Field(
        300,
        ge=1,
        le=10000,
        description="sets the timeout for ICMP requests in milliseconds.",
    )
    ggc_fping: bool = Field(
        False, description="[linux only]: use 'fping' instead of standard ping."
    )
    immediate_output: bool = Field(
        default=False, description="enables immediate output of check results."
    )
    version: int = Field(
        1, ge=1, description="displays the current version of the program."
    )
    tcph: List[str] = Field(
        default_factory=DefaultHosts.tcp_host,
        description="list of hostnames or IP addresses for TCP connections.",
    )
    tcpp: int = Field(
        443, ge=1, le=65535, description="sets the default port for TCP requests."
    )
    tcpt: int = Field(
        300, gt=0, description="sets the timeout for TCP requests in milliseconds."
    )
    udph: List[str] = Field(
        default_factory=DefaultHosts.udp_host,
        description="list of hostnames or IP addresses for UDP connections.",
    )
    udpp: int = Field(
        443, ge=1, le=65535, description="sets the default port for UDP requests."
    )
    udpt: int = Field(
        300, gt=0, description="sets the timeout for UDP requests in milliseconds."
    )
    ggch: List[str] = Field(
        default_factory=DefaultHosts.ggc_host,
        description="list of hostnames or IP addresses for GGC servers.",
    )
    ggcc: int = Field(1, ge=1, le=100, description="sets the number of ICMP requests.")
    ggct: int = Field(
        300,
        ge=1,
        le=10000,
        description="sets the timeout for ICMP requests in milliseconds.",
    )
    ggcf: bool = Field(
        False, description="[linux only]: use 'fping' instead of standard ping."
    )
    io: bool = Field(
        default=False, description="enables immediate output of check results."
    )
    v: int = Field(1, ge=1, description="displays the current version of the program.")

    class Config:
        str_min_length = 1
        str_strip_whitespace = True


def ping_host(host: str, options: Options) -> bool:
    """
    Ping a host asynchronously using fping or standard ping based on options.
    :param host: Hostname or IP address to ping
    :type host: str
    :param options: Options object containing ping options and other fields
    :type options: Options
    """
    fping = options.ggc_fping or options.ggcf
    count = options.ggc_count or options.ggcc
    timeout = options.ggc_timeout or options.ggct

    if fping:
        command = ["fping", "-c", str(count), "-t", str(timeout), host]
        try:
            result = subprocess_run(
                command, capture_output=True, text=True, check=False
            )
            if (
                result.returncode == 0
                and f"xmt/rcv/%loss" in result.stdout
                and not " 0%" in result.stdout.split("xmt/rcv/%loss")[1]
            ):
                return True

            return False
        except FileNotFoundError:
            print("Fping not found. Falling back to standard 'ping3' method.")
            ping_host(host, options.copy(update={"ggc_fping": False, "ggcf": False}))
            return False
        except SubprocessError as e:
            print(f"Error running fping: {e}")
            return False
    else:
        try:
            host = ping(host, count=count, timeout=timeout)
            if host.is_alive:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False


class InvalidURLException(Exception):
    """
    Exception raised for invalid URLs.
    """

    def __str__(self):
        return f"Invalid URL provided. {super().__str__()}"


class RequestData(BaseModel):
    """Represents request data with target address and optional port."""

    addr: str = Field(..., description="Target address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Target port")


class Middleware(ABC):
    """Abstract base class for request middleware processing."""

    @abstractmethod
    def process_request(self, data: RequestData):
        pass


class TypeCheckMiddleware(Middleware):
    """Middleware to validate request data using Pydantic."""

    def process_request(self, data: RequestData):
        RequestData.model_validate(data)


class Checker(ABC):
    """
    Abstract base class for checkers with middleware support.
    """

    def __init__(self):
        """
        Initializes the checker with a list of middlewares.
        """
        self.middlewares = [TypeCheckMiddleware()]

    def apply_middlewares(self, data: RequestData):
        """
        Applies all middlewares to the given request data.

        :param data: The request data to process.
        :type data: RequestData
        """
        for middleware in self.middlewares:
            try:
                middleware.process_request(data)
            except Exception as e:
                print(f"Middleware error: {e}")

    @abstractmethod
    def check(self, data: RequestData) -> Dict[str, Union[str, bool]]:
        """
        Abstract method for performing a check on request data.

        :param data: The request data to check.
        :type data: RequestData
        :return: A dictionary with check results.
        """
        pass


class TCPChecker(Checker):
    """
    TCP connectivity checker that verifies if a given address and port are reachable.
    """

    def __init__(self, options: Options):
        """
        Initializes the TCP checker with options.

        :param options: Configuration options for the checker.
        """
        super().__init__()
        self.options = options
        self.timeout = (self.options.tcp_timeout or self.options.tcpt) / 1000

    def check(self, data: RequestData) -> Dict[str, Union[str, bool]]:
        """
        Checks TCP connectivity for the given request data.

        :param data: The request data containing address and port.
        :return: A dictionary with check results, including address and connection state.
        """
        self.apply_middlewares(data)
        port = data.port or self.options.tcpp
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((data.addr, port))
            return {"type": "TCP", "addr": data.addr, "state": True}
        except (socket.gaierror, socket.timeout, OSError):
            return {"type": "TCP", "addr": data.addr, "state": False}


class UDPChecker(Checker):
    """
    UDP connectivity checker that verifies if a given address and port are reachable.
    """

    def __init__(self, options: Options):
        """
        Initializes the UDP checker with options.

        :param options: Configuration options for the checker.
        """
        super().__init__()
        self.options = options
        self.timeout = (self.options.udp_timeout or self.options.udpt) / 1000

    def check(self, data: RequestData) -> Dict[str, Union[str, bool]]:
        """
        Checks UDP connectivity for the given request data.

        :param data: The request data containing address and port.
        :return: A dictionary with check results, including address and connection state.
        """
        self.apply_middlewares(data)
        port = data.port or self.options.udpp
        try:
            return self._udp_check_sync(data.addr, port)
        except (socket.timeout, socket.gaierror, OSError):
            return {"type": "UDP", "addr": data.addr, "state": False}

    def _udp_check_sync(self, addr: str, port: int) -> Dict[str, Union[str, bool]]:
        """
        Performs a synchronous UDP connectivity check by sending and receiving a packet.

        :param addr: The target address.
        :param port: The target port.
        :return: A dictionary with check results.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(self.timeout)
            s.sendto(b"ping", (addr, port))
            s.recvfrom(1024)
            return {"type": "UDP", "addr": addr, "state": True}


class GGCChecker(Checker):
    """
    GGC connectivity checker that verifies if a given address is reachable via HTTPS.
    """

    def __init__(self, options: Options):
        """
        Initializes the GGC checker with an HTTP session and options.

        :param options: Configuration options for the checker.
        """
        super().__init__()
        self.options = options

    def check(self, data: RequestData) -> Dict[str, Union[str, bool]]:
        """
        Checks HTTPS connectivity for the given request data.

        :param data: The request data containing the target address.
        :return: A dictionary with check results, including address and connection state.
        """
        self.apply_middlewares(data)
        try:
            is_ping = ping_host(data.addr, self.options)
            return {
                "type": "GGC",
                "addr": data.addr,
                "state": is_ping,
            }
        except Exception as _:
            return {"type": "GGC", "addr": data.addr, "state": False}


class ServerAvailabilityChecker:
    """
    Runs availability checks for TCP, UDP, and GGC targets.
    """

    def __init__(
        self,
        tcp: List[str] | None = None,
        udp: List[str] | None = None,
        ggc: List[str] | None = None,
        options: Options = Options(),
    ):
        """
        Initializes the availability checker with target lists and options.

        :param tcp: List of TCP target addresses.
        :param udp: List of UDP target addresses.
        :param ggc: List of GGC target addresses.
        :param options: Configuration options for the checker.
        """
        self.targets = {}

        # add only non-None lists to the targets dictionary
        if tcp is not None:
            self.targets["TCP"] = tcp
        if udp is not None:
            self.targets["UDP"] = udp
        if ggc is not None:
            self.targets["GGC"] = ggc

        # raise an exception if no targets are provided
        if not self.targets:
            raise ValueError(
                "At least one target list (TCP, UDP, GGC) must be provided."
            )

        self.options = options
        self.io = self.options.immediate_output or self.options.io

    def run_checks(self):
        """
        Runs availability checks for all targets using their respective checkers.

        Opens an HTTP session for GGC checks and executes checks concurrently.
        Results are printed based on the options provided.
        """
        checkers = {}

        # initialize checkers only for non-None target types
        if "TCP" in self.targets:
            checkers["TCP"] = TCPChecker(self.options)
            timeout = self.options.tcp_timeout or self.options.tct
        if "UDP" in self.targets:
            checkers["UDP"] = UDPChecker(self.options)
            timeout = self.options.udp_timeout or self.options.udt
        if "GGC" in self.targets:
            checkers["GGC"] = GGCChecker(self.options)
            timeout = self.options.ggc_timeout or self.options.ggt

        results_dict = {target: [] for target in self.targets.keys()}
        for target, sites in self.targets.items():
            if target not in checkers:
                continue  # skip if no checker for this target type

            for s in sites:
                result = checkers[target].check(RequestData(addr=s))
                if self.io:
                    yield result if result is not None else None
                else:
                    if result is not None:
                        results_dict[target].append(result)
        if not self.io:
            yield results_dict


def parse_args():
    options = Options()
    parser = ArgumentParser(
        description="Check availability of TCP, UDP, and GGC servers."
    )
    parser.add_argument(
        "--tcp_hosts",
        nargs="*",
        default=options.tcp_hosts,
        help="list of hostnames or IP addresses for TCP connections.",
    )
    parser.add_argument(
        "--tcp_port",
        type=int,
        default=options.tcp_port,
        help="sets the default port for TCP requests.",
    )
    parser.add_argument(
        "--tcp_timeout",
        type=float,
        default=options.tcp_timeout,
        help="sets the timeout for TCP requests in milliseconds.",
    )

    parser.add_argument(
        "--udp_hosts",
        nargs="*",
        default=options.udp_hosts,
        help="list of hostnames or IP addresses for UDP connections.",
    )
    parser.add_argument(
        "--udp_port",
        type=int,
        default=options.udp_port,
        help="sets the default port for UDP requests.",
    )
    parser.add_argument(
        "--udp_timeout",
        type=float,
        default=options.udp_timeout,
        help="sets the timeout for UDP requests in milliseconds.",
    )

    parser.add_argument(
        "--ggc_hosts",
        nargs="*",
        default=options.ggc_hosts,
        help="list of hostnames or IP addresses for GGC servers.",
    )
    parser.add_argument(
        "--ggc_count",
        type=int,
        default=options.ggc_count,
        help="sets the number of ICMP requests.",
    )
    parser.add_argument(
        "--ggc_timeout",
        type=int,
        default=options.ggc_timeout,
        help="sets the timeout for ICMP requests in milliseconds.",
    )
    parser.add_argument(
        "--ggc_fping",
        action="store_true",
        default=options.ggc_fping,
        help="[linux only]: use 'fping' instead of standard ping.",
    )

    parser.add_argument(
        "--immediate_output",
        action="store_true",
        default=options.immediate_output,
        help="enables immediate output of check results.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0",
        help="displays the current version of the program.",
    )

    parser.add_argument(
        "-tcph",
        nargs="*",
        default=options.tcph,
        help="list of hostnames or IP addresses for TCP connections.",
    )
    parser.add_argument(
        "-tcpp",
        type=int,
        default=options.tcpp,
        help="sets the default port for TCP requests.",
    )
    parser.add_argument(
        "-tcpt",
        type=float,
        default=options.tcpt,
        help="sets the timeout for TCP requests in milliseconds.",
    )

    parser.add_argument(
        "-udph",
        nargs="*",
        default=options.udph,
        help="list of hostnames or IP addresses for UDP connections.",
    )
    parser.add_argument(
        "-udpp",
        type=int,
        default=options.udpp,
        help="sets the default port for UDP requests.",
    )
    parser.add_argument(
        "-udpt",
        type=float,
        default=options.udpt,
        help="sets the timeout for UDP requests in milliseconds.",
    )

    parser.add_argument(
        "-ggch",
        nargs="*",
        default=options.ggch,
        help="list of hostnames or IP addresses for GGC servers.",
    )
    parser.add_argument(
        "-ggcc",
        type=int,
        default=options.ggcc,
        help="sets the number of ICMP requests.",
    )
    parser.add_argument(
        "-ggct",
        type=int,
        default=options.ggct,
        help="sets the timeout for ICMP requests in milliseconds.",
    )
    parser.add_argument(
        "-ggcf",
        action="store_true",
        default=options.ggcf,
        help="[linux only]: use 'fping' instead of standard ping.",
    )

    parser.add_argument(
        "-io",
        action="store_true",
        default=options.immediate_output,
        help="enables immediate output of check results.",
    )
    parser.add_argument(
        "-v",
        action="version",
        version="%(prog)s 1.0",
        help="displays the current version of the program.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    options = Options(**vars(args))
    checker = ServerAvailabilityChecker(
        args.tcp_hosts or args.tcph,
        args.udp_hosts or args.udph,
        args.ggc_hosts or args.ggch,
        options=options,
    )

    for result in checker.run_checks():
        print(json.dumps(result, indent=2))
