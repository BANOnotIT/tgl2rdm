from datetime import datetime, timedelta

import petl

from tgl2rdm.transform import group_entries_by_day


def test_same_day():
    data = [
        ['dur', 'description', 'start'],
        [timedelta(), 'test', datetime(2000, 1, 1, 15, 10)],
        [timedelta(), 'test', datetime(2000, 1, 1, 15, 0)],
    ]

    result = group_entries_by_day(data)
    assert petl.nrows(result) == 1


def test_different_days():
    data = [
        ['dur', 'description', 'start'],
        [timedelta(), 'test', datetime(2000, 1, 1, 15)],
        [timedelta(), 'test', datetime(2000, 1, 2, 15)],
    ]

    result = group_entries_by_day(data)
    assert petl.nrows(result) == 2


def test_different_description():
    data = [
        ['dur', 'description', 'start'],
        [timedelta(), 'test 2', datetime(2000, 1, 1, 15, 10)],
        [timedelta(), 'test 2', datetime(2000, 1, 1, 15, 0)],
        [timedelta(), 'test 1', datetime(2000, 1, 1, 15, 15)],
        [timedelta(), 'test 1', datetime(2000, 1, 1, 16, 15)],
    ]

    result = group_entries_by_day(data)
    assert petl.nrows(result) == 2


def test_minimal_start():
    data = [
        ['dur', 'description', 'start'],
        [timedelta(), 'test 1', datetime(2000, 1, 1, 0, 15)],
        [timedelta(), 'test 1', datetime(2000, 1, 1, 20, 15)],
    ]

    result = group_entries_by_day(data)
    assert set(petl.values(result, 'start')) == {datetime(2000, 1, 1, 0, 15)}


def test_sum_duration():
    data = [
        ['dur', 'description', 'start'],
        [timedelta(minutes=1), 'test 1', datetime(2000, 1, 1, 15, 15)],
        [timedelta(minutes=1), 'test 1', datetime(2000, 1, 1, 20, 15)],
        [timedelta(hours=2), 'test 1', datetime(2000, 1, 20, 15, 15)],
        [timedelta(hours=1), 'test 1', datetime(2000, 1, 20, 20, 15)],
    ]

    result = group_entries_by_day(data)
    assert set(petl.values(result, 'dur')) == {timedelta(minutes=2), timedelta(hours=3)}


def test_no_header_mutation():
    data = [
        ['dur', 'description', 'start', 'alpha'],
        [.4, 'test 1', datetime(2000, 1, 1, 15, 15), 0],
        [.7, 'test 1', datetime(2000, 1, 1, 20, 15), 0],
        [1.6, 'test 1', datetime(2000, 1, 20, 15, 15), 0],
        [8.4, 'test 1', datetime(2000, 1, 20, 20, 15), 0],
    ]

    result = group_entries_by_day(data)
    assert set(petl.header(data)) == set(petl.header(result))
