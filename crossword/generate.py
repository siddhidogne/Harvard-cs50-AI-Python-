import sys
from crossword import Crossword, Variable


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)


        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node consistent.
        """
        for var in self.domains:

            to_remove = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    to_remove.add(word)
            for word in to_remove:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        # Agar koi overlap nahi hai, toh revision ki zarurat nahi
        if overlap is None:
            return False

        i, j = overlap
        to_remove = set()

        for word_x in self.domains[x]:
            # Check karein ki kya y ke domain mein koi aisi word hai jo x ke sath match kare
            if not any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                to_remove.add(word_x)
                revised = True

        for word in to_remove:
            self.domains[x].remove(word)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        """
        # Agar arcs None hai, toh saare possible arcs se shuru karein
        if arcs is None:
            queue = []
            for v1 in self.domains:
                for v2 in self.crossword.neighbors(v1):
                    queue.append((v1, v2))
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                # Agar x ka domain badla, toh uske baaki padosiyon ko phir se check karein
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each crossword variable).
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words are unique, correct length, no conflicts).
        """

        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False

        for var, word in assignment.items():

            if len(word) != var.length:
                return False


            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False
        return True




    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable using MRV and degree heuristics.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        # MRV: Sabse kam remaining values wala variable pehle
        return min(unassigned, key=lambda v: (len(self.domains[v]), -len(self.crossword.neighbors(v))))

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in arbitrary order.
        (Heuristics like LCV are optional but good for efficiency).
        """
        return list(self.domains[var])

def main():


    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")


    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None


    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()


    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

