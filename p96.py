class Puzzle:
    def __init__(self, new_puzzle):

        self.puzzle = new_puzzle
        self.puzzle_size = 9
        self.moves = list()
        self.rowList = []
        self.colList = []
        self.boxList = []
        self.worked = False
        self.solvable = True

        self.setup()
        self.update_all_missing()

        self.run()

    # where the magic happens
    def run(self):
        filled = False
        guess = False

        # keep things going while
        while self.solvable and not filled:
            filled = True
            start_over = False
            row = 0
            column = 0

            # go through each row and column to fill a spot
            while row < self.puzzle_size:
                while column < self.puzzle_size:

                    # attempt to fill a spot, else if the spot is empty
                    if self.fill(row, column):
                        filled = False
                        start_over = True
                        break
                    elif self.puzzle[row][column] == 0:
                        filled = False

                    # attempt a guess
                    if guess and not filled:
                        if self.guess_number(row, column):
                            guess = False
                            start_over = True
                            break

                    column += 1

                if start_over:
                    break
                row += 1
                column = 0

            guess = not start_over

        self.worked = True

    # add 1-9 to every row, column, and box list
    def setup(self):
        init_list = [x for x in range(1, self.puzzle_size + 1)]
        for x in range(1, self.puzzle_size + 1):
            self.colList.append(set(init_list))
            self.rowList.append(set(init_list))
            self.boxList.append(set(init_list))

    # get the potential numbers that can go into this spot
    def get_potentials(self, r, c, cross_check=True, return_list=True):
        if self.puzzle[r][c] != 0:
            if cross_check or return_list:
                return list()
            else:
                return set()

        box_num = self.get_box_num(r, c)

        row_set = self.rowList[r]
        column_set = self.colList[c]
        box_set = self.boxList[box_num]

        # potentials will be what the row, box, and column need
        potentials = row_set & column_set & box_set

        # if we need to dig deeper to get a good answer, and if we do not already have a specific answer
        if cross_check and len(potentials) > 1:
            # if we need to find numbers that can be placed elsewhere
            potentials -= self.get_numbers_to_exclude(r, c, box_num)

        if return_list:
            return list(potentials)
        else:
            return potentials

    # check the rest of the empty spaces in the box, and get the possible numbers for each
    def get_numbers_to_exclude(self, r, c, box_num):
        box_set_exclusions = set()

        for row in range(self.puzzle_size):
            for column in range(self.puzzle_size):
                if self.puzzle[row][column] != 0 or \
                        (row == r and column == c):
                    continue

                if self.get_box_num(row, column) == box_num:
                    box_set_exclusions |= self.get_potentials(row, column, False, False)

        return box_set_exclusions

    # part of initial setup, updates lists to remove known 
    def update_all_missing(self):
        for r in range(self.puzzle_size):
            for c in range(self.puzzle_size):
                if self.puzzle[r][c]:
                    self.update_missing(r, c)

    # gets rid of numbers needed from lists
    def update_missing(self, r, c):
        self.rowList[r].discard(self.puzzle[r][c])
        self.colList[c].discard(self.puzzle[r][c])
        self.boxList[self.get_box_num(r, c)].discard(self.puzzle[r][c])

    # puts number back into spot
    def revert_move(self, r, c):
        self.rowList[r].add(self.puzzle[r][c])
        self.colList[c].add(self.puzzle[r][c])
        self.boxList[self.get_box_num(r, c)].add(self.puzzle[r][c])
        self.puzzle[r][c] = 0

    @staticmethod
    def get_box_num(r, c):
        return int(3 * int(r / 3) + int(c / 3))

    @staticmethod
    def get_total():
        return (100 * puzzle[0][0]) + (10 * puzzle[0][1]) + (1 * puzzle[0][2])

    # undo all moves that happened under previous guess
    def retry_last_guess(self):
        # if there are not any moves to undo, then we're screwed
        if len(self.moves) == 0:
            self.solvable = False
            return

        # undo each "legit" move until we reach a guess
        while len(self.moves) > 0:
            move = self.moves.pop()
            old_value = self.puzzle[move.row][move.column]
            self.revert_move(move.row, move.column)
            if move.guess_value != -1:
                break

        # if the first move was not a guess
        if move.guess_value == -1:
            self.solvable = False
            return

        # if the old_value is not in the list of potentials, somethings wrong.
        potentials = self.get_potentials(move.row, move.column, False)
        if old_value not in potentials:
            self.solvable = False
            return

        # get the index of the guess, if it was the last in the list, then we need to go back
        index = potentials.index(old_value) + 1
        if index >= len(potentials):
            self.retry_last_guess()
            return

        self.add_move(move.row, move.column, potentials[index], True)

    # puts in a number that fits even though we are not sure if its correct
    def guess_number(self, r, c):
        potentials = self.get_potentials(r, c, False)
        if len(potentials) == 0:
            if r is self.puzzle_size - 1 and c is self.puzzle_size - 1:
                self.retry_last_guess()
                return True
            else:
                return False

        self.add_move(r, c, potentials[0], True)
        return True

    # attempt to put correct number into spot
    def fill(self, r, c):
        potentials = self.get_potentials(r, c)

        if len(potentials) == 1:
            self.add_move(r, c, potentials[0])
            return True
        return False

    # handles adding a move to the list & actually making the move 
    def add_move(self, row, col, value, is_guess=False):
        self.puzzle[row][col] = value
        if not is_guess:
            value = -1
        self.moves.append(Move(row, col, value))
        self.update_missing(row, col)


class Move:
    def __init__(self, row, column, guess_value=-1):
        self.row = row
        self.column = column
        self.guess_value = guess_value


import urllib.request as request
import re

link = "https://projecteuler.net/project/resources/p096_sudoku.txt"
file = request.urlopen(link)

puzzle = None
total = 0
for line in file:
    line = str(line)
    if line.find("Grid") > 0:
        if puzzle is not None:
            total += Puzzle(puzzle).get_total()
        puzzle = []
        continue

    line = re.sub("[^0-9]", "", line)
    puzzle.append([int(x) for x in line])

total += Puzzle(puzzle).get_total()

print(total)
