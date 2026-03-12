import pygame
from signalrcore.hub_connection_builder import HubConnectionBuilder
import threading

W, H = 800, 600
p_x, p_y = W // 2, H // 2
Players = {}
connected = False  # track connection state

url = "http://192.168.0.198:5001/positionhub"
connection = HubConnectionBuilder().with_url(url).build()

def move(x, y):
    global p_x, p_y
    if not connected:  # guard: don't invoke if not connected
        return
    p_x += x
    p_y += y
    connection.invoke("SendPosition", [p_x, p_y])

def listener(args):
    try:
        Id, x, y = args
        Players[Id] = (int(x), int(y))
    except Exception as e:
        print(f"Error in listener: {e}")

def on_user_connected(args):
    try:
        if len(args) >= 3:
            Players[args[0]] = (int(args[1]), int(args[2]))
        elif len(args) == 1:
            Players[args[0]] = (W // 2, H // 2)
    except Exception as e:
        print(f"Error in on_user_connected: {e}")

def start_connection():
    global connected
    try:
        connection.start()
        connected = True
        print("Connected to SignalR hub!")
    except Exception as e:
        print(f"Connection failed: {e}")

connection.on("Position", listener)
connection.on("UserDisconnected", lambda args: Players.pop(args[0], None))
connection.on("UserConnected", on_user_connected)

threading.Thread(target=start_connection, daemon=True).start()

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Python Client")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

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

    # show connection status on screen
    if not connected:
        text = font.render("Connecting...", True, (255, 255, 0))
        screen.blit(text, (10, 10))

    for Id, (x, y) in list(Players.items()):
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 10)

    pygame.draw.circle(screen, (0, 255, 0), (p_x, p_y), 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
connection.stop()
