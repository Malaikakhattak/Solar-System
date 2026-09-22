import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# -------------------
# CONFIG & DATA
# -------------------
WIDTH, HEIGHT = 1000, 750
angle_orbit = 0
angle_spin = 0 
moon_orbit = 0
asteroid_rot = 0 

stars = []
asteroids = []
nebula_clouds = []

def generate_universe():
    # Stars: Multi-colored palette 
    for _ in range(2500):
        stars.append({
            "pos": (random.uniform(-1500, 1500), random.uniform(-1500, 1500), random.uniform(-1500, 1500)),
            "color": random.choice([(1.0, 1.0, 1.0), (0.4, 0.8, 1.0), (1.0, 1.0, 0.4), (1.0, 0.4, 0.4)]),
            "flicker": random.uniform(0.5, 2.5),
            "size": random.uniform(1.5, 3.0) 
        })
    
    # Stony Layer: Asteroid Belt
    for _ in range(1500):
        dist = random.uniform(215, 245)
        ang = random.uniform(0, 2 * math.pi)
        asteroids.append({
            "dist": dist, "angle": ang, "y": random.uniform(-5, 5),
            "color": random.choice([(0.4, 0.35, 0.3), (0.3, 0.3, 0.3), (0.5, 0.45, 0.4)])
        })
    
    # Nebula: Deep space violets and teals
    neb_palette = [(0.0, 0.4, 0.5, 0.1), (0.4, 0.1, 0.6, 0.08), (0.1, 0.1, 0.3, 0.15)]
    for _ in range(180):
        ra = random.uniform(800, 1300)
        u, v = random.random(), random.random()
        theta, phi = 2 * math.pi * u, math.acos(2 * v - 1)
        nx, ny, nz = ra * math.sin(phi) * math.cos(theta), ra * math.sin(phi) * math.sin(theta), ra * math.cos(phi)
        nebula_clouds.append({"pos": (nx, ny, nz), "size": random.uniform(300, 700), "color": random.choice(neb_palette)})

def draw_background(t):
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    for n in nebula_clouds:
        glPushMatrix(); glTranslatef(*n["pos"]); glBegin(GL_TRIANGLE_FAN)
        glColor4f(*n["color"]); glVertex3f(0, 0, 0); glColor4f(0, 0, 0, 0)
        for i in range(10):
            a = i * (2 * math.pi / 9); glVertex3f(math.cos(a)*n["size"], math.sin(a)*n["size"], 0)
        glEnd(); glPopMatrix()

    # Crisp Multi-colored Stars
    for s in stars:
        f = (math.sin(t * s["flicker"]) + 1.5) / 2.5
        glPointSize(s["size"])
        glBegin(GL_POINTS)
        glColor4f(s["color"][0], s["color"][1], s["color"][2], 0.9 * f)
        glVertex3f(*s["pos"])
        glEnd()
    
    # Stony Layer
    glPointSize(2.5)
    glBegin(GL_POINTS)
    for a in asteroids:
        glColor3f(*a["color"])
        cur_ang = a["angle"] + asteroid_rot
        glVertex3f(a["dist"] * math.cos(cur_ang), a["y"], a["dist"] * math.sin(cur_ang))
    glEnd()

    glDisable(GL_POINT_SMOOTH)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)

def draw_body(radius, color, s_speed, is_sun=False, has_rings=False):
    glPushMatrix()
    glRotatef(angle_spin * s_speed, 0, 1, 0)
    
    if is_sun:
        glDisable(GL_LIGHTING); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor3f(1.0, 1.0, 0.95); gluSphere(gluNewQuadric(), radius, 50, 50) 
        glow_colors = [(1.0, 0.8, 0.0, 0.2), (1.0, 0.4, 0.0, 0.1), (0.8, 0.0, 0.4, 0.05)]
        for i, (r, g, b, a) in enumerate(glow_colors):
            p = math.sin(pygame.time.get_ticks() * 0.005) * (i * 0.5)
            glColor4f(r, g, b, a)
            gluSphere(gluNewQuadric(), radius + (i * 4.0) + p, 32, 32)
        glDisable(GL_BLEND); glEnable(GL_LIGHTING)
    else:
        glRotatef(23, 0, 0, 1); glColor3f(*color)
        gluSphere(gluNewQuadric(), radius, 40, 40)
        # Atmosphere
        glDisable(GL_LIGHTING); glEnable(GL_BLEND)
        glColor4f(color[0], color[1], color[2], 0.25)
        gluSphere(gluNewQuadric(), radius * 1.15, 30, 30)
        glDisable(GL_BLEND); glEnable(GL_LIGHTING)

    if has_rings:
        # LIGHT PURPLE RINGS
        glDisable(GL_CULL_FACE); glEnable(GL_BLEND); glColor4f(0.8, 0.6, 1.0, 0.4)
        glBegin(GL_QUAD_STRIP)
        for i in range(101):
            a = i * (2 * math.pi / 100)
            glVertex3f(math.cos(a)*(radius+3.5), 0, math.sin(a)*(radius+3.5))
            glVertex3f(math.cos(a)*(radius+9.5), 0, math.sin(a)*(radius+9.5))
        glEnd(); glDisable(GL_BLEND)
    glPopMatrix()

