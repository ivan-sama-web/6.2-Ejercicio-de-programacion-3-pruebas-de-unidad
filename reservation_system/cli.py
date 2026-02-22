#!/usr/bin/env python3
"""Command-driven console interface for the Hotel Reservation System.

A single-prompt REPL where short commands manage hotels, customers,
and reservations.  No external dependencies required.

Usage::

    python -m reservation_system.cli

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import os
import sys

# Ensure the project root is importable when running as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# pylint: disable=wrong-import-position
from reservation_system.managers import (  # noqa: E402
    CustomerManager,
    HotelManager,
    ReservationManager,
)

DATA_DIR = "data"
W = 72  # output width


# ── Formatting ──────────────────────────────────────────────────


def hr(char: str = "─") -> None:
    """Print a horizontal rule."""
    print(char * W)


def heading(text: str) -> None:
    """Print a centred heading."""
    print()
    hr("━")
    print(text.center(W))
    hr("━")


def cols(
    headers: list[str],
    rows: list[list[str]],
) -> None:
    """Print aligned columns with headers.

    Args:
        headers: Column names.
        rows: Data rows (list of string lists).
    """
    if not rows:
        print("  (empty)")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    def fmt(cells: list[str]) -> str:
        parts = []
        for i, cell in enumerate(cells):
            w = widths[i] if i < len(widths) else len(cell)
            parts.append(f"{cell:<{w}}")
        line = "  ".join(parts)
        return f"  {line}"

    print(fmt(headers))
    print("  " + "  ".join("─" * w for w in widths))
    for row in rows:
        print(fmt(row))


def ask(label: str, default: str = "") -> str:
    """Prompt the user; return default on empty input."""
    hint = f" [{default}]" if default else ""
    value = input(f"  {label}{hint}: ").strip()
    return value if value else default


def yes_no(msg: str) -> bool:
    """Ask a yes/no question."""
    return input(f"  {msg} (y/n): ").strip().lower() in (
        "y", "yes",
    )


def pick(
    items: list[tuple[str, str]],
) -> str | None:
    """Numbered picker.  Returns the ID or None.

    Args:
        items: (display_label, id_value) pairs.
    """
    if not items:
        print("  (none available)")
        return None
    for i, (label, _) in enumerate(items, 1):
        print(f"  [{i}] {label}")
    raw = input("  #: ").strip()
    try:
        idx = int(raw)
    except ValueError:
        return None
    if idx < 1 or idx > len(items):
        return None
    return items[idx - 1][1]


# ── Status bar ──────────────────────────────────────────────────


def status(
    hm: HotelManager,
    cm: CustomerManager,
    rm: ReservationManager,
) -> None:
    """Print a compact status line."""
    hotels = hm.list_hotels()
    avail = sum(h.rooms_available for h in hotels)
    total = sum(h.total_rooms for h in hotels)
    n_h = len(hotels)
    n_c = len(cm.list_customers())
    n_r = len(rm.list_reservations())
    status_line = (
        f"  Hotels: {n_h}  |  "
        f"Customers: {n_c}  |  "
        f"Reservations: {n_r}  |  "
        f"Rooms: {avail}/{total} free"
    )
    print()
    print("System status:")
    hr()
    print(status_line)
    hr()


# ── Hotel commands ──────────────────────────────────────────────


def hotel_list(hm: HotelManager) -> None:
    """Show all hotels."""
    heading("Hotels")
    hotels = hm.list_hotels()
    cols(
        ["#", "ID", "Name", "Address", "Rooms", "Avail"],
        [
            [
                str(i), h.hotel_id, h.name,
                h.address, str(h.total_rooms),
                str(h.rooms_available),
            ]
            for i, h in enumerate(hotels, 1)
        ],
    )


def hotel_add(hm: HotelManager) -> None:
    """Create a hotel interactively."""
    heading("Add Hotel")
    name = ask("Name")
    if not name:
        print("  Cancelled.")
        return
    address = ask("Address")
    rooms = ask("Total rooms")
    try:
        hotel = hm.create_hotel(name, address, int(rooms))
        print(f"\n  + Created: {hotel}")
    except (ValueError, TypeError) as exc:
        print(f"\n  ! Error: {exc}")


def hotel_edit(hm: HotelManager) -> None:
    """Edit a hotel interactively."""
    heading("Edit Hotel")
    hotels = hm.list_hotels()
    hid = pick([
        (f"{h.name} ({h.hotel_id})", h.hotel_id)
        for h in hotels
    ])
    if not hid:
        print("  Cancelled.")
        return
    hotel = hm.get_hotel(hid)
    if not hotel:
        return
    print(f"\n  Editing {hotel.name}  (Enter = keep)")
    name = ask("Name", hotel.name)
    address = ask("Address", hotel.address)
    rooms = ask("Total rooms", str(hotel.total_rooms))
    try:
        result = hm.modify_hotel(
            hid, name=name, address=address,
            total_rooms=int(rooms),
        )
        if result:
            print(f"\n  + Updated: {result}")
        else:
            print("\n  ! Validation failed.")
    except (ValueError, TypeError) as exc:
        print(f"\n  ! Error: {exc}")


def hotel_delete(hm: HotelManager) -> None:
    """Delete a hotel interactively."""
    heading("Delete Hotel")
    hotels = hm.list_hotels()
    hid = pick([
        (f"{h.name} ({h.hotel_id})", h.hotel_id)
        for h in hotels
    ])
    if not hid:
        print("  Cancelled.")
        return
    hotel = hm.get_hotel(hid)
    if hotel and yes_no(f"Delete '{hotel.name}'?"):
        if hm.delete_hotel(hid):
            print("  + Deleted.")
        else:
            print("  ! Failed.")
    else:
        print("  Cancelled.")


# ── Customer commands ───────────────────────────────────────────


def cust_list(cm: CustomerManager) -> None:
    """Show all customers."""
    heading("Customers")
    custs = cm.list_customers()
    cols(
        ["#", "ID", "Name", "Email"],
        [
            [str(i), c.customer_id, c.name, c.email]
            for i, c in enumerate(custs, 1)
        ],
    )


def cust_add(cm: CustomerManager) -> None:
    """Create a customer interactively."""
    heading("Add Customer")
    name = ask("Name")
    if not name:
        print("  Cancelled.")
        return
    email = ask("Email")
    try:
        cust = cm.create_customer(name, email)
        print(f"\n  + Created: {cust}")
    except (ValueError, TypeError) as exc:
        print(f"\n  ! Error: {exc}")


def cust_edit(cm: CustomerManager) -> None:
    """Edit a customer interactively."""
    heading("Edit Customer")
    custs = cm.list_customers()
    cid = pick([
        (f"{c.name} <{c.email}>", c.customer_id)
        for c in custs
    ])
    if not cid:
        print("  Cancelled.")
        return
    cust = cm.get_customer(cid)
    if not cust:
        return
    print(f"\n  Editing {cust.name}  (Enter = keep)")
    name = ask("Name", cust.name)
    email = ask("Email", cust.email)
    try:
        result = cm.modify_customer(
            cid, name=name, email=email,
        )
        if result:
            print(f"\n  + Updated: {result}")
        else:
            print("\n  ! Validation failed.")
    except (ValueError, TypeError) as exc:
        print(f"\n  ! Error: {exc}")


def cust_delete(cm: CustomerManager) -> None:
    """Delete a customer interactively."""
    heading("Delete Customer")
    custs = cm.list_customers()
    cid = pick([
        (f"{c.name} <{c.email}>", c.customer_id)
        for c in custs
    ])
    if not cid:
        print("  Cancelled.")
        return
    cust = cm.get_customer(cid)
    if cust and yes_no(f"Delete '{cust.name}'?"):
        if cm.delete_customer(cid):
            print("  + Deleted.")
        else:
            print("  ! Failed.")
    else:
        print("  Cancelled.")


# ── Reservation commands ────────────────────────────────────────


def res_list(
    hm: HotelManager,
    cm: CustomerManager,
    rm: ReservationManager,
) -> None:
    """Show all reservations."""
    heading("Reservations")
    rows = []
    for i, r in enumerate(rm.list_reservations(), 1):
        cust = cm.get_customer(r.customer_id)
        hotel = hm.get_hotel(r.hotel_id)
        rows.append([
            str(i),
            r.reservation_id,
            cust.name if cust else r.customer_id,
            hotel.name if hotel else r.hotel_id,
            r.check_in,
            r.check_out,
        ])
    cols(
        ["#", "ID", "Customer", "Hotel", "In", "Out"],
        rows,
    )


def res_new(
    hm: HotelManager,
    cm: CustomerManager,
    rm: ReservationManager,
) -> None:
    """Create a reservation interactively."""
    heading("New Reservation")
    custs = cm.list_customers()
    hotels = hm.list_hotels()
    if not custs:
        print("  No customers — create one first.")
        return
    if not hotels:
        print("  No hotels — create one first.")
        return

    print("  Customer:")
    cid = pick([
        (f"{c.name} <{c.email}>", c.customer_id)
        for c in custs
    ])
    if not cid:
        print("  Cancelled.")
        return

    print("\n  Hotel:")
    hid = pick([
        (
            f"{h.name}  [{h.rooms_available}/"
            f"{h.total_rooms} free]",
            h.hotel_id,
        )
        for h in hotels
    ])
    if not hid:
        print("  Cancelled.")
        return

    check_in = ask("Check-in  (YYYY-MM-DD)")
    check_out = ask("Check-out (YYYY-MM-DD)")

    res = rm.create_reservation(cid, hid, check_in, check_out)
    if res:
        print(f"\n  + Booked: {res}")
    else:
        print(
            "\n  ! Failed — check dates and availability."
        )


def res_cancel(
    hm: HotelManager,
    cm: CustomerManager,
    rm: ReservationManager,
) -> None:
    """Cancel a reservation interactively."""
    heading("Cancel Reservation")
    reservations = rm.list_reservations()
    items = []
    for r in reservations:
        cust = cm.get_customer(r.customer_id)
        hotel = hm.get_hotel(r.hotel_id)
        label = (
            f"{cust.name if cust else r.customer_id} @ "
            f"{hotel.name if hotel else r.hotel_id}  "
            f"{r.check_in} -> {r.check_out}"
        )
        items.append((label, r.reservation_id))

    rid = pick(items)
    if not rid:
        print("  Cancelled.")
        return
    if yes_no("Confirm cancellation?"):
        if rm.cancel_reservation(rid):
            print("  + Reservation cancelled.")
        else:
            print("  ! Failed.")
    else:
        print("  Kept.")


# ── Help text ───────────────────────────────────────────────────

HELP = """\

