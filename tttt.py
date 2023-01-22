import re
import signal
import sys


class Draw:
    """ simple wrapper around possible draws """
    Empty = " "
    X = "X"
    O = "O"


class TicTacToe:
    """ Primary Interface for the TicTacToe Game

    Notes:
        To draw we have to use coordinates starting at (0, 0):
            |(0, 0)|(0, 1)|(0, 2)|
            |(1, 0)|(1, 1)|(1, 3)|
            |(2, 0)|(2, 1)|(2, 2)|
            |...   |...   |...   |

        Size of dimensions can be chosen. The board will always be nXn.
        To have a winner X or O have to exist exactly n-times in one row or column.
    """

    def __init__(self, n_dimensions=3):
        """ Set up the TicTagToe board

        Args:
            n_dimensions: number of rows and columns
        """
        if n_dimensions < 3:
            raise ValueError("Board size must be at least 3x3. Pick a higher number.")

        self._n_dimensions = n_dimensions
        self._number_of_cells = n_dimensions * n_dimensions

        # identifier if the game is still running
        self._finished = False

        # track last draw
        self._last_draw = Draw.Empty

        # Fill our initial grid with the proper number of cells and empty entries
        # A key represents the cell coordinate and the value the entry
        # Keys are ordered by default
        self._grid = {}
        for x in range(n_dimensions):
            for y in range(n_dimensions):
                self._grid[x, y] = Draw.Empty

    def __repr__(self):
        return self.render()

    def __str__(self):
        return self.render()

    def render(self, show_coordinates=False):
        """ generate a string representation of the current board

        Keyword Args:
            show_coordinates (bool): If True it will present the cell coordinates
        Returns:
            str: the board with all its set entries
        """
        representation = ""
        row_number = 0
        row_repr = "       "  # give the board render some indentation
        for (x, y), value in self._grid.items():
            # identify when we reached a new row or start the last row
            is_last = self._is_last_cell(x, y)
            # allow to show the coordinates in the cells
            if show_coordinates:
                value = f"({x}, {y})"

            if row_number != x or is_last:
                representation += "{}|{}\n".format(row_repr, f"{value}|" if is_last else "")
                row_repr = f"       |{value}"
                row_number = x
            else:
                row_repr += f"|{value}"

        return f"\n\n{representation}\n\n"

    def _is_last_cell(self, x, y):
        """ helper to identify if the given coordinate is the last possible cell

        Args:
            x (int): x coordinate value
            y (int): y coordinate value
        Returns:
            bool: True if given coordinate represents last cell
        """
        return (x + 1) * (y + 1) == self._number_of_cells

    @property
    def finished(self):
        """ Return the finished state """
        return self._finished or \
               len([_ for _ in self._grid.values() if _ != Draw.Empty]) == self._number_of_cells

    @property
    def current_drawer(self):
        """ Who's draw is it...

        Returns:
            str: Draw.X or Draw.O
        """
        if self._last_draw == Draw.Empty or self._last_draw == Draw.O:
            return Draw.X
        else:
            return Draw.O

    def _show_winner(self, winner, how):
        """ Report the game winner and how game was won """
        self._finished = True
        print(f"Congratulations '{winner}' wins {how}!\n")

    def draw(self, entry, coordinate):
        """ Let the user make a draw and present the updated board

        Only when required this checks for a winner and ends the game.

        Args:
            entry (Entry.X or Entry.O): The players entry
            coordinate (tuple): The coordinate the entry will be placed

        Returns:
            bool: True if draw produced a winner, False if not

        """
        if self.finished:
            raise RuntimeError("Game ended. No draw possible anymore. Please start a new game.")

        if self._last_draw == entry:
            raise ValueError(f"{entry} not allowed to do the draw yet")

        redo_message = "Please redo your draw!"
        # check if coordinate exceeds grid cell
        if coordinate not in self._grid.keys():
            raise ValueError(
                f"Given coordinate {coordinate} doesn't exist in the dimensions "
                f"of {self._n_dimensions}x{self._n_dimensions}. Coordinate indices start at 0.\n" +
                redo_message
            )
        # check if cell is empty
        if self._grid[coordinate] != Draw.Empty:
            raise ValueError(f"Cell at given coordinage {coordinate} is not empty.\n" + redo_message)

        self._grid[coordinate] = entry
        self._last_draw = entry
        # immediately represent the updated board
        print(f"'{entry}' did the last draw at {coordinate}.")
        print(self)
        # only check for a winner if we did receive enough entries
        if len([_ for _ in self._grid.values() if _ != Draw.Empty]) >= (self._n_dimensions * 2) - 1:
            wins = self._does_win(entry)
            if wins[0]:
                self._show_winner(entry, "horizontally")
            if wins[1]:
                self._show_winner(entry, "vertically")
            if wins[2]:
                self._show_winner(entry, "diagonal descending")
            if wins[3]:
                self._show_winner(entry, "diagonal ascending")

            return any(wins)

        return False

    def _does_win(self, entry_type):
        """ identify if we have horizontal or vertical or diagonal completeness for given entry

        Args:
            entry_type (Entry.X or Entry.O):

        Returns:
            tuple: horizontal_win, vertical_win,

        """

        #### closures ####

        # base algorithm to check for straight axis completeness
        def _straight_check(grid_items):
            entries = []
            for coordinate, value in grid_items:
                if len(entries) <= self._n_dimensions:
                    entries.append(value)
                    if len(entries) == self._n_dimensions:
                        if all(_ == entry_type for _ in entries):
                            return True
                        else:
                            entries = []

        # base algorithm to check for diagonal axis completeness
        def _diagonal_check(values, step_size, offset):
            entries = []
            for i in range(offset, len(self._grid.values()), step_size):
                if len(entries) == self._n_dimensions:
                    break

                entries.append(values[i])

            return all([_ == entry_type for _ in entries])

        ###################

        # Items sorted by rows...
        horizontal_win = _straight_check(self._grid.items())
        # Items sorted by columns...
        vertical_win = _straight_check(sorted(self._grid.items(), key=lambda item: item[0][1]))

        # Go from zero-coordinate forwards check every other n+1 step
        diagonal_descending_win = _diagonal_check(list(self._grid.values()), self._n_dimensions + 1, 0)

        # Go from last-coordinate-(n-1) backwards and check every (n-1) step
        values = list(self._grid.values())
        values.reverse()
        diagonal_ascending_win = _diagonal_check(values, self._n_dimensions - 1, self._n_dimensions - 1)

        return horizontal_win, vertical_win, diagonal_descending_win, diagonal_ascending_win


def main():
    """ The main program to run """

    print("Welcome to TTTT (Terminal-Tic-Tac-Toe).\n\nTo abort the game press Ctrl+C.\n")
    # let gracefully abort the game.
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

    # TODO: proper value checking
    n_dimensions = int(
        input("This version isn't limited to 3x3.\nPlease define your board dimensions (int [default: 3]): ") or 3
    )
    game = TicTacToe(n_dimensions=n_dimensions)

    print("The board is set up :). Please use the coordinates as shown.")
    print(game.render(show_coordinates=True))

    won = False
    while not game.finished:
        drawer = game.current_drawer
        # TODO: proper value checking
        player_input = tuple(
            int(_) for _ in re.findall(r"\d+", input(f"Player '{drawer}' do your draw (x,y coordinate): "))
        )
        try:
            won = game.draw(drawer, player_input)
        except (ValueError, RuntimeError) as e:
            print(e)

        if won:
            sys.exit(0)

        if game.finished:
            print("You both did a too good job. This game has no winner...")


if __name__ == '__main__':
    main()