def draw_label(x, y, text, font):
    # WHITE TEXT
    surf = font.render(text, True, (255, 255, 255))
    data = pygame.image.tostring(surf, "RGBA", True)
    w, h = surf.get_size()
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glRasterPos2i(x, y); glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def project_label(x, y, z):
    m, p, v = glGetDoublev(GL_MODELVIEW_MATRIX), glGetDoublev(GL_PROJECTION_MATRIX), glGetIntegerv(GL_VIEWPORT)
    try:
        win = gluProject(x, y, z, m, p, v)
        return int(win[0]), int(v[3] - win[1])
    except: return None

def main():
    global angle_orbit, angle_spin, moon_orbit, asteroid_rot
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Neon Solar System")
    font = pygame.font.SysFont("Impact", 13)

    glMatrixMode(GL_PROJECTION); gluPerspective(45, WIDTH/HEIGHT, 0.1, 7000.0); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 0, 1))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.08, 0.08, 0.12, 1.0])

    generate_universe()
    cam_dist, cam_yaw = -700, 0
    clock = pygame.time.Clock()

    while True:
        t = pygame.time.get_ticks() / 1000
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); return

        keys = pygame.key.get_pressed()
        if keys[K_UP]: cam_dist += 10
        if keys[K_DOWN]: cam_dist -= 10
        if keys[K_LEFT]: cam_yaw += 2.5
        if keys[K_RIGHT]: cam_yaw -= 2.5

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); glLoadIdentity()
        glTranslatef(0, -80, cam_dist); glRotatef(35, 1, 0, 0); glRotatef(cam_yaw, 0, 1, 0)

        draw_background(t)
        draw_body(28, (1, 1, 1), 0.3, is_sun=True)
        label_list = [("SUN", 0, 50, 0)]

        planets = [
            ("Mercury", 75, 1.6, 0.2, 2.5, (0.7, 0.7, 0.9), False),
            ("Venus", 110, 1.2, 0.1, 3.8, (1.0, 0.8, 0.3), False),
            ("Earth", 160, 1.0, 1.0, 4.5, (0.0, 0.8, 1.0), False),
            ("Mars", 210, 0.8, 0.9, 3.2, (1.0, 0.2, 0.1), False),
            ("Jupiter", 340, 0.5, 2.5, 15.0, (1.0, 0.6, 0.3), False),
            ("Saturn", 460, 0.3, 2.2, 13.0, (0.9, 0.8, 0.5), True),
            ("Uranus", 570, 0.2, 1.5, 8.0, (0.3, 1.0, 0.8), False),
            ("Neptune", 660, 0.15, 1.6, 8.0, (0.2, 0.4, 1.0), False)
        ]

        for name, dist, o_spd, s_spd, size, col, rings in planets:
            # Subtle Orbits
            glDisable(GL_LIGHTING); glColor4f(0.0, 1.0, 1.0, 0.12)
            glBegin(GL_LINE_LOOP)
            for i in range(150):
                a = i * (2 * math.pi / 150); glVertex3f(dist * math.cos(a), 0, dist * math.sin(a))
            glEnd(); glEnable(GL_LIGHTING)

            px, pz = dist * math.cos(angle_orbit * o_spd), dist * math.sin(angle_orbit * o_spd)
            glPushMatrix(); glTranslatef(px, 0, pz)
            if name == "Earth":
                glPushMatrix(); glRotatef(moon_orbit, 0, 1, 0); glTranslatef(12, 0, 0)
                draw_body(1.1, (0.9, 0.9, 1.0), 0.2); glPopMatrix()
            draw_body(size, col, s_spd, has_rings=rings); glPopMatrix()
            label_list.append((name, px, size + 12, pz))

        for name, lx, ly, lz in label_list:
            pos = project_label(lx, ly, lz)
            if pos: draw_label(pos[0], pos[1], name, font)

        angle_orbit += 0.0025
        angle_spin += 0.5
        moon_orbit += 2.5
        asteroid_rot += 0.0006 
        
        pygame.display.flip(); clock.tick(60)

if __name__ == "__main__":
    main()