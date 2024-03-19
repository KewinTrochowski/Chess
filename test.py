rook = [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),
        (0,-1),(0,-2),(0,-3),(0,-4),(0,-5),(0,-6),(0,-7),
        (1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),
        (-1,0),(-2,0),(-3,0),(-4,0),(-5,0),(-6,0),(-7,0)]

knight = [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]

bishop = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
          (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7),
          (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7),
          (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]

king = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

queen = rook + bishop


def to_chess_notation(x,y):
    dic = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h" }
    row = 8-x
    col = dic[y]
    return f"{col}{row}"

def calculate_legal_moves(pos,piece):
    print(f"Legal moves for {to_chess_notation(pos[0],pos[1])}")
    legal_moves = []
    for move in piece:
        x = pos[0] + move[0]
        y = pos[1] + move[1]
        if 0 <= x <= 7 and 0 <= y <= 7:
            print(to_chess_notation(x,y))
            legal_moves.append((x,y))

calculate_legal_moves([0,4],bishop)