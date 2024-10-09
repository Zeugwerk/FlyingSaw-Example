import pygame
import random
import pyads

# Pygame initialization
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height)) 
pygame.display.set_caption("Conveyor Simulation")

# Fonts
font = pygame.font.SysFont("Arial", 24)
logo_font = pygame.font.Font(pygame.font.get_default_font(), 32)

# Colors
BACKGROUND_COLOR = (71, 91, 120)
CONVEYOR_COLOR = (245, 241, 238)
BOX_COLOR = (218, 119, 109)
BOX_SHADOW_COLOR = (150, 80, 70) 
SENSOR_COLOR = (245, 241, 238)
SENSOR_ACTIVE_COLOR = (218, 119, 109)
ROBOT_ARM_COLOR = (202, 208, 222)
ROBOT_ARM_SHADOW_COLOR = (142, 148, 162)

# Conveyor parameters
conveyor_width = 300
conveyor_height = 100
conveyor_y = screen_height / 2 + conveyor_height  # Position conveyor

# Box parameters
box_width, box_height = 60, 60

# Sensor parameters
sensor_width, sensor_height = 10, conveyor_height
sensor_x = 100  # Position sensor
sensor_y = conveyor_y

# Robot arm parameters
robot_arm_width, robot_arm_height = box_width / 3, box_width * 1.5
robot_arm_x = sensor_x
robot_arm_y = conveyor_y - 60
robot_arm_length = 80  # Length of the robot arm
robot_arm_offset = 0
robot_arm_speed = 5

netid = None

box_counter = 1

# Box structure
class Box:
    def __init__(self, box_id, x):
        self.id = box_id
        self.x = x
        self.y = conveyor_y + 20
        self.color = BOX_COLOR
        self.shadow_color = BOX_SHADOW_COLOR

def spawn(box_id):
    new_box = Box(box_id, -box_width / 2)  # Create a new box with a unique ID
    boxes.append(new_box)

def draw_rect_with_shadow(x, y, width, height, color, shadow_color):
    # Draw shadow
    shadow_rect = pygame.Rect(x + 5, y + 5, width, height)
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=5)

    # Draw box
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=5)    

def draw_box_with_shadow(box):
    draw_rect_with_shadow(box.x, box.y, box_width, box_height, box.color, box.shadow_color)

def draw_box_info():
    for i, box in enumerate(boxes):
        text_surface = font.render(f'Box ID: {box.id:03}', True, (255, 255, 255))
        screen.blit(text_surface, (10, 10 + i * 30))

def read_robot_pos(plc):
    return plc.read_by_name(f"ZGlobal.Com.Unit.Machine.Publish.Equipment.ToolX.Base.ActualPosition", pyads.PLCTYPE_LREAL)     

def read_conveyor_vel(plc):
    return plc.read_by_name(f"ZGlobal.Com.Unit.Machine.Publish.Equipment.TransportX.Base.ActualVelocity", pyads.PLCTYPE_LREAL)

def write_box_detected(plc, on):
    plc.write_by_name(f"ZGlobal.Com.Unit.Machine.Subscribe.Equipment.BoxDetected.Enable", on, pyads.PLCTYPE_BOOL)
    plc.write_by_name(f"ZGlobal.Com.Unit.Machine.Subscribe.Equipment.BoxDetected.Write", True, pyads.PLCTYPE_BOOL) 

def lerp(a, b, t):
    return a + (b - a) * t

# Connect to PLC
if netid is None:
    pyads.ads.open_port()
    netid = pyads.ads.get_local_address().netid
    pyads.ads.close_port()

plc = pyads.Connection("127.0.0.1.1.1", 851)
plc.open()


# Initialize box list
boxes = []

# Timer for spawning boxes
spawn_timer = 0
spawn_interval = random.randint(1000, 4000)  # Random interval between 1 sec and 4 sec

# Main loop
sensor_active_plc = False
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.get_time() / 1000.0
    
    screen.fill(BACKGROUND_COLOR)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    robot_arm_x = lerp(robot_arm_x, read_robot_pos(plc) + sensor_x, 0.5)
    box_speed = int(read_conveyor_vel(plc)) * dt
    
    # Update box positions
    for box in boxes:
        box.x += box_speed  # Move box to the left
        if box.x > screen_width:
            boxes.remove(box)

    # Check for collisions with the sensor
    sensor_rect = pygame.Rect(sensor_x, sensor_y, sensor_width, sensor_height)
    sensor_active = False

    for box in boxes:
        box_rect = pygame.Rect(box.x, box.y, box_width, box_height)
        if sensor_rect.colliderect(box_rect):
            sensor_active = True
            break
        
    # Update sensor status
    if sensor_active != sensor_active_plc:
        sensor_active_plc = sensor_active
        write_box_detected(plc, sensor_active)

    # Draw the conveyor with perspective
    for i in range(0, screen_width, 20):  # Draw sections of the conveyor
        pygame.draw.rect(screen, CONVEYOR_COLOR, (i, conveyor_y, conveyor_width - (i // 20), conveyor_height))

    # Draw the sensor
    sensor_color = SENSOR_ACTIVE_COLOR if sensor_active else SENSOR_COLOR
    pygame.draw.rect(screen, sensor_color, sensor_rect)

    # Draw the boxes with shadow
    for box in boxes:
        draw_box_with_shadow(box)

    # Draw the robot arm as a simple rectangle
    pygame.draw.rect(screen, CONVEYOR_COLOR, (0, robot_arm_y, screen_width, 5))
    draw_rect_with_shadow(robot_arm_x - box_width / 2, robot_arm_y, robot_arm_width, robot_arm_height, ROBOT_ARM_COLOR, ROBOT_ARM_SHADOW_COLOR)

    draw_box_info()

    # Spawn new boxes every 1-4 seconds
    current_time = pygame.time.get_ticks()
    if current_time - spawn_timer >= spawn_interval and box_speed > 0:
        spawn(box_counter)
        spawn_timer = current_time
        spawn_interval = random.randint(500, 4000)  # Set a new random spawn interval
        
        box_counter += 1
        if box_counter > 999:
            box_counter = 1

    text_surface = logo_font.render("Z E U G W E R K", True, (42,51,75))
    screen.blit(text_surface, dest=text_surface.get_rect(center=(140, 580)))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
