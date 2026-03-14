import pygame
import numpy as np
from signalrcore.hub_connection_builder import HubConnectionBuilder

#multiplayer
players = {}
url = "https://asher-nonchangeable-averi.ngrok-free.dev/3dpositionhub"

connected = False 

connection = HubConnectionBuilder().with_url(url).build()
W,H = 1920,1080

def pos(x,y,z):
    if not connected:
        return
    connection.invoke("SendPosition" , [x,y,z])

def listener(args):
    try:
        Id, X, Y, Z = args
        players[Id] = (float(X),float(Y),float(Z))
    except Exception as e:
        print(f"Error: {e}")

def on_user_connect():
    return

def start_connection():
    global connected
    try:
        connection.start()
        connected = True
        print("connected!")
    except Exception as e:
        print(f"Error: {e}")

connection.on("Position", listener)
connection.on("UserDisconnected", lambda args: players.pop[args[0], None])

pygame.init()

screen = pygame.display.set_mode((W,H))

clock = pygame.time.Clock()

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

creative = False

f = 200.0

sensitivity = .005
speed = 10
jump = 1

gravity = -0.981

dt = 0 

velocity = 0

height = 2

NEAR = .0001


world_normal = np.array([0,1,0])

cam_pos = np.array([14,2,14], dtype = float)

yaw, pitch = 0,0

block_vertices = np.array([
    [-1,-1,-1],
    [ 1,-1,-1],
    [ 1, 1,-1],
    [-1, 1,-1],
    [-1,-1, 1],
    [ 1,-1, 1],
    [ 1, 1, 1],
    [-1, 1, 1]
], dtype = float)

block_faces = [
    (0,1,2,3),
    (4,5,6,7),
    (0,1,5,4),
    (2,3,7,6),
    (1,2,6,5),
    (0,3,7,4)
]

block_colors = [
    (139, 69, 19),
    (139, 69, 19),
    (139, 69, 19),
    (0,255,0),
    (139, 69, 19),
    (139, 69, 19),
]

player_color= [
    (255, 0, 0),
    (255, 0, 0),
    (255, 0, 0),
    (255, 0, 0),
    (255, 0, 0),
    (255, 0, 0)
]

big_block = np.array([
    [-50, -0.5, -50],
    [ 50, -0.5, -50],
    [ 50,  0.5, -50],
    [-50,  0.5, -50],
    [-50, -0.5,  50],
    [ 50, -0.5,  50],
    [ 50,  0.5,  50],
    [-50,  0.5,  50]
])
floor_colors_1 = [
    (0,255,0)
]
floor_colors_2 = [
    (0,200,0)
]
floor_vert = np.array([
    [-1, 0, -1],
    [ 1, 0, -1],
    [ 1, 0,  1],
    [-1, 0,  1]
], dtype=float)

floor_faces = [
    (0, 1, 2, 3)
]

dimensions = (25,25)

def project(vertex):
    z = vertex[2]
    if z < NEAR:
        return None
    x = vertex[0] * f / z + W/2
    y = vertex[1] * -f / z + H/2
    return (x,y)
def move(forward, z, x, y):
      global cam_pos
      right = np.cross(world_normal,forward)
      right /= np.linalg.norm(right)
      cam_pos += z*forward + x * right + y * world_normal
def walk(forward, x, y, z):
    global cam_pos
    global velocity

    horizontal_forward = np.array([forward[0], 0, forward[2]])
    if np.linalg.norm(horizontal_forward) != 0:
        horizontal_forward /= np.linalg.norm(horizontal_forward)

    right = np.cross(np.array([0,1,0]), horizontal_forward)
    right /= np.linalg.norm(right)
    
    # move
    cam_pos += z * horizontal_forward + x * right
    cam_pos[1] += y
      
def cam_angles_to_pos(yaw,pitch):
    forward = np.array([
        np.cos(pitch) * np.sin(yaw),
        np.sin(pitch),
        np.cos(pitch) * np.cos(yaw)
    ])
    forward /= np.linalg.norm(forward)
    return forward

def renderobject(vertices, faces, colors, ox,oy,oz):
     
    transformed = []

    for v in vertices:
        world = v - cam_pos + np.array([ox,oy,oz])

        x = np.dot(world, right)
        y = np.dot(world, up)
        z = np.dot(world, forward)
        transformed.append(np.array([x,y,z]))

    order = []

    for i,face in enumerate(faces):
        z = max(transformed[j][2] for j in face)
        order.append((i,z))
    order.sort(key= lambda x:x[1], reverse=True)

    for idx, _ in order:
        pts = []
        ok = True
        for vi in faces[idx]:
            p = project(transformed[vi])
            if p is None:
                ok = False
                break
            pts.append(p)
        if ok:
            pygame.draw.polygon(screen,colors[idx],pts)

def y_collision(pos, y):
    return y > pos

      
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
          running = False

    

    if keys[pygame.K_c]:
          creative = not creative

    screen.fill((135, 206, 235))

    mx, my = pygame.mouse.get_rel()
    yaw += -mx*sensitivity
    pitch += -my*sensitivity

    pitch = max(-1.5, min(pitch, 1,5))

    forward = cam_angles_to_pos(yaw,pitch)
    if creative:
        move(forward, 
     z = (speed * dt) if keys[pygame.K_w] else (-speed * dt) if keys[pygame.K_s] else 0,
     x = (-speed * dt) if keys[pygame.K_d] else (speed * dt) if keys[pygame.K_a] else 0,
     y = (speed * dt) if keys[pygame.K_SPACE] else (-speed * dt) if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT] else 0)

    right = np.cross(forward, world_normal)

    right /= np.linalg.norm(right)

    up = np.cross(right, forward)

    if not creative:
        walk(forward, 
        z = (speed * dt) if keys[pygame.K_w] else (-speed * dt) if keys[pygame.K_s] else 0,
        y = jump if keys[pygame.K_SPACE] else 0,
        x = (-speed * dt) if keys[pygame.K_d] else (speed * dt) if keys[pygame.K_a] else 0,)

        velocity += gravity * dt
        if y_collision(cam_pos[1] - height,0):
            velocity = 0
        else:
            cam_pos[1] += velocity


    for x in range(dimensions[0]):
        for z in range(dimensions[1]):
            if (x + z) % 2 == 0:
                renderobject(floor_vert, floor_faces, floor_colors_1, x, 0, z)
            else:
                renderobject(floor_vert, floor_faces, floor_colors_2, x, 0, z)

    renderobject(block_vertices, block_faces, player_color, cam_pos[0], cam_pos[1]-2, cam_pos[2])
            
    pygame.display.flip()
    dt = clock.tick()/1000

pygame.quit()