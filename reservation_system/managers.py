"""Manager classes for Hotels, Customers, and Reservations.

Each manager encapsulates CRUD operations and delegates persistence
to the :mod:`persistence` module.  Errors from corrupt data are logged
to the console and skipped so that execution continues (Req 5).

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

from typing import Any

from reservation_system.models import Customer, Hotel, Reservation
from reservation_system.persistence import load_json, save_json


# ------------------------------------------------------------------
# Hotel Manager
# ------------------------------------------------------------------
class HotelManager:
    """Manage hotel records stored in a JSON file.

    Args:
        filepath: Path to the hotels JSON file.
    """

    def __init__(self, filepath: str = "data/hotels.json") -> None:
        self.filepath = filepath
        self._hotels: dict[str, Hotel] = {}
        self._load()

    # -- internal helpers ------------------------------------------
    def _load(self) -> None:
        """Load hotels from disk, skipping invalid records."""
        self._hotels.clear()
        for record in load_json(self.filepath):
            try:
                hotel = Hotel.from_dict(record)
                self._hotels[hotel.hotel_id] = hotel
            except (ValueError, KeyError, TypeError) as exc:
                print(
                    f"[WARNING] Skipping invalid hotel record: "
                    f"{exc}"
                )

    def _save(self) -> None:
        """Persist all hotels to disk."""
        save_json(
            self.filepath,
            [h.to_dict() for h in self._hotels.values()],
        )

    # -- public API -----------------------------------------------
    def create_hotel(
        self, name: str, address: str, total_rooms: int
    ) -> Hotel:
        """Create and persist a new hotel.

        Returns:
            The newly created :class:`Hotel`.
        """
        hotel = Hotel(
            name=name, address=address, total_rooms=total_rooms
        )
        self._hotels[hotel.hotel_id] = hotel
        self._save()
        return hotel

    def delete_hotel(self, hotel_id: str) -> bool:
        """Delete a hotel by its ID.

        Returns:
            *True* if the hotel was found and deleted, *False* otherwise.
        """
        if hotel_id not in self._hotels:
            print(f"[ERROR] Hotel '{hotel_id}' not found.")
            return False
        del self._hotels[hotel_id]
        self._save()
        return True

    def get_hotel(self, hotel_id: str) -> Hotel | None:
        """Return a hotel by ID or *None*."""
        return self._hotels.get(hotel_id)

    def display_hotel(self, hotel_id: str) -> str:
        """Return a human-readable string for a hotel.

        Returns:
            The string representation, or an error message.
        """
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            msg = f"[ERROR] Hotel '{hotel_id}' not found."
            print(msg)
            return msg
        info = str(hotel)
        print(info)
        return info

    def modify_hotel(
        self, hotel_id: str, **kwargs: Any
    ) -> Hotel | None:
        """Modify one or more attributes of an existing hotel.

        Accepted keyword arguments: *name*, *address*, *total_rooms*,
        *rooms_available*.

        Returns:
            The updated :class:`Hotel`, or *None* on failure.
        """
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            print(f"[ERROR] Hotel '{hotel_id}' not found.")
            return None
        allowed = {"name", "address", "total_rooms", "rooms_available"}
        for key, value in kwargs.items():
            if key not in allowed:
                print(f"[WARNING] Ignoring unknown field '{key}'.")
                continue
            setattr(hotel, key, value)
        try:
            hotel.validate()
        except ValueError as exc:
            print(f"[ERROR] Invalid modification: {exc}")
            self._load()  # rollback
            return None
        self._save()
        return hotel

    def reserve_room(self, hotel_id: str) -> bool:
        """Decrement available rooms by one.

        Returns:
            *True* on success, *False* if no rooms are available.
        """
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            print(f"[ERROR] Hotel '{hotel_id}' not found.")
            return False
        if hotel.rooms_available <= 0:
            print(f"[ERROR] No rooms available at '{hotel.name}'.")
            return False
        hotel.rooms_available -= 1
        self._save()
        return True

    def cancel_room(self, hotel_id: str) -> bool:
        """Increment available rooms by one (room freed).

        Returns:
            *True* on success, *False* on failure.
        """
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            print(f"[ERROR] Hotel '{hotel_id}' not found.")
            return False
        if hotel.rooms_available >= hotel.total_rooms:
            print(f"[ERROR] All rooms already available at '{hotel.name}'.")
            return False
        hotel.rooms_available += 1
        self._save()
        return True

    def list_hotels(self) -> list[Hotel]:
        """Return all loaded hotels."""
        return list(self._hotels.values())


# ------------------------------------------------------------------
# Customer Manager
# ------------------------------------------------------------------
class CustomerManager:
    """Manage customer records stored in a JSON file.

    Args:
        filepath: Path to the customers JSON file.
    """

    def __init__(
        self, filepath: str = "data/customers.json"
    ) -> None:
        self.filepath = filepath
        self._customers: dict[str, Customer] = {}
        self._load()

    def _load(self) -> None:
        self._customers.clear()
        for record in load_json(self.filepath):
            try:
                customer = Customer.from_dict(record)
                self._customers[customer.customer_id] = customer
            except (ValueError, KeyError, TypeError) as exc:
                print(
                    f"[WARNING] Skipping invalid customer record: "
                    f"{exc}"
                )

    def _save(self) -> None:
        save_json(
            self.filepath,
            [c.to_dict() for c in self._customers.values()],
        )

    def create_customer(self, name: str, email: str) -> Customer:
        """Create and persist a new customer."""
        customer = Customer(name=name, email=email)
        self._customers[customer.customer_id] = customer
        self._save()
        return customer

    def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer by ID."""
        if customer_id not in self._customers:
            print(f"[ERROR] Customer '{customer_id}' not found.")
            return False
        del self._customers[customer_id]
        self._save()
        return True

    def get_customer(self, customer_id: str) -> Customer | None:
        """Return a customer by ID or *None*."""
        return self._customers.get(customer_id)

    def display_customer(self, customer_id: str) -> str:
        """Return a human-readable string for a customer."""
        customer = self.get_customer(customer_id)
        if customer is None:
            msg = f"[ERROR] Customer '{customer_id}' not found."
            print(msg)
            return msg
        info = str(customer)
        print(info)
        return info

    def modify_customer(
        self, customer_id: str, **kwargs: Any
    ) -> Customer | None:
        """Modify customer attributes (*name*, *email*)."""
        customer = self.get_customer(customer_id)
        if customer is None:
            print(f"[ERROR] Customer '{customer_id}' not found.")
            return None
        allowed = {"name", "email"}
        for key, value in kwargs.items():
            if key not in allowed:
                print(f"[WARNING] Ignoring unknown field '{key}'.")
                continue
            setattr(customer, key, value)
        try:
            customer.validate()
        except ValueError as exc:
            print(f"[ERROR] Invalid modification: {exc}")
            self._load()
            return None
        self._save()
        return customer

    def list_customers(self) -> list[Customer]:
        """Return all loaded customers."""
        return list(self._customers.values())


