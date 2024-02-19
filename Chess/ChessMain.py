"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
import pygame.transform
import numpy as np
import keyboard as k

from Chess import ChessEngine
from Chess import ChessAI

WIDTH = HEIGHT = 512 #400 is another option
DIMENSION = 8
SQ_SIZE =HEIGHT // DIMENSION
MAX_FPS = 15 #for animation
IMAGES = {}

'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,WIDTH))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #Flag variable for when a move is made
    loadImages() #Only do this once, before the while loop
    sqSelected = () #No square is selected, keep track of the last click of the user (tuple: (row,col))
    playerClicks = [] #Keep track of player click (two tuples: [(x_1,y_1),(x_2,y_2)])
    gameOver = False
    playerSelected = False
    playerWhite = True #True if player is human
    playerBlack = True #Ture if player is human
    print('Choose a player ("w" for white, "b" for black, "space" for both, "n" for none)')

    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerWhite) or (not gs.whiteToMove and playerBlack)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn and playerSelected:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col): #the user clicked the same square twice
                        sqSelected = (row,col)
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2: #after 2nd click
                        move = ChessEngine.Move(startSq=playerClicks[0], endSq=playerClicks[1], board=gs.board)
                        if (gs.whiteToMove and move.pieceMoved == "wp" and move.endRow == 0) or (not gs.whiteToMove and move.pieceMoved == "bp" and move.endRow == 7):
                            # Request input for pawn promotion
                            print("Promote your pawn!")
                            print("Press 1 -> Rook, 2 -> Night, 3 -> Bishop or 4 -> Queen to continue...")
                            while True:
                                keyPressed = k.read_event(suppress=True).name
                                if keyPressed in ["1", "2", "3", "4"]:
                                    if keyPressed == "1":
                                        move.pawnPromotionPiece = "R"
                                    elif keyPressed == "2":
                                        move.pawnPromotionPiece = "N"
                                    elif keyPressed == "3":
                                        move.pawnPromotionPiece = "B"
                                    elif keyPressed == "4":
                                        move.pawnPromotionPiece = "Q"
                                    break

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                sqSelected = () #reset user clicks
                                playerClicks = [] #clear list
                                print(move.getChessNotation())
                                moveMade = True
                                break
                        if not moveMade:
                            playerClicks = [sqSelected]

            #Key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo move when "z" is pressed
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                    print("Undo last move")
                if e.key == p.K_r: #Reset the board when "r" is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    playerSelected = False
                    playerWhite = True
                    playerBlack = True
                    print('Reset game - Choose a player ("w" for white, "b" for black, "space" for both, "n" for none)')
                if e.key == p.K_w: #Select white when "w" is pressed
                    playerSelected = True
                    playerBlack = False
                    #print("You selected white")
                if e.key == p.K_b: #Select black when "b" is pressed
                    playerSelected = True
                    playerWhite = False
                    #print("Yous selected black")
                if e.key == p.K_SPACE: #Select white and black when "space" is pressed
                    playerSelected = True
                    #print("You selected player vs. player")
                if e.key == p.K_n: #Select non when "n" is pressed
                    playerWhite = False
                    playerBlack = False
                    playerSelected = True
                    #print("You selected machine vs. machine")


        #AI move finder
        if not gameOver and not humanTurn:

            #######################   Chess AI   #######################
            AIMove = ChessAI.findMinMaxGreedyMoveMultipleSteps(gs, playerBestMove=None, depth=4, alpha=-np.inf, beta=np.inf)[1]
            #AIMove = ChessAI.findMinMaxGreedyMoveOneStep(gs, validMoves)
            ############################################################

            if AIMove is None:
                AIMove = ChessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            # print(AIMove.getChessNotation())

        if moveMade:
            validMoves = gs.getValidMoves() # Generate new list of all valid moves
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if not playerSelected:
            drawText(screen, 'Choose a player')
        if gs.checkMate:
            gameOver = True
            drawText(screen, 'Checkmate')

        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces = ['wp','wR','wN','wB','wK','wQ','bp','bR','bN','bB','bK','bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'),(SQ_SIZE,SQ_SIZE))
    # Note: we can access an image by saying for example 'IMAGES['wp']'

'''
Highlight square selected and moves for piece selected 
'''
def highlightSquares(screen, gs, sqSelected):
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)  # Transparency value -> 0 transparent; 255 opaque
    s.fill(p.Color('yellow'))

    # Highlight last enemy move
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        screen.blit(s, (lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))

    if  sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"): # sqSelected is a piece that can be moved
            # Highlight selected square
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))

            # Highlight moves from the selected square
            for move in gs.getValidMoves():
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

'''
Responsible for all the graphics within a current game state.
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on top of those squares

'''
Draw the squares on the board. the top left square is always light.
'''
def drawBoard(screen):
    colors = [p.Color('white'), p.Color('aquamarine4')] # Colors: grey, aquamarine4, seagreen4
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row+col)%2)]
            p.draw.rect(screen,color,p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board 
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--': # Not empty square
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE,SQ_SIZE))

def drawText(screen, text):
    font = p.font.SysFont('Helvitca', 50, True, False)
    textObject = font.render(text, 0, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT, ).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()

