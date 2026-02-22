"""Unit tests for reservation_system.models.

Covers Hotel, Customer, and Reservation creation, validation,
serialisation, and edge-case handling.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import unittest

from reservation_system.models import (
    Customer,
    Hotel,
    Reservation,
    _generate_id,
)


class TestHotel(unittest.TestCase):
    """Tests for the Hotel dataclass."""

    def test_create_valid_hotel(self) -> None:
        """Hotel with valid data initialises without error."""
        hotel = Hotel(
            name="Test Hotel", address="123 St", total_rooms=10,
        )
        self.assertEqual(hotel.name, "Test Hotel")
        self.assertEqual(hotel.address, "123 St")
        self.assertEqual(hotel.total_rooms, 10)
        self.assertEqual(hotel.rooms_available, 10)

    def test_create_hotel_custom_available(self) -> None:
        """Rooms_available can be set explicitly."""
        hotel = Hotel(
            name="H", address="A",
            total_rooms=10, rooms_available=5,
        )
        self.assertEqual(hotel.rooms_available, 5)

    def test_invalid_name_empty(self) -> None:
        """Empty name raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(name="", address="A", total_rooms=5)

    def test_invalid_name_type(self) -> None:
        """Non-string name raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(  # type: ignore[arg-type]
                name=123, address="A", total_rooms=5,
            )

    def test_invalid_address_empty(self) -> None:
        """Whitespace-only address raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(name="H", address="  ", total_rooms=5)

    def test_invalid_address_type(self) -> None:
        """Non-string address raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(  # type: ignore[arg-type]
                name="H", address=99, total_rooms=5,
            )

    def test_invalid_total_rooms_zero(self) -> None:
        """Zero total_rooms raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(name="H", address="A", total_rooms=0)

    def test_invalid_total_rooms_type(self) -> None:
        """Non-integer total_rooms raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(  # type: ignore[arg-type]
                name="H", address="A", total_rooms="ten",
            )

    def test_invalid_rooms_available_negative(self) -> None:
        """Negative rooms_available raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(
                name="H", address="A",
                total_rooms=5, rooms_available=-2,
            )

    def test_invalid_rooms_available_exceeds(self) -> None:
        """rooms_available > total_rooms raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(
                name="H", address="A",
                total_rooms=5, rooms_available=10,
            )

    def test_invalid_rooms_available_type(self) -> None:
        """Non-integer rooms_available raises ValueError."""
        with self.assertRaises(ValueError):
            Hotel(
                name="H", address="A", total_rooms=5,
                rooms_available="x",  # type: ignore[arg-type]
            )

    def test_to_dict(self) -> None:
        """to_dict returns a complete dictionary."""
        hotel = Hotel(name="H", address="A", total_rooms=3)
        data = hotel.to_dict()
        self.assertIn("hotel_id", data)
        self.assertEqual(data["name"], "H")

    def test_from_dict_valid(self) -> None:
        """from_dict reconstructs a Hotel from valid data."""
        data = {
            "hotel_id": "abc", "name": "H",
            "address": "A", "total_rooms": 5,
            "rooms_available": 3,
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.hotel_id, "abc")
        self.assertEqual(hotel.rooms_available, 3)

    def test_from_dict_defaults_available(self) -> None:
        """rooms_available defaults to total_rooms when absent."""
        data = {
            "hotel_id": "abc", "name": "H",
            "address": "A", "total_rooms": 7,
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.rooms_available, 7)

    def test_from_dict_missing_fields(self) -> None:
        """from_dict raises ValueError on missing keys."""
        with self.assertRaises(ValueError):
            Hotel.from_dict({"name": "H"})

    def test_str(self) -> None:
        """__str__ includes name and id."""
        hotel = Hotel(
            name="H", address="A",
            total_rooms=3, hotel_id="x",
        )
        self.assertIn("H", str(hotel))
        self.assertIn("x", str(hotel))


class TestCustomer(unittest.TestCase):
    """Tests for the Customer dataclass."""

    def test_create_valid(self) -> None:
        """Valid customer initialises correctly."""
        cust = Customer(name="Alice", email="a@b.com")
        self.assertEqual(cust.name, "Alice")

    def test_invalid_name(self) -> None:
        """Empty name raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(name="", email="a@b.com")

    def test_invalid_name_type(self) -> None:
        """Non-string name raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(  # type: ignore[arg-type]
                name=42, email="a@b.com",
            )

    def test_invalid_email_no_at(self) -> None:
        """Email without @ raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(name="A", email="invalid")

    def test_invalid_email_no_dot(self) -> None:
        """Email without dot in domain raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(name="A", email="a@b")

    def test_invalid_email_type(self) -> None:
        """Non-string email raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(  # type: ignore[arg-type]
                name="A", email=123,
            )

    def test_to_dict(self) -> None:
        """to_dict returns complete dictionary."""
        cust = Customer(name="A", email="a@b.com")
        self.assertEqual(cust.to_dict()["name"], "A")

    def test_from_dict_valid(self) -> None:
        """from_dict reconstructs from valid data."""
        data = {
            "customer_id": "c1",
            "name": "A",
            "email": "a@b.com",
        }
        cust = Customer.from_dict(data)
        self.assertEqual(cust.customer_id, "c1")

    def test_from_dict_missing(self) -> None:
        """from_dict raises ValueError on missing keys."""
        with self.assertRaises(ValueError):
            Customer.from_dict({"name": "A"})

    def test_str(self) -> None:
        """__str__ includes name and email."""
        cust = Customer(
            name="A", email="a@b.com", customer_id="c1",
        )
        self.assertIn("A", str(cust))
        self.assertIn("a@b.com", str(cust))


