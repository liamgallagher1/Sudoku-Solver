# Project Euler, problem 96
# Sudoku solver
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.text as text
import matplotlib.animation as animation



problems = open('CPC.txt', 'r')


class Board:
    """
    The board represents a potentially unsolved Sudoku problem.
    It consists of a 9x9 grid of cells that may or may not be filled in with a
    number. It also groups cells into 27 groups of 9 corresponding to the
    to 1x9 rows and columns and 3x3 squares.
    """
    def __init__(self, grid, ax = None, writer = None):
        self.grid = [[Cell(self) for x in range(0, 9)] for y in range(0, 9)]
        # all 27 groups
        self.groups = []
        # the 9 specific groups
        self.rows = [None] * 9
        self.cols = [None] * 9
        self.squares = [None] * 9
        self.updated = False
        self.ax = ax
        self.writer = writer
        self.artists = []
        if ax is None:
            fig, ax = plt.subplots()
            self.ax = ax
            self.fig = fig
            plt.axis([0, 9, 0, 9])
            plt.grid(True)
            plt.draw()
            FFMpegWriter = animation.writers['ffmpeg']
            metadata = dict(title='Movie Test', artist='Matplotlib',
                            comment='Movie support!')
            self.writer = FFMpegWriter(fps=15, metadata=metadata)
            self.writer.setup(self.fig, "bigger_sudoku_solver.mp4", 600)

        # build the groups
        for i in range(0, 9):
            self.rows[i] = Line([self.get_cell(j, i) for j in range(0, 9)], self)
            self.cols[i] = Line([self.get_cell(i, j) for j in range(0, 9)], self)
            self.squares[i] = Line([], self)
        for y in range(0, 9):
            y_div, y_mod = divmod(y, 3)
            for x in range(0, 9):
                x_div, x_mod = divmod(x, 3)
                self.squares[y_div * 3 + x_div].cells.append(self.get_cell(x, y))
        for x in range(0, 9):
            for y in range(0, 9):
                self.get_cell(x, y).set_group(self.rows[y], self.cols[x], self.squares[(y / 3) * 3 + x / 3])
        for x in range(0, 9):
            for y in range(0, 9):
                self.get_cell(x, y).assign(grid[y][x])
        self.groups.extend(self.rows)
        self.groups.extend(self.cols)
        self.groups.extend(self.squares)

    def get_cell(self, x, y):
        """ Returns the cell at coordinate x, y """
        return self.grid[y][x]

    def solve(self):
        """
        Returns the solved 2d grid if it is able to be solved.
        Returns None if it can't solve the board, i.e. there is an inconsistency.
        """
        solved = self.solved()
        if solved == 81:
            return self.get_grid()
        if not self.update():  # Attempts to fill in some cells
            return None
        if self.solved() != solved:  # Recurse while updates are being made
            return self.solve()
        else:  # No updates can be made using just this simple logic.
            # Pick a cell to take a guess on
            ((x, y), possibilities) = self.find_best_cell_to_guess()
            # Cache the current board state in case we guess wrong
            grid = self.get_grid()
            for pos in possibilities:
                # Copy the board state, guess, and try to solve
                new_board = Board(grid, self.ax, self.writer)
                self.writer.grab_frame()
                valid = new_board.get_cell(x, y).assign(pos)
                if not valid:
                    continue  # We guessed wrong
                possible_to_solve = new_board.solve()
                if possible_to_solve is not None:  # Good guess, it was solved
                    #for artist in self.artists:
                    #    artist.remove()
                    plt.cla()
                    self.fig.canvas.draw()
                    for x in range(0, 9):
                        for y in range (0, 9):
                            self.get_cell(x, y).assign(possible_to_solve[y][x])
                    return possible_to_solve
            return None

    def update(self):
        """
        Updates self by finding any rows, columns or squares where there is
        only one number that's not filled in, and setting the remaining cell.
        Returns false if there is an inconsistency in the board.
        """
        for line in self.groups:
            if not line.update():
                return False
        return True

    def to_string(self):
        line = "|-----------|\n"
        s = line
        for i in range(0, 9):
            new_line = "|"
            for j in range(0, 9):
                new_line += str(self.get_cell(j, i).get_val())
                if j % 3 == 2:
                    new_line += "|"
            s += new_line + "\n"
            if i % 3 == 2:
                s += line
        return s

    def solved(self):
        """ Returns the number of cells (0 - 81) that have been filled in """
        num_filled = 0
        for y in range(0, 9):
            for x in range(0, 9):
                if not self.get_cell(x, y).val == 0: num_filled += 1
        return num_filled

    def find_best_cell_to_guess(self):
        """ Finds a cell that has only 2 possibilities, or otherwise the
        minimum number of possibilities of any unfilled cell on the board. Returns
        the coordinates of the cell (x, y), and the list of its possibilities
        """
        min_cell = Cell(self)
        (cell_x, cell_y) = (9, 9)
        for x in range(0, 9):
            for y in range(0, 9):
                cell = self.get_cell(x, y)
                if not cell.count == 0 and cell.count < min_cell.count:
                    if cell.count == 2:
                        return (x, y), cell.get_pos()
                    else:
                        min_cell = cell
                        cell_x, cell_y = x, y
        return (cell_x, cell_y), cell.get_pos()

    def draw_cell(self, cell):
        for x in range(0, 9):
            for y in range(0, 9):
                other_cell = self.get_cell(x, y);
                if other_cell == cell:
                    my_text = text.Text(x + 0.5, y + 0.5, str(cell.val), ha= "center")
                    self.ax.add_artist(my_text)
                    self.artists.append(my_text)
                    plt.draw()
                    print "Filled cell " + str(self.solved())
                    self.writer.grab_frame()

    def set_board(self, grid):
        for x in range(0, 9):
            for y in range(0, 9):
                self.get_cell(x, y).assign(grid[y][x])

    def get_grid(self):
        """ Returns a 2d array of the cells values """
        grid = [None] * 9
        for y in range(0, 9):
            grid[y] = [None] * 9
            for x in range(0, 9):
                grid[y][x] = self.get_cell(x, y).val

        return grid


