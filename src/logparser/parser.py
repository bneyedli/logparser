#!/usr/bin/env python3
"""
Module to process logs and serve results
"""

import argparse
import sys
from typing import Callable, Dict, Generator, List, Tuple

from apachelogs import COMBINED as ApacheCombined
from apachelogs import LogParser
from flask import Flask, redirect, render_template, request, url_for
from werkzeug import Response


class ParserRuntime:
    """
    Load runtime arguments for parser and provide facility to parse logs
    """

    def __init__(self) -> None:
        self.run_args = self.parse_args()
        self.requests: Dict[str, int] = {}
        self.get_referers: Dict[str, int] = {}
        self.unique_status: List[int] = []
        self.referers_sorted: Dict = {}
        self.top_referers: Dict = {}

    def parse_args(self) -> argparse.Namespace:
        """Parse args and return collection"""
        parser = argparse.ArgumentParser(
            description="Process and evaluate access logs."
        )
        parser.add_argument(
            "--logfile", default="/mnt/logs/access.log", help="Absolute path to logs"
        )
        parser.add_argument(
            "--ip", default="127.0.0.1", help="Host IP to listen on, default *all*"
        )
        parser.add_argument(
            "--port", default="3000", help="Host Port to listen on, default 3000"
        )
        return parser.parse_args()

    def parse_logs(self) -> bool:
        """Take logfile and parse results"""
        self.requests = {}
        self.get_referers = {}
        self.unique_status = []
        self.referers_sorted = {}
        self.top_referers = {}
        logfile = self.run_args.logfile
        parser = LogParser(ApacheCombined)
        print(f"Parsing logfile {logfile}")
        try:
            with open(logfile, encoding="utf8") as file:
                for entry in parser.parse_lines(file):
                    remote_host = entry.remote_host.strip()
                    final_status = entry.final_status
                    referer = entry.headers_in["Referer"].strip()
                    if remote_host in self.requests:
                        self.requests[remote_host] += 1
                    else:
                        self.requests[remote_host] = 1

                    if final_status not in self.unique_status:
                        self.unique_status.append(final_status)

                    if entry.request_line.startswith("GET"):
                        if referer in self.get_referers:
                            self.get_referers[referer] += 1
                        else:
                            self.get_referers[referer] = 1
            file.close()
        except FileNotFoundError:
            print(f"Log does not exist at: {logfile}")
            return False

        self.referers_sorted = dict(
            sorted(self.get_referers.items(), key=lambda item: item[1], reverse=True)
        )
        self.requests = dict(
            sorted(self.requests.items(), key=lambda item: item[1], reverse=True)
        )
        self.top_referers = {
            key: self.referers_sorted[key] for key in list(self.referers_sorted)[:5]
        }
        return True


class FlaskWrapper:
    """
    Wrapper for flask service
    """

    def __init__(self, app_name: str, parser: ParserRuntime) -> None:
        self.flask_app = Flask(
            app_name, static_url_path="/public", static_folder="./public"
        )
        self.flask_app.debug = True
        self.flask_app.config["JSON_SORT_KEYS"] = False
        self.run_args = parser.run_args
        self.logparser = parser
        self.requests: dict = {}

    def run_app(self) -> None:
        """
        Serve flask app on acquired host and port
        """
        self.flask_app.run(host=self.run_args.ip, port=self.run_args.port)

    def add_endpoint(
        self, name: str, path: str, handler: Callable, methods: list
    ) -> None:
        """
        Add route to flask app for given path, methods and handler
        """
        self.flask_app.add_url_rule(path, name, handler, methods=methods)

    def doc_root(self) -> Response:
        """Redirect / requests to stats"""
        return redirect(url_for("stats"))

    def stats_endpoint(self) -> Tuple[Dict, int]:
        """Stats endpoint check request args for output format process and return"""
        output_format = request.args.get("format")
        sort_hosts = request.args.get("sort_hosts")
        stats: Dict = {}
        stats["error_message"] = None

        if not self.logparser.parse_logs():
            return_value = 400
            stats["error_message"] = "Failed to parse logs"

        if sort_hosts == "true":
            self.requests = dict(
                sorted(self.logparser.requests.items(), key=lambda item: item[0])
            )

        if output_format is None:
            output_format = "json"

        if output_format == "json":
            return_value = 200
        else:
            stats["error_message"] = f"Unknown format: {output_format}"
            return_value = 400

        if return_value == 200:
            stats["request_count"] = len(self.logparser.requests)
            stats["top_referers"] = self.logparser.top_referers
            stats["unique_status"] = self.logparser.unique_status
            stats["host_count"] = self.logparser.requests

        return stats, return_value

    def yield_results(
        self, template_file: str, message: str, **kwargs: dict
    ) -> Generator:
        """Yield rendered html template"""
        print(type(render_template(template_file, **kwargs)))
        yield f"<pre>{message}</pre>"
        yield render_template(template_file, **kwargs)


if __name__ == "__main__":
    logparser = ParserRuntime()
    print(
        f"Listening on ip: {logparser.run_args.ip} "
        f"port: {logparser.run_args.port} "
        f"processing file {logparser.run_args.logfile}",
        file=sys.stderr,
    )
    flask_app = FlaskWrapper("logparser", logparser)
    flask_app.add_endpoint(
        path="/", name="doc_root", handler=flask_app.doc_root, methods=["GET"]
    )
    flask_app.add_endpoint(
        path="/stats", name="stats", handler=flask_app.stats_endpoint, methods=["GET"]
    )
    flask_app.run_app()
