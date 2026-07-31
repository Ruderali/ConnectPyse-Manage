from typing import List, Optional

from ..models.board import Board
from ..models.board_status import BoardStatus
from ..models.board_type import BoardType
from ..models.board_subtype import BoardSubtype
from ..models.board_item import BoardItem


class BoardsMixin:
    """Service board-related API methods."""

    def get_boards(self, active_only: bool = True, run_as: Optional[str] = None) -> List[Board]:
        """
        Get all service boards.

        Args:
            active_only: If True, only return active (non-inactive) boards
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Board]: List of boards
        """
        conditions = "inactive=false" if active_only else ""
        results = self.get_all("service/boards", conditions=conditions, run_as=run_as)
        return [Board.from_dict(r) for r in results]

    def get_board_count(self, conditions: str = "", run_as: Optional[str] = None) -> int:
        """
        Return the total number of service boards matching the given conditions
        without fetching any board data.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            int: Total board count, or None if the endpoint was not found
        """
        return self.get_count("service/boards", conditions=conditions, run_as=run_as)

    def get_board_statuses(self, board_id: int, run_as: Optional[str] = None) -> List[BoardStatus]:
        """
        Get all statuses for a specific board.

        Args:
            board_id: Board ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[BoardStatus]: List of board statuses
        """
        results = self.get_all(f"service/boards/{board_id}/statuses", run_as=run_as)
        return [BoardStatus.from_dict(r) for r in results]

    def get_board_types(self, board_id: int, run_as: Optional[str] = None) -> List[BoardType]:
        """
        Get all types for a specific board.

        Args:
            board_id: Board ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[BoardType]: List of board types
        """
        results = self.get_all(f"service/boards/{board_id}/types", run_as=run_as)
        return [BoardType.from_dict(r) for r in results]

    def get_board_subtypes(self, board_id: int, run_as: Optional[str] = None) -> List[BoardSubtype]:
        """
        Get all subtypes for a specific board.

        Args:
            board_id: Board ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[BoardSubtype]: List of board subtypes
        """
        results = self.get_all(f"service/boards/{board_id}/subtypes", run_as=run_as)
        return [BoardSubtype.from_dict(r) for r in results]

    def get_board_items(self, board_id: int, run_as: Optional[str] = None) -> List[BoardItem]:
        """
        Get all items for a specific board.

        Args:
            board_id: Board ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[BoardItem]: List of board items
        """
        results = self.get_all(f"service/boards/{board_id}/items", run_as=run_as)
        return [BoardItem.from_dict(r) for r in results]