# ------------------------------------------------------------------
# Reservation Manager
# ------------------------------------------------------------------
class ReservationManager:
    """Manage reservation records, coordinating with hotel/customer managers.

    Args:
        filepath: Path to the reservations JSON file.
        hotel_manager: Instance of :class:`HotelManager`.
        customer_manager: Instance of :class:`CustomerManager`.
    """

    def __init__(
        self,
        filepath: str = "data/reservations.json",
        hotel_manager: HotelManager | None = None,
        customer_manager: CustomerManager | None = None,
    ) -> None:
        self.filepath = filepath
        self.hotel_manager = hotel_manager
        self.customer_manager = customer_manager
        self._reservations: dict[str, Reservation] = {}
        self._load()

    def _load(self) -> None:
        self._reservations.clear()
        for record in load_json(self.filepath):
            try:
                res = Reservation.from_dict(record)
                self._reservations[res.reservation_id] = res
            except (ValueError, KeyError, TypeError) as exc:
                print(
                    f"[WARNING] Skipping invalid reservation record: "
                    f"{exc}"
                )

    def _save(self) -> None:
        save_json(
            self.filepath,
            [r.to_dict() for r in self._reservations.values()],
        )

    def create_reservation(
        self,
        customer_id: str,
        hotel_id: str,
        check_in: str,
        check_out: str,
    ) -> Reservation | None:
        """Create a reservation if customer, hotel exist and rooms are free.

        Returns:
            The new :class:`Reservation`, or *None* on failure.
        """
        if self.customer_manager is not None:
            if self.customer_manager.get_customer(customer_id) is None:
                print(
                    f"[ERROR] Customer '{customer_id}' not found."
                )
                return None
        if self.hotel_manager is not None:
            if self.hotel_manager.get_hotel(hotel_id) is None:
                print(f"[ERROR] Hotel '{hotel_id}' not found.")
                return None
            if not self.hotel_manager.reserve_room(hotel_id):
                return None
        try:
            reservation = Reservation(
                customer_id=customer_id,
                hotel_id=hotel_id,
                check_in=check_in,
                check_out=check_out,
            )
        except ValueError as exc:
            print(f"[ERROR] Invalid reservation data: {exc}")
            if self.hotel_manager is not None:
                self.hotel_manager.cancel_room(hotel_id)
            return None
        self._reservations[reservation.reservation_id] = reservation
        self._save()
        return reservation

    def cancel_reservation(self, reservation_id: str) -> bool:
        """Cancel (delete) a reservation, freeing the hotel room.

        Returns:
            *True* on success, *False* if the reservation was not found.
        """
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            print(
                f"[ERROR] Reservation '{reservation_id}' not found."
            )
            return False
        if self.hotel_manager is not None:
            self.hotel_manager.cancel_room(reservation.hotel_id)
        del self._reservations[reservation_id]
        self._save()
        return True

    def get_reservation(
        self, reservation_id: str
    ) -> Reservation | None:
        """Return a reservation by ID or *None*."""
        return self._reservations.get(reservation_id)

    def list_reservations(self) -> list[Reservation]:
        """Return all loaded reservations."""
        return list(self._reservations.values())
