"""Route-order bag packing with weight + volume caps and a per-route bag-count cap.

Stops are packed in seq order; a new bag is opened when the current one cannot
fit the next stop under the weight/volume caps. When opening another bag would
exceed ``max_bags``, the current stop and every subsequent unpacked stop are
rejected with a "bag count exhausted" reason — already packed bags stay as-is.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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


def bag_exhausted_reason(max_bags: int) -> str:
    return f"袋数用尽：路线最多 {max_bags} 袋"


def pack_route(
    stops: list[StopItem],
    max_weight: float,
    max_volume: float,
    max_bags: int | None = None,
) -> PackResult:
    ordered = sorted(stops, key=lambda s: s.seq)
    bags: list[Bag] = []
    rejects: list[tuple[StopItem, str]] = []
    current: Bag | None = None
    exhausted = False

    for item in ordered:
        if exhausted:
            # bag cap already hit: every remaining stop is rejected as-is
            rejects.append((item, bag_exhausted_reason(max_bags)))
            continue

        if item.weight_kg > max_weight or item.volume_l > max_volume:
            reason = []
            if item.weight_kg > max_weight:
                reason.append(f"超重 {item.weight_kg}>{max_weight}")
            if item.volume_l > max_volume:
                reason.append(f"超体积 {item.volume_l}>{max_volume}")
            rejects.append((item, "；".join(reason)))
            continue

        if current is None or not can_fit(current, item, max_weight, max_volume):
            if max_bags is not None and len(bags) >= max_bags:
                # one more bag would exceed the route cap: truncate here
                exhausted = True
                rejects.append((item, bag_exhausted_reason(max_bags)))
                continue
            current = Bag(bag_index=len(bags) + 1)
            bags.append(current)

        if not can_fit(current, item, max_weight, max_volume):
            # should not happen after single-item check, but keep safe
            rejects.append((item, "无法装入新袋"))
            continue

        current.items.append(item)
        current.weight_kg += item.weight_kg
        current.volume_l += item.volume_l

    return PackResult(bags=bags, rejects=rejects)
