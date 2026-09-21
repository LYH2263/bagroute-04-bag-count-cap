"""Route-order bag packing with weight + volume caps; reject when exceed."""

from __future__ import annotations

from dataclasses import dataclass, field

# 拒收原因分档关键字：袋数用尽与超重/超体积必须可区分
REASON_BAG_CAP = "袋数用尽"


@dataclass(frozen=True)
class StopItem:
    stop_id: int
    seq: int
    weight_kg: float
    volume_l: float
    label: str = ""


@dataclass
class Bag:
    bag_index: int
    items: list[StopItem] = field(default_factory=list)
    weight_kg: float = 0.0
    volume_l: float = 0.0


@dataclass(frozen=True)
class PackResult:
    bags: list[Bag]
    rejects: list[tuple[StopItem, str]]


def can_fit(bag: Bag, item: StopItem, max_weight: float, max_volume: float) -> bool:
    return (
        bag.weight_kg + item.weight_kg <= max_weight + 1e-9
        and bag.volume_l + item.volume_l <= max_volume + 1e-9
    )


def bag_cap_reason(max_bags: int) -> str:
    return f"{REASON_BAG_CAP}：路线袋数上限 {max_bags} 袋，已全部装满"


def pack_route(
    stops: list[StopItem],
    max_weight: float,
    max_volume: float,
    max_bags: int = 0,
) -> PackResult:
    ordered = sorted(stops, key=lambda s: s.seq)
    bags: list[Bag] = []
    rejects: list[tuple[StopItem, str]] = []
    current: Bag | None = None
    # 一旦需要再开一袋却会超过上限，本路线后续站点全部按袋数用尽拒收
    bags_exhausted = False

    for item in ordered:
        if item.weight_kg > max_weight or item.volume_l > max_volume:
            reason = []
            if item.weight_kg > max_weight:
                reason.append(f"超重 {item.weight_kg}>{max_weight}")
            if item.volume_l > max_volume:
                reason.append(f"超体积 {item.volume_l}>{max_volume}")
            rejects.append((item, "；".join(reason)))
            continue

        if bags_exhausted:
            rejects.append((item, bag_cap_reason(max_bags)))
            continue

        needs_new_bag = current is None or not can_fit(current, item, max_weight, max_volume)
        if needs_new_bag and max_bags > 0 and len(bags) >= max_bags:
            bags_exhausted = True
            rejects.append((item, bag_cap_reason(max_bags)))
            continue

        if needs_new_bag:
            current = Bag(bag_index=len(bags) + 1)
            bags.append(current)

        current.items.append(item)
        current.weight_kg += item.weight_kg
        current.volume_l += item.volume_l

    return PackResult(bags=bags, rejects=rejects)