class Line:
    """ A Line is a set of nine cells, representing a row, column, or 3x3 square.
    It tracks the numbers that it has filled in. If only one number remains, that
    cell can be filled. """
    def __init__(self, cells, board):
        self.cells = cells
        self.has = [False] * 9
        self.board = board

    def update(self):
        """
        If the line has a number that hasn't been filled in, and only one cell
        could possibly be this, then it sets it. Returns False if there is an
        inconsistency. """
        for i in range(1, 10):
            if not self.has[i - 1]:
                count = 0  # Number of cells that can be i
                j = 0
                cell_to_update = None
                while count < 2 and j < 9:
                    cell = self.cells[j]
                    if cell.can_be[i - 1]:
                        count += 1
                        cell_to_update = cell
                    j += 1
                if count == 0:  # Only possible if there is an inconsistency.
                    return False
                if count == 1:  # Set the cell and see how it goes
                    if not cell_to_update.assign(i):
                        return False
                    self.board.updated = True
        return True

    def cant_be(self, i):
        """ Sets all cells in the line to not be able to be i. """
        self.has[i - 1] = True
        for cell in self.cells:
            cell.cant_be(i)

    def check_possibilities(self):
        """ Sets any cells that have only one possibility. Returns false if
         there is an inconsistency. """
        for cell in self.cells:
            if not cell.check_possibilities():
                return False
        return True

    def to_string(self):
        s = "["
        for cell in self.cells:
            s += str(cell.val) + ", "
        s += "] "
        return s


class Cell:
    """
    A cell is a single box on the board. It can be any integer between 1 - 9.
    If its value is not assigned, its set to be zero.
    It keeps track of all the numbers it can potentially be. It can't be number
    if another cell in the same group is assigned that number. When it can only
    be one possible number, it can be set to that. If it doesn't have a value
    and can't be any number, then there's an inconsistency in the board and you
    need to fix the mistake.
    """
    def __init__(self, board):
        self.board = board
        self.val = 0
        self.can_be = [True] * 9
        self.groups = []
        self.count = 9

    def get_val(self):
        """ Returns the number at the cell. Its 0 if it was never set. """
        return self.val

    def can_be(self, i):
        """ Could the value of this cell legally be i? """
        return self.can_be[i - 1]

    def get_pos(self):
        """ Returns the list of possible values this cell could take on. """
        pos = []
        for i in range(0, 9):
            if self.can_be[i]: pos.append(i + 1)
        return pos

    def set_group(self, row, col, square):
        """ Sets this cell's group pointers """
        self.groups.append(row)
        self.groups.append(col)
        self.groups.append(square)

    def assign(self, i):
        """ Assigns the cell to be the number i. Updates all cells in the group
        such that they can't be i, and assigns them if they can only be one value.
        Returns false if it leads to an inconsistency,
        i.e., Something is wrong on the board, so setting this cell to i leads to
        a cell not being able to be anything """
        if self.val == 0 and not i == 0:
            self.val = i
            self.board.draw_cell(self)
            for line in self.groups:
                line.cant_be(i)
            for line in self.groups:
                if not line.check_possibilities():
                    print "False on this cell: " + self.val
                    for line in self.groups:
                        print line.to_string()
                    return False
            self.count = 0
            self.can_be = [False] * 9
        #elif not i == 0:
        #self.board.draw_cell(self)
        return True

    def cant_be(self, i):
        """ If this cell wasn't set, it assigns it to not be able to be this
        value """
        if self.val == 0:
            if self.can_be[i - 1]:
                self.count -= 1
                self.can_be[i - 1] = False

    def check_possibilities(self):
        """ If only one possible value remains, it sets the cell to that value.
        Returns false if this creates an inconsistency. """
        if self.count == 1:
            for j in range(0, 9):
                if self.can_be[j]:
                    if not self.assign(j + 1):
                        return False
        return True

    def to_string(self):
        s = str(self.val) + ", ["
        for i in self.can_be:
            s += str(i) + ", "
        s += ("] " + str(self.count))
        return s

boards = [None] * 50
summed = 0  # The answer to the euler problem
start = time.time()
for b in range(0, 1):
    problems.readline()
    new_board = [[None]] * 9
    for y_cord in range(0, 9):
        temp_chars = list(problems.readline())[0:9]
        new_board[y_cord] = [None] * 9
        for x_cord in range(0, 9):
            new_board[y_cord][x_cord] = int(temp_chars[x_cord])
    print "Board #" + str(b + 1)
    # Board can be solved on construction through cells having only one possibility
    boards[b] = Board(new_board)
    print boards[b].to_string()
    solved_grid = boards[b].solve()
    if solved_grid is None:
        print "Board could not be solved" # never happens
        break
    solved = boards[b]
    summed += solved.get_cell(0, 0).val * 100 + solved.get_cell(1, 0).val * 10 + solved.get_cell(2, 0).val
    print "Solution:"
    print solved.to_string()
    plt.show()

end = time.time()

print "Project Euler solution: " + str(summed)
print "Time to solve: " + str(end - start)
