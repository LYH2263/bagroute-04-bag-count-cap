from app.services.pack_engine import REASON_BAG_CAP, StopItem, pack_route


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


def test_bag_cap_truncates_tail_and_keeps_packed_bags():
    # 重量 4kg 上限：前 4 站恰好装满 2 袋，第 5 站需要再开第 3 袋 → 截断
    stops = [
        StopItem(1, 1, 2.0, 1.0, "甲"),
        StopItem(2, 2, 2.0, 1.0, "乙"),
        StopItem(3, 3, 2.5, 1.0, "丙"),
        StopItem(4, 4, 1.5, 1.0, "丁"),
        StopItem(5, 5, 1.0, 1.0, "戊"),
        StopItem(6, 6, 1.0, 1.0, "己"),
    ]
    result = pack_route(stops, max_weight=4.0, max_volume=10.0, max_bags=2)

    # 袋数不超过上限，且已装入的袋保持不变
    assert len(result.bags) == 2
    assert [i.stop_id for i in result.bags[0].items] == [1, 2]
    assert [i.stop_id for i in result.bags[1].items] == [3, 4]
    packed_weight = sum(b.weight_kg for b in result.bags)
    assert packed_weight == 8.0

    # 触发再开第 3 袋的当前站及其后序站点全部拒收
    rejected = result.rejects
    assert [item.stop_id for item, _ in rejected] == [5, 6]
    assert all(REASON_BAG_CAP in reason for _, reason in rejected)
    # 袋数用尽不能被写成超重/超体积
    assert all("超重" not in reason and "超体积" not in reason for _, reason in rejected)


def test_bag_cap_reason_distinguishes_from_single_stop_overflow():
    # seq=2 自身超重（现网原因），seq=3 因袋数用尽拒收，两者必须可区分
    stops = [
        StopItem(1, 1, 3.0, 1.0, "甲"),
        StopItem(2, 2, 9.0, 1.0, "超重件"),
        StopItem(3, 3, 3.0, 1.0, "乙"),
        StopItem(4, 4, 1.0, 1.0, "丙"),
    ]
    result = pack_route(stops, max_weight=4.0, max_volume=10.0, max_bags=1)

    reasons = {item.stop_id: reason for item, reason in result.rejects}
    assert "超重" in reasons[2]
    assert REASON_BAG_CAP not in reasons[2]
    assert REASON_BAG_CAP in reasons[3]
    assert REASON_BAG_CAP in reasons[4]

    # 已装入的唯一一袋保持
    assert len(result.bags) == 1
    assert [i.stop_id for i in result.bags[0].items] == [1]


def test_zero_max_bags_means_unlimited():
    stops = [StopItem(i, i, 3.0, 1.0) for i in range(1, 6)]
    result = pack_route(stops, max_weight=4.0, max_volume=10.0, max_bags=0)
    assert len(result.bags) == 5
    assert not result.rejects
