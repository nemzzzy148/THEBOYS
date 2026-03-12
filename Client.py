import pygame
from signalrcore.hub_connection_builder import HubConnectionBuilder

W, H = 800, 600

p_x, p_y = W // 2, H // 2

Players = {}

url = "http://192.168.0.198:5001/positionHub"
connection = HubConnectionBuilder().with_url(url).build()

def listener(args):

    try:    
        Id, x, y = args

        if Players.get(Id) is None:
            print(f"Player not found!")

        Players[Id] = (x, y)

        print(f"Player {Id} moved to ({x}, {y})")
        print("Current Players:", len(Players))
    except Exception as e:
        print(f"Error in listener: {e}")

connection.on("SendPosition", listener)
connection.on("UserDisconnected", lambda args: Players.pop(args[0], None))
connection.on("UserConnected", lambda args: Players.update({args[0]: (args[1], args[2])}))
connection.start()

def move(x,y):
    p_x += x
    p_y += y
    connection.invoke("UpdatePosition", [x, y])

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Python Client")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move(-10, 0)
            elif event.key == pygame.K_RIGHT:
                move(10, 0)
            elif event.key == pygame.K_UP:
                move(0, -10)
            elif event.key == pygame.K_DOWN:
                move(0, 10)
    
    screen.fill((0, 0, 0))

    for Id, (x, y) in Players.items():
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 10)

    pygame.draw.circle(screen, (255, 0, 0), (p_x, p_y), 10)