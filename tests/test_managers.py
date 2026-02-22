"""Unit tests for reservation_system.managers.

Covers HotelManager, CustomerManager, and ReservationManager CRUD
operations, error handling, and persistence round-trips.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from reservation_system.managers import (
    CustomerManager,
    HotelManager,
    ReservationManager,
)


class _TempFilesMixin:
    """Provide temporary JSON file paths for each test."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        """Create temporary directory and file paths."""
        self._tmpdir_obj = (  # pylint: disable=consider-using-with
            tempfile.TemporaryDirectory()
        )
        self.tmpdir = self._tmpdir_obj.name
        self.hotels_path = os.path.join(
            self.tmpdir, "hotels.json",
        )
        self.customers_path = os.path.join(
            self.tmpdir, "customers.json",
        )
        self.reservations_path = os.path.join(
            self.tmpdir, "reservations.json",
        )

    def tearDown(self) -> None:  # pylint: disable=invalid-name
        """Clean up temporary directory."""
        self._tmpdir_obj.cleanup()


# ==================================================================
# HotelManager Tests
# ==================================================================
class TestHotelManager(_TempFilesMixin, unittest.TestCase):
    """Tests for HotelManager."""

    def _manager(self) -> HotelManager:
        """Return a fresh HotelManager backed by a temp file."""
        return HotelManager(filepath=self.hotels_path)

    def test_create_hotel(self) -> None:
        """create_hotel persists and returns a Hotel."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 10)
        self.assertEqual(hotel.name, "H")
        self.assertEqual(len(mgr.list_hotels()), 1)

    def test_delete_hotel(self) -> None:
        """delete_hotel removes the hotel."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 10)
        self.assertTrue(mgr.delete_hotel(hotel.hotel_id))
        self.assertEqual(len(mgr.list_hotels()), 0)

    def test_delete_hotel_not_found(self) -> None:
        """delete_hotel returns False for unknown ID."""
        mgr = self._manager()
        self.assertFalse(mgr.delete_hotel("missing"))

    def test_get_hotel(self) -> None:
        """get_hotel returns Hotel or None."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 5)
        self.assertIsNotNone(mgr.get_hotel(hotel.hotel_id))
        self.assertIsNone(mgr.get_hotel("nope"))

    def test_display_hotel(self) -> None:
        """display_hotel returns info string for valid ID."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 5)
        self.assertIn("H", mgr.display_hotel(hotel.hotel_id))

    def test_display_hotel_not_found(self) -> None:
        """display_hotel returns error for unknown ID."""
        mgr = self._manager()
        self.assertIn("[ERROR]", mgr.display_hotel("nope"))

    def test_modify_hotel(self) -> None:
        """modify_hotel updates and persists changes."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 10)
        updated = mgr.modify_hotel(hotel.hotel_id, name="New")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "New")

    def test_modify_hotel_not_found(self) -> None:
        """modify_hotel returns None for unknown ID."""
        mgr = self._manager()
        self.assertIsNone(mgr.modify_hotel("nope", name="X"))

    def test_modify_hotel_invalid(self) -> None:
        """modify_hotel returns None on invalid values."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 10)
        self.assertIsNone(
            mgr.modify_hotel(hotel.hotel_id, total_rooms=-5)
        )

    def test_modify_hotel_unknown_field(self) -> None:
        """modify_hotel ignores unknown fields."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 10)
        self.assertIsNotNone(
            mgr.modify_hotel(hotel.hotel_id, zzz=99)
        )

    def test_reserve_room(self) -> None:
        """reserve_room decrements rooms_available."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 2)
        self.assertTrue(mgr.reserve_room(hotel.hotel_id))
        self.assertEqual(
            mgr.get_hotel(hotel.hotel_id).rooms_available, 1,
        )

    def test_reserve_room_no_availability(self) -> None:
        """reserve_room returns False when sold out."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 1)
        mgr.reserve_room(hotel.hotel_id)
        self.assertFalse(mgr.reserve_room(hotel.hotel_id))

    def test_reserve_room_not_found(self) -> None:
        """reserve_room returns False for unknown ID."""
        mgr = self._manager()
        self.assertFalse(mgr.reserve_room("nope"))

    def test_cancel_room(self) -> None:
        """cancel_room increments rooms_available."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 2)
        mgr.reserve_room(hotel.hotel_id)
        self.assertTrue(mgr.cancel_room(hotel.hotel_id))
        self.assertEqual(
            mgr.get_hotel(hotel.hotel_id).rooms_available, 2,
        )

    def test_cancel_room_already_full(self) -> None:
        """cancel_room returns False when all rooms are free."""
        mgr = self._manager()
        hotel = mgr.create_hotel("H", "A", 2)
        self.assertFalse(mgr.cancel_room(hotel.hotel_id))

    def test_cancel_room_not_found(self) -> None:
        """cancel_room returns False for unknown ID."""
        mgr = self._manager()
        self.assertFalse(mgr.cancel_room("nope"))

    def test_persistence_roundtrip(self) -> None:
        """Hotels survive a save/reload cycle."""
        mgr = self._manager()
        mgr.create_hotel("H", "A", 5)
        mgr2 = HotelManager(filepath=self.hotels_path)
        self.assertEqual(len(mgr2.list_hotels()), 1)

    def test_load_with_invalid_records(self) -> None:
        """Invalid records in file are skipped."""
        with open(
            self.hotels_path, "w", encoding="utf-8",
        ) as fh:
            json.dump(
                [{"hotel_id": "x", "name": "",
                  "address": "A", "total_rooms": 5}],
                fh,
            )
        mgr = HotelManager(filepath=self.hotels_path)
        self.assertEqual(len(mgr.list_hotels()), 0)


# ==================================================================
# CustomerManager Tests
# ==================================================================
class TestCustomerManager(_TempFilesMixin, unittest.TestCase):
    """Tests for CustomerManager."""

    def _manager(self) -> CustomerManager:
        """Return a fresh CustomerManager."""
        return CustomerManager(filepath=self.customers_path)

    def test_create_customer(self) -> None:
        """create_customer persists and returns a Customer."""
        mgr = self._manager()
        cust = mgr.create_customer("Alice", "a@b.com")
        self.assertEqual(cust.name, "Alice")
        self.assertEqual(len(mgr.list_customers()), 1)

    def test_delete_customer(self) -> None:
        """delete_customer removes the customer."""
        mgr = self._manager()
        cust = mgr.create_customer("A", "a@b.com")
        self.assertTrue(mgr.delete_customer(cust.customer_id))
        self.assertEqual(len(mgr.list_customers()), 0)

    def test_delete_customer_not_found(self) -> None:
        """delete_customer returns False for unknown ID."""
        mgr = self._manager()
        self.assertFalse(mgr.delete_customer("missing"))

    def test_get_customer(self) -> None:
        """get_customer returns Customer or None."""
        mgr = self._manager()
        cust = mgr.create_customer("A", "a@b.com")
        self.assertIsNotNone(
            mgr.get_customer(cust.customer_id),
        )
        self.assertIsNone(mgr.get_customer("nope"))

    def test_display_customer(self) -> None:
        """display_customer returns info for valid ID."""
        mgr = self._manager()
        cust = mgr.create_customer("A", "a@b.com")
        info = mgr.display_customer(cust.customer_id)
        self.assertIn("A", info)

    def test_display_customer_not_found(self) -> None:
        """display_customer returns error for unknown ID."""
        mgr = self._manager()
        self.assertIn(
            "[ERROR]", mgr.display_customer("nope"),
        )

    def test_modify_customer(self) -> None:
        """modify_customer updates and persists changes."""
        mgr = self._manager()
        cust = mgr.create_customer("A", "a@b.com")
        updated = mgr.modify_customer(
            cust.customer_id, name="B",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "B")

    def test_modify_customer_not_found(self) -> None:
        """modify_customer returns None for unknown ID."""
        mgr = self._manager()
        self.assertIsNone(
            mgr.modify_customer("nope", name="X"),
        )

    def test_modify_customer_invalid(self) -> None:
        """modify_customer returns None on invalid values."""
        mgr = self._manager()
        cust = mgr.create_customer("A", "a@b.com")
        self.assertIsNone(
            mgr.modify_customer(cust.customer_id, email="bad"),
        )

    def test_modify_customer_unknown_field(self) -> None:
        """modify_customer ignores unknown fields."""
        mgr = self._manager()
        cust = mgr.create_customer("A", "a@b.com")
        self.assertIsNotNone(
            mgr.modify_customer(cust.customer_id, zzz=1),
        )

    def test_persistence_roundtrip(self) -> None:
        """Customers survive a save/reload cycle."""
        mgr = self._manager()
        mgr.create_customer("A", "a@b.com")
        mgr2 = CustomerManager(filepath=self.customers_path)
        self.assertEqual(len(mgr2.list_customers()), 1)

    def test_load_with_invalid_records(self) -> None:
        """Invalid records are skipped on load."""
        with open(
            self.customers_path, "w", encoding="utf-8",
        ) as fh:
            json.dump(
                [{"customer_id": "x", "name": "",
                  "email": "a@b.com"}],
                fh,
            )
        mgr = CustomerManager(filepath=self.customers_path)
        self.assertEqual(len(mgr.list_customers()), 0)


# ==================================================================
# ReservationManager Tests
# ==================================================================
class TestReservationManager(
    _TempFilesMixin, unittest.TestCase,
):
    """Tests for ReservationManager."""

    def _managers(
        self,
    ) -> tuple[
        HotelManager, CustomerManager, ReservationManager,
    ]:
        """Create a linked set of managers."""
        hotel_mgr = HotelManager(filepath=self.hotels_path)
        cust_mgr = CustomerManager(
            filepath=self.customers_path,
        )
        res_mgr = ReservationManager(
            filepath=self.reservations_path,
            hotel_manager=hotel_mgr,
            customer_manager=cust_mgr,
        )
        return hotel_mgr, cust_mgr, res_mgr

    def test_create_reservation(self) -> None:
        """create_reservation links customer to hotel."""
        hotel_mgr, cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 5)
        cust = cust_mgr.create_customer("A", "a@b.com")
        res = res_mgr.create_reservation(
            cust.customer_id, hotel.hotel_id,
            "2026-07-01", "2026-07-05",
        )
        self.assertIsNotNone(res)
        self.assertEqual(
            hotel_mgr.get_hotel(hotel.hotel_id).rooms_available,
            4,
        )
        self.assertEqual(len(res_mgr.list_reservations()), 1)

    def test_create_reservation_no_customer(self) -> None:
        """create_reservation fails for missing customer."""
        hotel_mgr, _cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 5)
        self.assertIsNone(
            res_mgr.create_reservation(
                "missing", hotel.hotel_id,
                "2026-07-01", "2026-07-05",
            )
        )

    def test_create_reservation_no_hotel(self) -> None:
        """create_reservation fails for missing hotel."""
        _hotel_mgr, cust_mgr, res_mgr = self._managers()
        cust = cust_mgr.create_customer("A", "a@b.com")
        self.assertIsNone(
            res_mgr.create_reservation(
                cust.customer_id, "missing",
                "2026-07-01", "2026-07-05",
            )
        )

    def test_create_reservation_no_rooms(self) -> None:
        """create_reservation fails when hotel is full."""
        hotel_mgr, cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 1)
        cust = cust_mgr.create_customer("A", "a@b.com")
        res_mgr.create_reservation(
            cust.customer_id, hotel.hotel_id,
            "2026-07-01", "2026-07-05",
        )
        self.assertIsNone(
            res_mgr.create_reservation(
                cust.customer_id, hotel.hotel_id,
                "2026-07-06", "2026-07-10",
            )
        )

    def test_create_reservation_invalid_dates(self) -> None:
        """create_reservation rollbacks room on invalid dates."""
        hotel_mgr, cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 5)
        cust = cust_mgr.create_customer("A", "a@b.com")
        self.assertIsNone(
            res_mgr.create_reservation(
                cust.customer_id, hotel.hotel_id,
                "bad", "data",
            )
        )
        self.assertEqual(
            hotel_mgr.get_hotel(hotel.hotel_id).rooms_available,
            5,
        )

    def test_cancel_reservation(self) -> None:
        """cancel_reservation frees the room."""
        hotel_mgr, cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 5)
        cust = cust_mgr.create_customer("A", "a@b.com")
        res = res_mgr.create_reservation(
            cust.customer_id, hotel.hotel_id,
            "2026-07-01", "2026-07-05",
        )
        self.assertTrue(
            res_mgr.cancel_reservation(res.reservation_id),
        )
        self.assertEqual(
            hotel_mgr.get_hotel(hotel.hotel_id).rooms_available,
            5,
        )
        self.assertEqual(len(res_mgr.list_reservations()), 0)

    def test_cancel_reservation_not_found(self) -> None:
        """cancel_reservation returns False for unknown ID."""
        _hotel_mgr, _cust_mgr, res_mgr = self._managers()
        self.assertFalse(res_mgr.cancel_reservation("nope"))

    def test_get_reservation(self) -> None:
        """get_reservation returns Reservation or None."""
        hotel_mgr, cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 5)
        cust = cust_mgr.create_customer("A", "a@b.com")
        res = res_mgr.create_reservation(
            cust.customer_id, hotel.hotel_id,
            "2026-07-01", "2026-07-05",
        )
        self.assertIsNotNone(
            res_mgr.get_reservation(res.reservation_id),
        )
        self.assertIsNone(res_mgr.get_reservation("nope"))

    def test_persistence_roundtrip(self) -> None:
        """Reservations survive save/reload."""
        hotel_mgr, cust_mgr, res_mgr = self._managers()
        hotel = hotel_mgr.create_hotel("H", "A", 5)
        cust = cust_mgr.create_customer("A", "a@b.com")
        res_mgr.create_reservation(
            cust.customer_id, hotel.hotel_id,
            "2026-07-01", "2026-07-05",
        )
        res_mgr2 = ReservationManager(
            filepath=self.reservations_path,
            hotel_manager=hotel_mgr,
            customer_manager=cust_mgr,
        )
        self.assertEqual(len(res_mgr2.list_reservations()), 1)

    def test_load_with_invalid_records(self) -> None:
        """Invalid records are skipped on load."""
        with open(
            self.reservations_path, "w", encoding="utf-8",
        ) as fh:
            json.dump([{"reservation_id": "x"}], fh)
        res_mgr = ReservationManager(
            filepath=self.reservations_path,
        )
        self.assertEqual(len(res_mgr.list_reservations()), 0)

    def test_create_reservation_no_managers(self) -> None:
        """ReservationManager works without linked managers."""
        res_mgr = ReservationManager(
            filepath=self.reservations_path,
            hotel_manager=None,
            customer_manager=None,
        )
        res = res_mgr.create_reservation(
            "c1", "h1", "2026-08-01", "2026-08-05",
        )
        self.assertIsNotNone(res)

    def test_cancel_reservation_no_hotel_manager(self) -> None:
        """Cancel works without hotel_manager."""
        res_mgr = ReservationManager(
            filepath=self.reservations_path,
            hotel_manager=None,
            customer_manager=None,
        )
        res = res_mgr.create_reservation(
            "c1", "h1", "2026-08-01", "2026-08-05",
        )
        self.assertTrue(
            res_mgr.cancel_reservation(res.reservation_id),
        )


if __name__ == "__main__":
    unittest.main()
