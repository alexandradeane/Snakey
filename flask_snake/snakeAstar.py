from AStar import *
from flask import Flask, request, jsonify
import json
import random
import pdb

app = Flask(__name__)

SNEK_BUFFER = 3
ID = 'de508402-17c8-4ac7-ab0b-f96cb53fbee8'
SNAKE = 1
WALL = 2
FOOD = 3
GOLD = 4
SAFTEY = 5


def init(data):
    grid = [[0 for col in xrange(data['height'])] for row in xrange(data['width'])]
    mysnake = data['you'] 
    
    for snek in data['snakes']['data']:
        points = snek["body"]["data"]
        for pnt in points :
            print ("whereIam: ", pnt["x"],pnt["y"])
            grid[pnt["x"]][pnt["y"]] = SNAKE
        
    for f in data['food']['data']:
        grid[f['x']][f['y']] = FOOD
    print("init complete")
    return mysnake, grid

def direction(from_cell, to_cell):
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]

    if dx == 1:
        return 'right'
    elif dx == -1:
        return 'left'
    elif dy == -1:
        return 'up'
    elif dy == 1:
        return 'down'

@app.route("/start", methods=["GET","HEAD","POST","PUT"])
def start():
    # NOTE: 'request' contains the data which was sent to us about the Snake game
    # after every POST to our server 
    #print(request.__dict__) 
    print(request.data)
    snake = {
        "color": "ffffff",
        "name": "SneethSnake"
    }

    return jsonify(snake)

@app.route("/move", methods=["GET","HEAD","POST","PUT"])
def move():
    dataStr = str(request.data)
    jsonData = json.loads(dataStr)
    #pdb.set_trace()
    snek,grid = init(jsonData)
    HeadX = snek['body']['data'][0]['x']
    HeadY = snek['body']['data'][0]['y']
    width = jsonData["width"]
    height = jsonData["height"]
    Direction = "up"
    
    start = [HeadX,HeadY]
    #most of the logic will be choosing good goal locations on the grid
    #default is the middle of the grid
    goal = [width / 2, height /2]
    #get the first food if it exists, would be better to go for the closest if multiple foods
    if len(jsonData['food']['data']) > 0:
        goal = [jsonData['food']['data'][0]['x'],jsonData['food']['data'][0]['y']]
    #find the path from 'start' to 'goal'
    path = a_star(start, goal, grid, snek["body"]["data"])
    
    #print("head ", HeadX, HeadY)
    #print('\n'.join([''.join(['{:2}'.format(item) for item in row]) 
    #  for row in grid]))
    if path:
        Direction = direction(path[0], path[1])
    else:
        #crap! no path, what to do?! choose a safe emergency move
        Direction = FindSafeMoveDirection(HeadX,HeadY,grid,width,height)
    
    print Direction
    moves = ["up", "down", "left", "right"]
    response = {
        "move": Direction
    }


    return jsonify(response)

def FindSafeMoveDirection(HeadX, HeadY, grid, width, height):    
    Direction = "up";
    if IsSafe(HeadX - 1, HeadY, grid, width, height):
        Direction = "left"
    if IsSafe(HeadX + 1, HeadY, grid, width, height):
        Direction = "right"
    if IsSafe(HeadX, HeadY - 1, grid, width, height):
        Direction = "up"
    if IsSafe(HeadX, HeadY + 1, grid, width, height):
        Direction = "down" 
    return Direction

def IsSafe(x, y, grid, width, height):
    if x < 0:
        return False
    if x >= width:
        return False
    if y < 0:
        return False
    if y >= height:
        return False
    if grid[x][y] == 0:
        return True
    elif grid[x][y] == 3:
        return True
    else:
        return False
        
if __name__ == "__main__":
    app.run(host='192.168.56.1', port=8089, debug=True)
