"""
This class is responsible for storing all the information about the current state of a chess game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""


class GameState():
    def __init__(self):
        # The board is an 8x8 2d list, each element of the list has 2 characters
        # The first character represents the color of the pieces and the second represents the type
        # "--"  represents an empty space

        '''
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 0 to Column 0 - 7
            ["--", "--", "--", "--", "wK", "--", "--", "--"],  # Row 1 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 2 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "bK"],  # Row 3 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 4 to Column 0 - 7
            ["--", "--", "wp", "--", "--", "--", "--", "--"],  # Row 5 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "wR", "--"],  # Row 6 to Column 0 - 7
            ["wQ", "--", "--", "--", "--", "--", "--", "--"]]  # Row 7 to Column 0 - 7
        '''

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Row 0 to Column 0 - 7
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Row 1 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 2 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 3 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 4 to Column 0 - 7
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Row 5 to Column 0 - 7
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # Row 6 to Column 0 - 7
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]  # Row 7 to Column 0 - 7


        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # (row,col) for the square where en passant is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant).
    '''

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # Log the move
        self.whiteToMove = not self.whiteToMove  # Swap players

        # Update the King's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.pawnPromotionPiece != False:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.pawnPromotionPiece  # Replace pawn by "R", "N", "B" or "Q"

        # En passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # Capture pawn

        # Capture en passant
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:  # Only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()  # Reset enpassant square

        # Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # King side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1]  # Copy rook to new square
                self.board[move.endRow][move.endCol + 1] = "--"  # Erase old rook
            else:  # Queen side castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2]  # Copy rook to new square
                self.board[move.endRow][move.endCol - 2] = "--"  # Erase old rook

        # Update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
    Undo the last move made.
    '''

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            if len(self.moveLog) != 0:
                previousMove = self.moveLog[-1]
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turn back
            # Update the King's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # Undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # Update en passant possible
            if len(self.moveLog) != 0:
                if previousMove.pieceMoved[1] == "p" and abs(previousMove.startRow - previousMove.endRow) == 2:
                    self.enpassantPossible = ((previousMove.startRow + previousMove.endRow) // 2,
                                              previousMove.endCol)  # Restore the deleted possible en passant move
            # Undo castling rights
            self.castleRightsLog.pop()  # Get rid of the new castle rights from the move we are undoing
            newCastleRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newCastleRights.wks, newCastleRights.bks, newCastleRights.wqs,
                                                     newCastleRights.bqs)  # Set the current castle rights to the last one in the list
            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King side castle move
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # Queen side castle move
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # Undo check mate and stale mate
            self.checkMate = False
            self.staleMate = False

    '''
    Update the castle rights given the move
    '''

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # Left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # Right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # Left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # Right rook
                    self.currentCastlingRight.bks = False

    '''
    All moves considering checks:
    '''

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible  # Safe copy of en passant move
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1.) generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # 2.) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # When removing from a list go backwards through the list
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove  # Correct the switch due to call of makeMove()
            # 3.) generate all opponent's moves
            # 4.) for each of your opponent's moves, see if they attack your king
            # 5.) if they do attack your king, not a valid move
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # Either checkmate or stalemate if no possible moves available
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        if len(self.moveLog) >= 6: # stalemate if move repetition
            if (self.moveLog[-6].moveID == self.moveLog[-2].moveID) and (self.moveLog[-5].moveID == self.moveLog[-1].moveID):
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    '''
    Determine if the current player is in check
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy can attack the square (row, col)
    '''

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove  # Switch to opponents point of view
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # Switch to own view back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:  # Square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):  # Number of rows
            for col in range(len(self.board[row])):  # Number of columns in given row
                turn = self.board[row][col][0]  # Get color of piece form piece name
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)  # Calls the appropriate move function based on piece type
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove and row > 0:  # White pawn moves
            if self.board[row - 1][col] == "--":  # If row in front is empty
                if row > 1:
                    moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 1: # pawn promotion
                    moves.extend([Move((row, col), (row - 1, col), self.board, pawnPromotionPiece=piece) for piece in ["R", "N", "B", "Q"]])
                if row == 6 and self.board[row - 2][col] == "--":  # Two square pawn advance
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # Capture to the left
                if self.board[row - 1][col - 1][0] == "b":  # Enemy piece to capture
                    if row > 1:
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
                    if row == 1:  # pawn promotion
                        moves.extend(
                            [Move((row, col), (row - 1, col - 1), self.board, pawnPromotionPiece=piece) for piece in ["R", "N", "B", "Q"]])
                elif (row - 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True))
            if col + 1 <= 7:  # Capture to the right
                if self.board[row - 1][col + 1][0] == "b":  # Enemy piece to capture
                    if row > 1:
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
                    if row == 1:  # pawn promotion
                        moves.extend([Move((row, col), (row - 1, col + 1), self.board, pawnPromotionPiece=piece) for piece in ["R", "N", "B", "Q"]])
                elif (row - 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True))
        if not self.whiteToMove and row < 7:  # Black pawn moves
            if self.board[row + 1][col] == "--":  # If row in front is empty
                if row < 6:
                    moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 6:  # pawn promotion
                    moves.extend([Move((row, col), (row + 1, col), self.board, pawnPromotionPiece=piece) for piece in ["R", "N", "B", "Q"]])
                if row == 1 and self.board[row + 2][col] == "--":  # Two square pawn advance
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # Capture to the right
                if self.board[row + 1][col - 1][0] == "w":  # Enemy piece to capture
                    if row < 6:
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                    if row == 6:  # pawn promotion
                        moves.extend([Move((row, col), (row + 1, col - 1), self.board, pawnPromotionPiece=piece) for piece in ["R", "N", "B", "Q"]])
                elif (row + 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True))
            if col + 1 <= 7:  # Capture to the left
                if self.board[row + 1][col + 1][0] == "w":  # Enemy piece to capture
                    if row < 6:
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                    if row == 6:  # pawn promotion
                        moves.extend([Move((row, col), (row + 1, col + 1), self.board, pawnPromotionPiece=piece) for piece in ["R", "N", "B", "Q"]])
                elif (row + 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove=True))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''

    def getRookMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for multiplier in range(1, 8):
                endRow = row + direction[0] * multiplier
                endCol = col + direction[1] * multiplier
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Check if on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty space valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # Friendly piece in front
                        break
                else:  # Off board
                    break

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''

    def getKnightMoves(self, row, col, moves):
        directions = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2))  # Up-left-left, up-up-left, up-up-right, up-right-right, down-left-left, down-down-left, down-down-right, down-right-right
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            endRow = row + direction[0]
            endCol = col + direction[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Check if on board
                endPiece = self.board[endRow][endCol]
                if endPiece == "--":  # Empty space valid
                    moves.append(Move((row, col), (endRow, endCol), self.board))
                elif endPiece[0] == enemyColor:  # Enemy piece valid
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''

    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # Up-left, down-left, up-right, down-right
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for multiplier in range(1, 8):
                endRow = row + direction[0] * multiplier
                endCol = col + direction[1] * multiplier
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Check if on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty space valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # Friendly piece in front
                        break
                else:  # Off board
                    break

    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''

    def getQueenMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1),
                      (1, 1))  # Up, left, down, right, Up-left, down-left, up-right, down-right
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for multiplier in range(1, 8):
                endRow = row + direction[0] * multiplier
                endCol = col + direction[1] * multiplier
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Check if on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty space valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # Friendly piece in front
                        break
                else:  # Off board
                    break

    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''

    def getKingMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1),
                      (1, 1))  # Up, left, down, right, Up-left, down-left, up-right, down-right
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            endRow = row + direction[0]
            endCol = col + direction[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Check if on board
                endPiece = self.board[endRow][endCol]
                if endPiece == "--":  # Empty space valid
                    moves.append(Move((row, col), (endRow, endCol), self.board))
                elif endPiece[0] == enemyColor:  # Enemy piece valid
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    '''
    Generate all valid castle moves for the king at (row,col) and add them to the list of moves
    '''

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return  # Can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White king side
        self.bks = bks  # Black king side
        self.wqs = wqs  # White queen side
        self.bqs = bqs  # Black queen side

class Move():
    # Maps coordinates like (0,0) to chess notation like a8
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}  # Reversing the dictionary
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}  # Reversing the dictionary

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False, pawnPromotionPiece=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion:                                                                                                <--------------------------
        self.pawnPromotionPiece = pawnPromotionPiece
        # En passant:
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        # Castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # Generate a move ID

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.moveID == other.moveID) and (self.pawnPromotionPiece == other.pawnPromotionPiece)
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]