class TestReservation(unittest.TestCase):
    """Tests for the Reservation dataclass."""

    def test_create_valid(self) -> None:
        """Valid reservation initialises correctly."""
        res = Reservation(
            customer_id="c1", hotel_id="h1",
            check_in="2026-05-01", check_out="2026-05-03",
        )
        self.assertEqual(res.customer_id, "c1")

    def test_missing_customer_id(self) -> None:
        """Empty customer_id raises ValueError."""
        with self.assertRaises(ValueError):
            Reservation(
                customer_id="", hotel_id="h1",
                check_in="2026-05-01",
                check_out="2026-05-03",
            )

    def test_missing_hotel_id(self) -> None:
        """Empty hotel_id raises ValueError."""
        with self.assertRaises(ValueError):
            Reservation(
                customer_id="c1", hotel_id="",
                check_in="2026-05-01",
                check_out="2026-05-03",
            )

    def test_invalid_dates_format(self) -> None:
        """Non-ISO date raises ValueError."""
        with self.assertRaises(ValueError):
            Reservation(
                customer_id="c1", hotel_id="h1",
                check_in="not-a-date",
                check_out="2026-05-03",
            )

    def test_invalid_dates_type(self) -> None:
        """None date raises ValueError."""
        with self.assertRaises(ValueError):
            Reservation(
                customer_id="c1", hotel_id="h1",
                check_in=None,  # type: ignore[arg-type]
                check_out="2026-05-03",
            )

    def test_checkout_before_checkin(self) -> None:
        """check_out before check_in raises ValueError."""
        with self.assertRaises(ValueError):
            Reservation(
                customer_id="c1", hotel_id="h1",
                check_in="2026-05-05",
                check_out="2026-05-01",
            )

    def test_checkout_equals_checkin(self) -> None:
        """check_out equal to check_in raises ValueError."""
        with self.assertRaises(ValueError):
            Reservation(
                customer_id="c1", hotel_id="h1",
                check_in="2026-05-01",
                check_out="2026-05-01",
            )

    def test_to_dict(self) -> None:
        """to_dict returns a complete dictionary."""
        res = Reservation(
            customer_id="c1", hotel_id="h1",
            check_in="2026-05-01", check_out="2026-05-03",
        )
        self.assertEqual(res.to_dict()["customer_id"], "c1")

    def test_from_dict_valid(self) -> None:
        """from_dict reconstructs from valid data."""
        data = {
            "reservation_id": "r1",
            "customer_id": "c1",
            "hotel_id": "h1",
            "check_in": "2026-06-01",
            "check_out": "2026-06-05",
        }
        res = Reservation.from_dict(data)
        self.assertEqual(res.reservation_id, "r1")

    def test_from_dict_missing(self) -> None:
        """from_dict raises ValueError on missing keys."""
        with self.assertRaises(ValueError):
            Reservation.from_dict({"customer_id": "c1"})

    def test_str(self) -> None:
        """__str__ includes reservation and customer IDs."""
        res = Reservation(
            customer_id="c1", hotel_id="h1",
            check_in="2026-05-01", check_out="2026-05-03",
            reservation_id="r1",
        )
        self.assertIn("r1", str(res))
        self.assertIn("c1", str(res))


class TestGenerateId(unittest.TestCase):
    """Tests for the _generate_id helper."""

    def test_length(self) -> None:
        """Generated IDs should be 12 characters long."""
        self.assertEqual(len(_generate_id()), 12)

    def test_unique(self) -> None:
        """Generated IDs should be unique."""
        ids = {_generate_id() for _ in range(100)}
        self.assertEqual(len(ids), 100)


if __name__ == "__main__":
    unittest.main()
