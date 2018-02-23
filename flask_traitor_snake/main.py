from AStar import *
import copy
import math
import os

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
def goals(data):
    result = data['food']
    if data['mode'] == 'advanced':
        result.extend(data['gold'])
    return result

def direction(from_cell, to_cell):
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]

    if dx == 1:
        return 'east'
    elif dx == -1:
        return 'west'
    elif dy == -1:
        return 'north'
    elif dy == 1:
        return 'south'

def distance(p, q):
    dx = abs(p[0] - q[0])
    dy = abs(p[1] - q[1])
    return dx + dy;

def closest(items, start):
    closest_item = None
    closest_distance = 10000

    # TODO: use builtin min for speed up
    for item in items:
        item_distance = distance(start, item)
        if item_distance < closest_distance:
            closest_item = item
            closest_distance = item_distance

    return closest_item

def init(data):
    grid = [[0 for col in xrange(data['height'])] for row in xrange(data['width'])]
    mysnake = data['you'] 
    for snek in data['snakes']['data']:
        for coord in snek['body']['data']:
            grid[coord['x'],coord['y']] = SNAKE



    for f in data['food']['data']:
        grid[f['x']][f['y']] = FOOD
    print("init complete")
    return mysnake, grid

#@bottle.route('/static/<path:path>')
#def static(path):
#    return bottle.static_file(path, root='static/')


#@bottle.get('/')
#def index():
#    head_url = '%s://%s/static/Traitor.gif' % (
#        bottle.request.urlparts.scheme,
#        bottle.request.urlparts.netloc
#    )

#    return {
#        'color': '#00ff00',
#        'head': head_url
#    }


@app.route("/start", methods=["GET","HEAD","POST","PUT"])
def start():
    # NOTE: 'request' contains the data which was sent to us about the Snake game
    # after every POST to our server 
    #print(request.__dict__) 
    print(request.data)
    snake = {
        "color": "ffffff",
        "name": "ObbleBooble"
    }
    return jsonify(snake)
    
# DATA OBJECT
# {
#     "you": <snake object>,
#     "turn": 4,
#     "height": 20,
#     "width": 30,
#     "snakes": [
#         <Snake Object>, <Snake Object>, ...
#     ],
#     "food": [
#         [1, 2], [9, 3], ...
#     ],
#     "walls": [    // Advanced Only
#         [2, 2]
#     ],
#     "gold": [     // Advanced Only
#         [5, 5]
#     ]
# }

#SNAKE
# {
#     "taunt" : "",
#     "object" : "snake",
#     "id": "1234-567890-123456-7890",
#     "name": "Well Documented Snake",
#     "length" : 3
#     "status": "alive",
#     "health" : 100,
#     "body" : <body object>
# }

#BODY
#        "object":"list",
#        "data":
#        [
#            {"y":15,"x":15,"object":"point"},
#            {"y":15,"x":15,"object":"point"},
#            {"y":15,"x":15,"object":"point"}
#        ]

@app.route("/move", methods=["GET","HEAD","POST","PUT"])
def move():
    dataStr = str(request.data)
    print dataStr
    data = json.loads(dataStr)
    snek, grid = init(data)

    #foreach snake
    for enemy in data['snakes']['data']:
        if (enemy['id'] == ID):
            continue
        if distance(snek['coords'][0], enemy['coords'][0]) > SNEK_BUFFER:
            continue
        if (len(enemy['coords']) > len(snek['coords'])-1):
            #dodge
            if enemy['coords'][0][1] < data['height']-1:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1]+1] = SAFTEY
            if enemy['coords'][0][1] > 0:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1]-1] = SAFTEY

            if enemy['coords'][0][0] < data['width']-1:
                grid[enemy['coords'][0][0]+1][enemy['coords'][0][1]] = SAFTEY
            if enemy['coords'][0][0] > 0:
                grid[enemy['coords'][0][0]-1][enemy['coords'][0][1]] = SAFTEY


    snek_head = snek['coords'][0]
    snek_coords = snek['coords']
    path = None
    middle = [data['width'] / 2, data['height'] / 2]
    foods = sorted(data['food'], key = lambda p: distance(p,middle))
    if data['mode'] == 'advanced':
        foods = data['gold'] + foods
    for food in foods:
        #print food
        tentative_path = a_star(snek_head, food, grid, snek_coords)
        if not tentative_path:
            #print "no path to food"
            continue

        path_length = len(tentative_path)
        snek_length = len(snek_coords) + 1

        dead = False
        for enemy in data['snakes']:
            if enemy['id'] == ID:
                continue
            if path_length > distance(enemy['coords'][0], food):
                dead = True
        if dead:
            continue

        # Update snek
        if path_length < snek_length:
            remainder = snek_length - path_length
            new_snek_coords = list(reversed(tentative_path)) + snek_coords[:remainder]
        else:
            new_snek_coords = list(reversed(tentative_path))[:snek_length]

        if grid[new_snek_coords[0][0]][new_snek_coords[0][1]] == FOOD:
            # we ate food so we grow
            new_snek_coords.append(new_snek_coords[-1])

        # Create a new grid with the updates snek positions
        new_grid = copy.deepcopy(grid)

        for coord in snek_coords:
            new_grid[coord[0]][coord[1]] = 0
        for coord in new_snek_coords:
            new_grid[coord[0]][coord[1]] = SNAKE

        #printg(grid, 'orig')
        #printg(new_grid, 'new')

        #print snek['coords'][-1]
        foodtotail = a_star(food,new_snek_coords[-1],new_grid, new_snek_coords)
        if foodtotail:
            path = tentative_path
            break
        #print "no path to tail from food"



    if not path:
        path = a_star(snek_head, snek['coords'][-1], grid, snek_coords)

    despair = not (path and len(path) > 1)

    if despair:
        for neighbour in neighbours(snek_head,grid,0,snek_coords, [1,2,5]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            #print 'i\'m scared'
            break

    despair = not (path and len(path) > 1)


    if despair:
        for neighbour in neighbours(snek_head,grid,0,snek_coords, [1,2]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            #print 'lik so scared'
            break

    if path:
        assert path[0] == tuple(snek_head)
        assert len(path) > 1

    return {
        'move': direction(path[0], path[1]),
        'taunt': 'TRAITOR!'
    }


@app.route("/end", methods=["GET","HEAD","POST","PUT"])
def end():

    # TODO: Do things with data

    return {
        'taunt': 'battlesnake-python!'
    }


if __name__ == "__main__":
    app.run(host='192.168.1.148', port=8087, debug=True)