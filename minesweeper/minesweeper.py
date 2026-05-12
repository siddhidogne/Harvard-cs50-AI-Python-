import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):


        self.height = height
        self.width = width
        self.mines = set()


        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)


        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True


        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """


        count = 0


        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):


                if (i, j) == cell:
                    continue


                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"


    def known_mines(self):
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):


        self.height = height
        self.width = width


        self.moves_made = set()


        self.mines = set()
        self.safes = set()


        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def add_knowledge(self, cell, count):

        self.moves_made.add(cell)


        self.mark_safe(cell)


        neighbors = set()
        row, col = cell
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):

                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) in self.mines:
                        count -= 1
                    elif (i, j) not in self.safes:
                        neighbors.add((i, j))


        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)


        while True:
            new_safes = set()
            new_mines = set()


            for sentence in self.knowledge:
                new_safes.update(sentence.known_safes())
                new_mines.update(sentence.known_mines())


            if new_safes:
                for s in new_safes.copy():
                    self.mark_safe(s)
            if new_mines:
                for m in new_mines.copy():
                    self.mark_mine(m)


            new_inferences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 != s2 and s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        new_s = Sentence(diff_cells, diff_count)
                        if new_s not in self.knowledge:
                            new_inferences.append(new_s)


            if not new_safes and not new_mines and not new_inferences:
                break

            self.knowledge.extend(new_inferences)

            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

    def make_safe_move(self):
        for move in self.safes:
            if move not in self.moves_made:
                return move
            return None

    def make_random_move(self):
        import random
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    possible_moves.append(move)

        if possible_moves:
            return random.choice(possible_moves)
        return None
