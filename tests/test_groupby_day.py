from datetime import datetime

import petl

from tgl2rdm.transform import group_entries_by_day


def test_same_day():
    data = [
        ['dur', 'description', 'start'],
        [1, 'test', datetime(2000, 1, 1, 15, 10)],
        [1, 'test', datetime(2000, 1, 1, 15, 0)],
    ]

    result = group_entries_by_day(data)
    assert petl.nrows(result) == 1


def test_different_days():
    data = [
        ['dur', 'description', 'start'],
        [1, 'test', datetime(2000, 1, 1, 15)],
        [1, 'test', datetime(2000, 1, 2, 15)],
    ]

    result = group_entries_by_day(data)
    assert petl.nrows(result) == 2


def test_different_description():
    data = [
        ['dur', 'description', 'start'],
        [1, 'test 2', datetime(2000, 1, 1, 15, 10)],
        [1, 'test 2', datetime(2000, 1, 1, 15, 0)],
        [1, 'test 1', datetime(2000, 1, 1, 15, 15)],
        [1, 'test 1', datetime(2000, 1, 1, 16, 15)],
    ]

    result = group_entries_by_day(data)
    assert petl.nrows(result) == 2


def test_minimal_start():
    data = [
        ['dur', 'description', 'start'],
        [1, 'test 1', datetime(2000, 1, 1, 0, 15)],
        [1, 'test 1', datetime(2000, 1, 1, 20, 15)],
    ]

    result = group_entries_by_day(data)
    assert set(petl.values(result, 'start')) == {datetime(2000, 1, 1, 0, 15)}


def test_sum_duration():
    data = [
        ['dur', 'description', 'start'],
        [.4, 'test 1', datetime(2000, 1, 1, 15, 15)],
        [.7, 'test 1', datetime(2000, 1, 1, 20, 15)],
        [1.6, 'test 1', datetime(2000, 1, 20, 15, 15)],
        [8.4, 'test 1', datetime(2000, 1, 20, 20, 15)],
    ]

    result = group_entries_by_day(data)
    assert set(petl.values(result, 'dur')) == {.4 + .7, 1.6 + 8.4}
