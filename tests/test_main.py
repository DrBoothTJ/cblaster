#!/usr/bin/env python3

"""
Test suite for main.py
"""

import sys
import pytest

from cblaster import local, context, main, classes, remote


class MockOrganism(classes.Organism):
    def count_hit_clusters(self):
        return 1

    def summary(self, headers=True, human=True):
        return "mocked"


def test_summarise(capsys, tmp_path):
    def return_text(x):
        return "test"

    organisms = [
        MockOrganism(name="test", strain="123"),
        MockOrganism(name="test2", strain="456"),
    ]

    # Test output file handle
    file = tmp_path / "test.txt"

    with file.open("w") as handle:
        main.summarise(organisms, output=handle)

    assert file.read_text() == "mocked\n\n\nmocked\n"

    # Test stdout
    main.summarise(organisms, output=sys.stdout)
    captured = capsys.readouterr()
    assert captured.out == "mocked\n\n\nmocked\n"


def test_cblaster(mocker, tmp_path):
    mocker.patch("cblaster.local.search")
    mocker.patch("cblaster.remote.search")
    mocker.patch("cblaster.context.search")
    mocker.patch("cblaster.main.summarise")

    file = tmp_path / "test.txt"

    with file.open("w") as handle:
        main.cblaster(query_ids=["seq1"], mode="local", output=handle)

    main.cblaster(query_ids=["seq1"], mode="remote", output=sys.stdout)

    local.search.assert_called_once()
    remote.search.assert_called_once()

    context.search.call_count = 2
    main.summarise.call_count = 2


def test_get_arguments_remote_defaults():
    assert vars(main.get_arguments(["search", "-qf", "test"])) == {
        "subcommand": "search",
        "output": sys.stdout,
        "output_headers": True,
        "output_human": True,
        "binary": None,
        "binary_headers": False,
        "binary_human": False,
        "debug": False,
        "query_ids": None,
        "query_file": "test",
        "mode": "remote",
        "json": None,
        "database": "nr",
        "entrez_query": None,
        "rid": None,
        "gap": 20000,
        "conserve": 3,
        "max_evalue": 0.01,
        "min_identity": 30,
        "min_coverage": 50,
    }


def test_get_arguments_remote_invalid_db():
    with pytest.raises(ValueError):
        main.get_arguments(["search", "-qf", "test", "-m", "remote", "-db", "fake"])


def test_get_arguments_local_invalid_arg():
    with pytest.raises(ValueError):
        main.get_arguments(["search", "-qf", "test", "-m", "local", "-eq", "entrez"])
        main.get_arguments(["search", "-qf", "test", "-m", "local", "--rid", "rid"])
