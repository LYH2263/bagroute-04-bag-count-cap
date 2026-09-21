from app.services.pack_engine import StopItem, pack_route


def test_packs_in_route_order_splitting_bags():
    stops = [
        StopItem(1, 1, 2.0, 3.0),
        StopItem(2, 2, 2.5, 3.0),
        StopItem(3, 3, 1.0, 1.0),
    ]
    result = pack_route(stops, max_weight=4.0, max_volume=10.0)
    assert len(result.bags) == 2
    assert [i.stop_id for i in result.bags[0].items] == [1]
    assert [i.stop_id for i in result.bags[1].items] == [2, 3]
    assert not result.rejects


def test_reject_oversized_stop():
    stops = [StopItem(1, 1, 9.0, 1.0, "大件"), StopItem(2, 2, 1.0, 1.0)]
    result = pack_route(stops, max_weight=5.0, max_volume=5.0)
    assert len(result.rejects) == 1
    assert result.rejects[0][0].stop_id == 1
    assert len(result.bags) == 1
    assert result.bags[0].items[0].stop_id == 2


def test_volume_cap_triggers_new_bag():
    stops = [StopItem(1, 1, 1.0, 4.0), StopItem(2, 2, 1.0, 4.0)]
    result = pack_route(stops, max_weight=10.0, max_volume=5.0)
    assert len(result.bags) == 2


def _bag_stop_ids(result):
    return [[i.stop_id for i in b.items] for b in result.bags]


def test_bag_limit_truncates_keeps_packed_bags_and_rejects_rest():
    stops = [
        StopItem(1, 1, 2.0, 3.0),
        StopItem(2, 2, 2.5, 3.0),
        StopItem(3, 3, 1.0, 1.0),
        StopItem(4, 4, 1.0, 1.0),
    ]
    unlimited = pack_route(stops, max_weight=4.0, max_volume=10.0)
    assert _bag_stop_ids(unlimited) == [[1], [2, 3], [4]]

    limited = pack_route(stops, max_weight=4.0, max_volume=10.0, max_bags=2)
    # already packed bags are exactly the unlimited run's first two
    assert _bag_stop_ids(limited) == _bag_stop_ids(unlimited)[:2]
    # every stop after the truncation point is rejected
    assert [r[0].stop_id for r in limited.rejects] == [4]
    reason = limited.rejects[0][1]
    assert "袋数用尽" in reason
    assert "超重" not in reason and "超体积" not in reason


def test_bag_limit_rejects_all_subsequent_stops_even_if_they_fit():
    stops = [
        StopItem(1, 1, 3.0, 1.0),
        StopItem(2, 2, 3.0, 1.0),  # opens bag 2
        StopItem(3, 3, 2.5, 1.0),  # would need bag 3 -> cap hit
        StopItem(4, 4, 0.5, 1.0),  # fits in bag 2, but truncation is terminal
    ]
    result = pack_route(stops, max_weight=5.0, max_volume=50.0, max_bags=2)
    assert _bag_stop_ids(result) == [[1], [2]]
    assert [r[0].stop_id for r in result.rejects] == [3, 4]
    assert all("袋数用尽" in r[1] for r in result.rejects)


def test_bag_limit_reason_distinct_from_single_stop_oversize():
    stops = [
        StopItem(1, 1, 9.0, 1.0, "大件"),  # itself over weight -> 超重
        StopItem(2, 2, 3.0, 1.0),
        StopItem(3, 3, 3.0, 1.0),          # opens bag 2
        StopItem(4, 4, 2.5, 1.0),          # would need bag 3 -> 袋数用尽
    ]
    result = pack_route(stops, max_weight=5.0, max_volume=50.0, max_bags=2)
    assert _bag_stop_ids(result) == [[2], [3]]
    reasons = {r[0].stop_id: r[1] for r in result.rejects}
    assert set(reasons) == {1, 4}
    assert "超重" in reasons[1] and "袋数用尽" not in reasons[1]
    assert "袋数用尽" in reasons[4] and "超重" not in reasons[4]


def test_bag_limit_not_reached_packs_normally():
    stops = [
        StopItem(1, 1, 2.0, 3.0),
        StopItem(2, 2, 2.5, 3.0),
        StopItem(3, 3, 1.0, 1.0),
    ]
    result = pack_route(stops, max_weight=4.0, max_volume=10.0, max_bags=2)
    assert _bag_stop_ids(result) == [[1], [2, 3]]
    assert not result.rejects
