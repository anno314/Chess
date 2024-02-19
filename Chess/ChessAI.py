import random
import numpy as np
import numba

CHECKMATE = np.inf
STALEMATE = -1

'''
Picks and return a random move.
'''
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

'''
Find the best move based on material alone.
'''

def findMinMaxGreedyMoveOneStep(gs, validMoves): #Minimize the opponents next maximum move
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE #Intial total board score
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.makeMove(opponentsMove)
            if gs.checkMate:
                score = -turnMultiplier * CHECKMATE
            elif gs.staleMate:
                score = -turnMultiplier * STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def findMinMaxGreedyMoveMultipleSteps(gs, playerBestMove, depth, alpha, beta):
    #Value of last knots
    if depth == 0 or gs.checkMate or gs.staleMate:
        turnMultiplier = 1 if gs.whiteToMove else -1
        if gs.checkMate:
            score = turnMultiplier*CHECKMATE
        elif gs.staleMate:
            score = turnMultiplier*STALEMATE
        else:
            score = scoreMaterial(gs.board)
        return score, playerBestMove

    #Iterative valuation for white
    if gs.whiteToMove:
        maxEval = -np.inf
        for playerMove in gs.getValidMoves():
            gs.makeMove(playerMove)
            if gs.checkMate:
                maxEval = CHECKMATE
                playerBestMove = playerMove
            elif gs.staleMate:
                maxEval = -STALEMATE
                playerBestMove = playerMove
            else:
                eval = findMinMaxGreedyMoveMultipleSteps(gs, playerBestMove, depth-1, alpha, beta)[0]
                gs.undoMove()
                if eval > maxEval:
                    playerBestMove = playerMove
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return maxEval, playerBestMove

    #Iterative valuation for black
    else:
        minEval = np.inf
        for playerMove in gs.getValidMoves():
            gs.makeMove(playerMove)
            if gs.checkMate:
                minEval = -CHECKMATE
                playerBestMove = playerMove
            elif gs.staleMate:
                minEval = -STALEMATE
                playerBestMove = playerMove
            else:
                eval = findMinMaxGreedyMoveMultipleSteps(gs, playerBestMove, depth-1, alpha, beta)[0]
                gs.undoMove()
                if eval < minEval:
                    playerBestMove = playerMove
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return minEval, playerBestMove

'''
Score the board based on material.
'''
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1} #King is equal to zero since they cancel each other out

rookBoardScore = [[4, 3, 4, 4, 4, 4, 3, 4],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [4, 3, 4, 4, 4, 4, 3, 4]]

knightBoardScore = [[1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1]]

bishopBoardScore = [[4, 3, 2, 1, 1, 2, 3, 4],
                    [3, 4, 3, 2, 2, 3, 4, 3],
                    [2, 3, 4, 3, 3, 4, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 4, 3, 3, 4, 3, 2],
                    [3, 4, 3, 2, 2, 3, 4, 3],
                    [4, 3, 2, 1, 1, 2, 3, 4]]

queenBoardScore = [[1, 1, 1, 3, 1, 1, 1, 1],
                    [1, 1, 2, 3, 2, 1, 2, 1],
                    [1, 4, 3, 3, 3, 4, 2, 1],
                    [1, 2, 3, 3, 3, 2, 2, 1],
                    [1, 2, 3, 3, 3, 2, 2, 1],
                    [1, 4, 3, 3, 3, 4, 2, 1],
                    [1, 1, 2, 3, 2, 1, 2, 1],
                    [1, 1, 1, 3, 1, 1, 1, 1]]

kingBoardScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

whitePawnBoardScore = [[8, 8, 8, 8, 8, 8, 8, 8],
                        [8, 8, 8, 8, 8, 8, 8, 8],
                        [5, 6, 6, 7, 7, 6, 6, 5],
                        [2, 3, 3, 5, 5, 3, 3, 2],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [1, 1, 2, 3, 3, 2, 1, 1],
                        [1, 1, 1, 0, 0, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnBoardScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 0, 0, 1, 1, 1],
                        [1, 1, 2, 3, 3, 2, 1, 1],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [2, 3, 3, 5, 5, 3, 3, 2],
                        [5, 6, 6, 7, 7, 6, 6, 5],
                        [8, 8, 8, 8, 8, 8, 8, 8],
                        [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"R": rookBoardScore, "N": knightBoardScore, "B": bishopBoardScore, "Q": queenBoardScore, "K": kingBoardScore, "wp": whitePawnBoardScore, "bp": blackPawnBoardScore}

def scoreMaterial(board):
    score = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            square = board[row][col]

            if square != "--":
                piecePositionScore = 0

                if square == "wp":
                    piecePositionScore = piecePositionScores["wp"][row][col]

                elif square == "bp":
                    piecePositionScore = piecePositionScores["bp"][row][col]

                elif square[1] != "p":
                    piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == "w":
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == "b":
                    score -= pieceScore[square[1]] + piecePositionScore * .1

    return score


