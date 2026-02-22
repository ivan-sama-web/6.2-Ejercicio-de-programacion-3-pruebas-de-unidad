"""Unit tests for reservation_system.cli.

Achieves 100 % line coverage of the CLI module by exercising every
function, branch, and edge case through mocked ``input()`` calls
and temporary data files.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from reservation_system.managers import (
    CustomerManager,
    HotelManager,
    ReservationManager,
)
from reservation_system import cli


# pylint: disable=too-many-instance-attributes
class _CliTestBase(unittest.TestCase):
    """Shared setup: isolated managers in a temp directory."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir.name
        hp = os.path.join(self.tmpdir, "hotels.json")
        cp = os.path.join(self.tmpdir, "customers.json")
        rp = os.path.join(self.tmpdir, "reservations.json")
        self.hm = HotelManager(hp)
        self.cm = CustomerManager(cp)
        self.rm = ReservationManager(
            rp, hotel_manager=self.hm,
            customer_manager=self.cm,
        )
        self.mgrs: dict[str, object] = {
            "hm": self.hm, "cm": self.cm, "rm": self.rm,
        }
        # Seed one hotel + one customer for reservation tests.
        self.hotel = self.hm.create_hotel("Inn", "1 Rd", 10)
        self.cust = self.cm.create_customer(
            "Alice", "a@b.com",
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    # Helper: feed a list of strings to input().
    @staticmethod
    def _patch_input(values: list[str]):
        return mock.patch(
            "builtins.input", side_effect=values,
        )


# ================================================================
# Formatting helpers
# ================================================================
class TestHr(_CliTestBase):
    """Tests for hr()."""

    def test_default_char(self) -> None:
        """hr() prints 72 dashes by default."""
        with mock.patch("builtins.print") as mp:
            cli.hr()
        mp.assert_called_once_with("─" * 72)

    def test_custom_char(self) -> None:
        """hr() respects a custom character."""
        with mock.patch("builtins.print") as mp:
            cli.hr("=")
        mp.assert_called_once_with("=" * 72)


class TestHeading(_CliTestBase):
    """Tests for heading()."""

    def test_prints_centered(self) -> None:
        """heading() prints centred text between rules."""
        with mock.patch("builtins.print") as mp:
            cli.heading("Title")
        # Should print: blank, rule, title, rule
        self.assertEqual(mp.call_count, 4)
        title_arg = mp.call_args_list[2][0][0]
        self.assertIn("Title", title_arg)


class TestCols(_CliTestBase):
    """Tests for cols()."""

    def test_empty_rows(self) -> None:
        """cols() prints '(empty)' for no data."""
        with mock.patch("builtins.print") as mp:
            cli.cols(["A", "B"], [])
        mp.assert_called_once_with("  (empty)")

    def test_with_data(self) -> None:
        """cols() prints header, separator, and data rows."""
        with mock.patch("builtins.print") as mp:
            cli.cols(
                ["Name", "Age"],
                [["Alice", "30"], ["Bob", "25"]],
            )
        # header + separator + 2 data rows = 4 calls
        self.assertEqual(mp.call_count, 4)

    def test_wide_cell(self) -> None:
        """Columns expand to fit data wider than header."""
        with mock.patch("builtins.print") as mp:
            cli.cols(["X"], [["LongValue"]])
        output = mp.call_args_list[2][0][0]  # data row
        self.assertIn("LongValue", output)


class TestAsk(_CliTestBase):
    """Tests for ask()."""

    def test_returns_input(self) -> None:
        """ask() returns the typed value."""
        with self._patch_input(["hello"]):
            result = cli.ask("Name")
        self.assertEqual(result, "hello")

    def test_default_on_empty(self) -> None:
        """ask() returns default when Enter is pressed."""
        with self._patch_input([""]):
            result = cli.ask("Name", "default")
        self.assertEqual(result, "default")

    def test_no_default(self) -> None:
        """ask() returns empty string with no default."""
        with self._patch_input([""]):
            result = cli.ask("Name")
        self.assertEqual(result, "")


class TestYesNo(_CliTestBase):
    """Tests for yes_no()."""

    def test_yes(self) -> None:
        """'y' returns True."""
        with self._patch_input(["y"]):
            self.assertTrue(cli.yes_no("Ok?"))

    def test_yes_full(self) -> None:
        """'yes' returns True."""
        with self._patch_input(["yes"]):
            self.assertTrue(cli.yes_no("Ok?"))

    def test_no(self) -> None:
        """'n' returns False."""
        with self._patch_input(["n"]):
            self.assertFalse(cli.yes_no("Ok?"))

    def test_other(self) -> None:
        """Anything else returns False."""
        with self._patch_input(["maybe"]):
            self.assertFalse(cli.yes_no("Ok?"))


class TestPick(_CliTestBase):
    """Tests for pick()."""

    def test_empty_items(self) -> None:
        """pick() returns None for empty list."""
        result = cli.pick([])
        self.assertIsNone(result)

    def test_valid_pick(self) -> None:
        """pick() returns the selected ID."""
        with self._patch_input(["2"]):
            result = cli.pick([("A", "a1"), ("B", "b2")])
        self.assertEqual(result, "b2")

    def test_out_of_range_high(self) -> None:
        """pick() returns None for index > length."""
        with self._patch_input(["99"]):
            result = cli.pick([("A", "a1")])
        self.assertIsNone(result)

    def test_out_of_range_zero(self) -> None:
        """pick() returns None for index 0."""
        with self._patch_input(["0"]):
            result = cli.pick([("A", "a1")])
        self.assertIsNone(result)

    def test_non_numeric(self) -> None:
        """pick() returns None for non-numeric input."""
        with self._patch_input(["abc"]):
            result = cli.pick([("A", "a1")])
        self.assertIsNone(result)


# ================================================================
# Status
# ================================================================
class TestStatus(_CliTestBase):
    """Tests for status()."""

    def test_prints_summary(self) -> None:
        """status() prints counts for all entities."""
        with mock.patch("builtins.print") as mp:
            cli.status(self.hm, self.cm, self.rm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("Hotels: 1", output)
        self.assertIn("Customers: 1", output)
        self.assertIn("Reservations: 0", output)


# ================================================================
# Hotel commands
# ================================================================
class TestHotelList(_CliTestBase):
    """Tests for hotel_list()."""

    def test_shows_hotels(self) -> None:
        """hotel_list() outputs a table with hotel data."""
        with mock.patch("builtins.print") as mp:
            cli.hotel_list(self.hm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("Inn", output)

    def test_empty_list(self) -> None:
        """hotel_list() shows (empty) when no hotels."""
        self.hm.delete_hotel(self.hotel.hotel_id)
        with mock.patch("builtins.print") as mp:
            cli.hotel_list(self.hm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("(empty)", output)


class TestHotelAdd(_CliTestBase):
    """Tests for hotel_add()."""

    def test_success(self) -> None:
        """hotel_add() creates a hotel."""
        with self._patch_input(["New", "Addr", "5"]):
            cli.hotel_add(self.hm)
        self.assertEqual(len(self.hm.list_hotels()), 2)

    def test_empty_name_cancels(self) -> None:
        """hotel_add() cancels on empty name."""
        with self._patch_input([""]):
            cli.hotel_add(self.hm)
        self.assertEqual(len(self.hm.list_hotels()), 1)

    def test_bad_rooms(self) -> None:
        """hotel_add() handles non-integer rooms."""
        with self._patch_input(["X", "Y", "abc"]):
            cli.hotel_add(self.hm)
        self.assertEqual(len(self.hm.list_hotels()), 1)


class TestHotelEdit(_CliTestBase):
    """Tests for hotel_edit()."""

    def test_success(self) -> None:
        """hotel_edit() modifies hotel attributes."""
        with self._patch_input(["1", "Renamed", "", ""]):
            cli.hotel_edit(self.hm)
        self.assertEqual(
            self.hm.list_hotels()[0].name, "Renamed",
        )

    def test_cancel_pick(self) -> None:
        """hotel_edit() cancels when pick returns None."""
        with self._patch_input(["0"]):
            cli.hotel_edit(self.hm)
        self.assertEqual(
            self.hm.list_hotels()[0].name, "Inn",
        )

    def test_validation_failure(self) -> None:
        """hotel_edit() reports validation errors."""
        with self._patch_input(["1", "", "", "0"]):
            cli.hotel_edit(self.hm)
        # Rooms = 0 fails validation, name stays.
        self.assertEqual(
            self.hm.list_hotels()[0].name, "Inn",
        )

    def test_bad_rooms_type(self) -> None:
        """hotel_edit() handles non-integer rooms."""
        with self._patch_input(["1", "", "", "abc"]):
            cli.hotel_edit(self.hm)
        self.assertEqual(
            self.hm.list_hotels()[0].name, "Inn",
        )

    def test_get_returns_none(self) -> None:
        """hotel_edit() exits when get_hotel returns None."""
        with self._patch_input(["1"]):
            with mock.patch.object(
                self.hm, "get_hotel", return_value=None,
            ):
                cli.hotel_edit(self.hm)


class TestHotelDelete(_CliTestBase):
    """Tests for hotel_delete()."""

    def test_confirm_yes(self) -> None:
        """hotel_delete() deletes when confirmed."""
        with self._patch_input(["1", "y"]):
            cli.hotel_delete(self.hm)
        self.assertEqual(len(self.hm.list_hotels()), 0)

    def test_confirm_no(self) -> None:
        """hotel_delete() keeps hotel when declined."""
        with self._patch_input(["1", "n"]):
            cli.hotel_delete(self.hm)
        self.assertEqual(len(self.hm.list_hotels()), 1)

    def test_cancel_pick(self) -> None:
        """hotel_delete() cancels on bad pick."""
        with self._patch_input(["0"]):
            cli.hotel_delete(self.hm)
        self.assertEqual(len(self.hm.list_hotels()), 1)

    def test_delete_fails(self) -> None:
        """hotel_delete() reports failure from manager."""
        with self._patch_input(["1", "y"]):
            with mock.patch.object(
                self.hm, "delete_hotel", return_value=False,
            ):
                cli.hotel_delete(self.hm)
        # Hotel still present (mock prevented real delete).
        self.assertEqual(len(self.hm.list_hotels()), 1)


# ================================================================
# Customer commands
# ================================================================
class TestCustList(_CliTestBase):
    """Tests for cust_list()."""

    def test_shows_customers(self) -> None:
        """cust_list() outputs a table with data."""
        with mock.patch("builtins.print") as mp:
            cli.cust_list(self.cm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("Alice", output)


class TestCustAdd(_CliTestBase):
    """Tests for cust_add()."""

    def test_success(self) -> None:
        """cust_add() creates a customer."""
        with self._patch_input(["Bob", "bob@x.com"]):
            cli.cust_add(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 2)

    def test_empty_name_cancels(self) -> None:
        """cust_add() cancels on empty name."""
        with self._patch_input([""]):
            cli.cust_add(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 1)

    def test_bad_email(self) -> None:
        """cust_add() handles invalid email."""
        with self._patch_input(["Bad", "no-at"]):
            cli.cust_add(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 1)


class TestCustEdit(_CliTestBase):
    """Tests for cust_edit()."""

    def test_success(self) -> None:
        """cust_edit() modifies customer attributes."""
        with self._patch_input(
            ["1", "Alice2", ""]
        ):
            cli.cust_edit(self.cm)
        self.assertEqual(
            self.cm.list_customers()[0].name, "Alice2",
        )

    def test_cancel_pick(self) -> None:
        """cust_edit() cancels when pick returns None."""
        with self._patch_input(["0"]):
            cli.cust_edit(self.cm)
        self.assertEqual(
            self.cm.list_customers()[0].name, "Alice",
        )

    def test_validation_failure(self) -> None:
        """cust_edit() reports validation errors."""
        with self._patch_input(["1", "", "bad"]):
            cli.cust_edit(self.cm)
        # Email "bad" fails, original kept.
        self.assertEqual(
            self.cm.list_customers()[0].email, "a@b.com",
        )

    def test_bad_email_type(self) -> None:
        """cust_edit() handles type errors gracefully."""
        with self._patch_input(["1", "", "no-at"]):
            cli.cust_edit(self.cm)
        self.assertEqual(
            self.cm.list_customers()[0].email, "a@b.com",
        )

    def test_get_returns_none(self) -> None:
        """cust_edit() exits when get_customer returns None."""
        with self._patch_input(["1"]):
            with mock.patch.object(
                self.cm, "get_customer",
                return_value=None,
            ):
                cli.cust_edit(self.cm)

    def test_type_error(self) -> None:
        """cust_edit() catches TypeError from manager."""
        with self._patch_input(["1", "", ""]):
            with mock.patch.object(
                self.cm, "modify_customer",
                side_effect=TypeError("boom"),
            ):
                cli.cust_edit(self.cm)


class TestCustDelete(_CliTestBase):
    """Tests for cust_delete()."""

    def test_confirm_yes(self) -> None:
        """cust_delete() deletes when confirmed."""
        with self._patch_input(["1", "y"]):
            cli.cust_delete(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 0)

    def test_confirm_no(self) -> None:
        """cust_delete() keeps customer when declined."""
        with self._patch_input(["1", "n"]):
            cli.cust_delete(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 1)

    def test_cancel_pick(self) -> None:
        """cust_delete() cancels on bad pick."""
        with self._patch_input(["0"]):
            cli.cust_delete(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 1)

    def test_delete_fails(self) -> None:
        """cust_delete() reports failure from manager."""
        with self._patch_input(["1", "y"]):
            with mock.patch.object(
                self.cm, "delete_customer",
                return_value=False,
            ):
                cli.cust_delete(self.cm)
        self.assertEqual(len(self.cm.list_customers()), 1)


# ================================================================
# Reservation commands
# ================================================================
class TestResList(_CliTestBase):
    """Tests for res_list()."""

    def test_shows_resolved_names(self) -> None:
        """res_list() resolves customer and hotel names."""
        self.rm.create_reservation(
            self.cust.customer_id,
            self.hotel.hotel_id,
            "2026-06-01", "2026-06-05",
        )
        with mock.patch("builtins.print") as mp:
            cli.res_list(self.hm, self.cm, self.rm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("Alice", output)
        self.assertIn("Inn", output)

    def test_fallback_ids(self) -> None:
        """res_list() shows raw IDs for missing entities."""
        # Create reservation then simulate missing entities.
        res = self.rm.create_reservation(
            self.cust.customer_id,
            self.hotel.hotel_id,
            "2026-06-01", "2026-06-05",
        )
        self.assertIsNotNone(res)
        with (
            mock.patch.object(
                self.hm, "get_hotel", return_value=None,
            ),
            mock.patch.object(
                self.cm, "get_customer",
                return_value=None,
            ),
            mock.patch("builtins.print") as mp,
        ):
            cli.res_list(self.hm, self.cm, self.rm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn(self.cust.customer_id, output)
        self.assertIn(self.hotel.hotel_id, output)

    def test_empty_list(self) -> None:
        """res_list() shows (empty) when no reservations."""
        with mock.patch("builtins.print") as mp:
            cli.res_list(self.hm, self.cm, self.rm)
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("(empty)", output)


class TestResNew(_CliTestBase):
    """Tests for res_new()."""

    def test_success(self) -> None:
        """res_new() creates a reservation."""
        with self._patch_input(
            ["1", "1", "2026-07-01", "2026-07-05"],
        ):
            cli.res_new(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 1,
        )

    def test_no_customers(self) -> None:
        """res_new() exits early with no customers."""
        with mock.patch.object(
            self.cm, "list_customers", return_value=[],
        ):
            cli.res_new(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )

    def test_no_hotels(self) -> None:
        """res_new() exits early with no hotels."""
        with mock.patch.object(
            self.hm, "list_hotels", return_value=[],
        ):
            cli.res_new(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )

    def test_cancel_customer_pick(self) -> None:
        """res_new() cancels when customer pick fails."""
        with self._patch_input(["0"]):
            cli.res_new(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )

    def test_cancel_hotel_pick(self) -> None:
        """res_new() cancels when hotel pick fails."""
        with self._patch_input(["1", "0"]):
            cli.res_new(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )

    def test_bad_dates(self) -> None:
        """res_new() handles invalid dates gracefully."""
        with self._patch_input(
            ["1", "1", "bad", "worse"],
        ):
            cli.res_new(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )


class TestResCancel(_CliTestBase):
    """Tests for res_cancel()."""

    def setUp(self) -> None:
        super().setUp()
        self.res = self.rm.create_reservation(
            self.cust.customer_id,
            self.hotel.hotel_id,
            "2026-08-01", "2026-08-05",
        )

    def test_confirm_yes(self) -> None:
        """res_cancel() cancels when confirmed."""
        with self._patch_input(["1", "y"]):
            cli.res_cancel(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )

    def test_confirm_no(self) -> None:
        """res_cancel() keeps reservation when declined."""
        with self._patch_input(["1", "n"]):
            cli.res_cancel(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 1,
        )

    def test_cancel_pick(self) -> None:
        """res_cancel() cancels on bad pick."""
        with self._patch_input(["0"]):
            cli.res_cancel(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 1,
        )

    def test_fallback_labels(self) -> None:
        """res_cancel() uses raw IDs for missing entities."""
        with (
            mock.patch.object(
                self.hm, "get_hotel", return_value=None,
            ),
            mock.patch.object(
                self.cm, "get_customer",
                return_value=None,
            ),
            self._patch_input(["1", "y"]),
        ):
            cli.res_cancel(self.hm, self.cm, self.rm)
        self.assertEqual(
            len(self.rm.list_reservations()), 0,
        )

    def test_cancel_fails(self) -> None:
        """res_cancel() reports failure from manager."""
        with self._patch_input(["1", "y"]):
            with mock.patch.object(
                self.rm, "cancel_reservation",
                return_value=False,
            ):
                cli.res_cancel(
                    self.hm, self.cm, self.rm,
                )
        self.assertEqual(
            len(self.rm.list_reservations()), 1,
        )


# ================================================================
# Help
# ================================================================
class TestShowHelp(_CliTestBase):
    """Tests for show_help()."""

    def test_prints_help(self) -> None:
        """show_help() prints the HELP string."""
        with mock.patch("builtins.print") as mp:
            cli.show_help()
        output = " ".join(
            str(c) for c in mp.call_args_list
        )
        self.assertIn("HOTELS", output)
        self.assertIn("CUSTOMERS", output)


# ================================================================
# Dispatch
# ================================================================
class TestDispatch(_CliTestBase):
    """Tests for dispatch()."""

    def test_quit_q(self) -> None:
        """dispatch('q') returns False."""
        self.assertFalse(cli.dispatch("q", self.mgrs))

    def test_quit_quit(self) -> None:
        """dispatch('quit') returns False."""
        self.assertFalse(
            cli.dispatch("quit", self.mgrs),
        )

    def test_quit_exit(self) -> None:
        """dispatch('exit') returns False."""
        self.assertFalse(
            cli.dispatch("exit", self.mgrs),
        )

    def test_help_question(self) -> None:
        """dispatch('?') shows help and returns True."""
        self.assertTrue(cli.dispatch("?", self.mgrs))

    def test_help_word(self) -> None:
        """dispatch('help') shows help and returns True."""
        self.assertTrue(
            cli.dispatch("help", self.mgrs),
        )

    def test_status(self) -> None:
        """dispatch('s') shows status and returns True."""
        self.assertTrue(cli.dispatch("s", self.mgrs))

    def test_status_word(self) -> None:
        """dispatch('status') shows status."""
        self.assertTrue(
            cli.dispatch("status", self.mgrs),
        )

    def test_unknown_command(self) -> None:
        """dispatch() prints error for unknown command."""
        with mock.patch("builtins.print") as mp:
            result = cli.dispatch("zzz", self.mgrs)
        self.assertTrue(result)
        output = mp.call_args[0][0]
        self.assertIn("Unknown command", output)

    def test_hotel_list_command(self) -> None:
        """dispatch('h') calls hotel_list."""
        result = cli.dispatch("h", self.mgrs)
        self.assertTrue(result)

    def test_case_insensitive(self) -> None:
        """dispatch() is case-insensitive."""
        self.assertFalse(cli.dispatch("Q", self.mgrs))

    def test_strips_whitespace(self) -> None:
        """dispatch() strips leading/trailing spaces."""
        self.assertFalse(
            cli.dispatch("  q  ", self.mgrs),
        )

    def test_routes_all_commands(self) -> None:
        """Every COMMANDS entry dispatches without error."""
        for cmd in cli.COMMANDS:
            with self._patch_input(["0"] * 10):
                try:
                    result = cli.dispatch(cmd, self.mgrs)
                except StopIteration:
                    result = True
                self.assertTrue(result)


# ================================================================
# Main loop
# ================================================================
class TestMain(_CliTestBase):
    """Tests for main()."""

    @mock.patch.object(cli, "DATA_DIR")
    @mock.patch("os.system")
    def test_quit_command(
        self, mock_sys: mock.MagicMock,
        mock_dir: str,
    ) -> None:
        """main() exits on 'q'."""
        with tempfile.TemporaryDirectory() as td:
            mock_dir.__str__ = lambda _: td  # noqa: ARG005
            with mock.patch.object(cli, "DATA_DIR", td):
                with self._patch_input(["q"]):
                    cli.main()
        mock_sys.assert_called_once()

    @mock.patch("os.system")
    def test_eof_exits(
        self, _mock_sys: mock.MagicMock,
    ) -> None:
        """main() exits gracefully on EOFError."""
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(cli, "DATA_DIR", td):
                with mock.patch(
                    "builtins.input",
                    side_effect=EOFError,
                ):
                    cli.main()

    @mock.patch("os.system")
    def test_keyboard_interrupt_exits(
        self, _mock_sys: mock.MagicMock,
    ) -> None:
        """main() exits gracefully on KeyboardInterrupt."""
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(cli, "DATA_DIR", td):
                with mock.patch(
                    "builtins.input",
                    side_effect=KeyboardInterrupt,
                ):
                    cli.main()

    @mock.patch("os.system")
    def test_empty_input_skipped(
        self, _mock_sys: mock.MagicMock,
    ) -> None:
        """main() skips empty input lines."""
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(cli, "DATA_DIR", td):
                with self._patch_input(["", "", "q"]):
                    cli.main()


if __name__ == "__main__":
    unittest.main()