Command reference:
  HOTELS               CUSTOMERS           RESERVATIONS
  -----------------    ----------------    -------------------
  h  : list hotels     c  : list custs     r  : list bookings
  ha : add hotel       ca : add cust       rn : new booking
  he : edit hotel      ce : edit cust      rc : cancel booking
  hd : delete hotel    cd : delete cust

  GENERAL
  ----------------------------------
  s : status    ? : help    q ; quit
"""


def show_help() -> None:
    """Print the command reference."""
    heading("Commands")
    print(HELP)


# ── Command router ──────────────────────────────────────────────

# Maps command strings to (handler, args_needed) where
# args_needed is a tuple of manager attribute names.
COMMANDS: dict[str, tuple[str, ...]] = {
    "h":  ("hotel_list", "hm"),
    "ha": ("hotel_add", "hm"),
    "he": ("hotel_edit", "hm"),
    "hd": ("hotel_delete", "hm"),
    "c":  ("cust_list", "cm"),
    "ca": ("cust_add", "cm"),
    "ce": ("cust_edit", "cm"),
    "cd": ("cust_delete", "cm"),
    "r":  ("res_list", "hm", "cm", "rm"),
    "rn": ("res_new", "hm", "cm", "rm"),
    "rc": ("res_cancel", "hm", "cm", "rm"),
}


def dispatch(
    cmd: str,
    managers: dict[str, object],
) -> bool:
    """Run a command.  Returns False to quit.

    Args:
        cmd: User-entered command string.
        managers: Dict mapping 'hm', 'cm', 'rm' to managers.

    Returns:
        True to continue the loop, False to quit.
    """
    cmd = cmd.strip().lower()
    if cmd in ("q", "quit", "exit"):
        return False
    if cmd in ("?", "help"):
        show_help()
        return True
    if cmd in ("s", "status"):
        status(
            managers["hm"],  # type: ignore[arg-type]
            managers["cm"],  # type: ignore[arg-type]
            managers["rm"],  # type: ignore[arg-type]
        )
        return True
    spec = COMMANDS.get(cmd)
    if spec is None:
        print(f"  Unknown command: '{cmd}'  (type ? for help)")
        return True
    func_name = spec[0]
    arg_keys = spec[1:]
    func = globals()[func_name]
    args = [managers[k] for k in arg_keys]
    func(*args)
    return True


# ── Main loop ───────────────────────────────────────────────────


def main() -> None:
    """Entry point — REPL loop."""
    os.makedirs(DATA_DIR, exist_ok=True)
    hm = HotelManager(
        os.path.join(DATA_DIR, "hotels.json"),
    )
    cm = CustomerManager(
        os.path.join(DATA_DIR, "customers.json"),
    )
    rm = ReservationManager(
        os.path.join(DATA_DIR, "reservations.json"),
        hotel_manager=hm,
        customer_manager=cm,
    )
    managers: dict[str, object] = {
        "hm": hm, "cm": cm, "rm": rm,
    }

    os.system("cls" if os.name == "nt" else "clear")
    heading("Hotel Reservation System")
    status(hm, cm, rm)
    print(HELP)

    while True:
        try:
            cmd = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue
        if not dispatch(cmd, managers):
            print("\n  Goodbye!\n")
            break


if __name__ == "__main__":  # pragma: no cover
    main()
