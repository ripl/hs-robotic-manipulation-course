import os
import random
import math
from pathlib import Path
from collections import deque
from typing import List
from pygame_arm import PygameArm

# import basic pygame modules
import pygame as pg
from pygame.math import Vector2

# game constants
SCREENRECT = pg.Rect(0, 0, 640, 480)
SCORE = 0

# --- New physics constants for the throw system ---
GRAVITY = 0.6                 # px/frame^2 applied to thrown helicopters
GRIPPER_HISTORY_LEN = 5       # how many frames of gripper motion to average for velocity
MIN_THROW_SPEED = 1.0         # below this speed, a "release" is treated as a drop, not a throw
SPAWN_POS = Vector2(800, 160) # where a helicopter respawns after leaving the screen

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


def load_sound(file):
    """because pygame can be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print(f"Warning, unable to load, {file}")
    return None


class Joint(pg.sprite.Sprite):
    # shoulder 71x23
    #
    def __init__(self, pos=(100, 240), image="shoulder.png", size=3.0, pivot=(88, -2), length=180):
        super().__init__()
        self.image = pg.image.load(image).convert_alpha()
        self.image = pg.transform.scale_by(self.image, size)
        # self.image = pg.Surface(size, pg.SRCALPHA)
        # pg.draw.polygon(self.image, pg.Color('dodgerblue1'),
        # ((1, 0), (120, 35), (1, 70)))
        # A reference to the original image to preserve the quality.
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)  # The original center position/pivot point.
        self.offset = Vector2(pivot[0], pivot[1])  # We shift the sprite 50 px to the right.
        self.length = length
        self.tan_length = length
        self.angle = 0

    def update(self):
        self.rotate()

    def set_rot(self, angle=0):
        self.angle = angle

    def change_rot(self, angle=0):
        self.angle += angle

    def get_tip(self):
        distance_to_tip = self.length

        # Calculate the X and Y offsets using trigonometry
        tip_x = self.pos.x + math.cos(-self.angle / 57.92) * distance_to_tip
        tip_y = self.pos.y - math.sin(-self.angle / 57.92) * distance_to_tip

        return (tip_x, tip_y)

    def rotate(self):
        """Rotate the image of the sprite around a pivot point."""
        # Rotate the image.
        self.image = pg.transform.rotozoom(self.orig_image, -self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos + offset_rotated)

    def update_pos(self, pos):
        self.pos = pos


class Helicopter(pg.sprite.Sprite):
    def __init__(self, pos, claw, image="./sprites/helicopter.png"):
        super().__init__()
        self.image = pg.image.load(image).convert_alpha()
        self.image = pg.transform.scale_by(self.image, 3.0)
        self.orig_image = self.image
        self.angle = -10
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.claw = claw

        # --- Grab / throw state ---
        self.grabbed = False        # currently held by the claw
        self.thrown = False         # currently in free flight after being released
        self.velocity = Vector2(0, 0)  # px/frame velocity while thrown
        self.spin_speed = 0.0       # cosmetic spin while thrown, derived from throw speed

        # Reference values captured at the instant of grab, used to hold the
        # helicopter at a fixed offset/orientation relative to the claw
        # rather than snapping it onto the claw's own center.
        self.grab_offset = Vector2(0, 0)  # heli position relative to claw center, at grab time
        self.grab_claw_angle = 0.0        # claw's angle at grab time
        self.grab_heli_angle = 0.0        # heli's own angle at grab time

    def rotate(self):
        """Rotate the image of the sprite around a pivot point."""
        # Rotate the image.
        self.image = pg.transform.rotozoom(self.orig_image, -self.angle, 1)
        self.rect = self.image.get_rect(center=self.pos)

    def throw(self, velocity: Vector2):
        """Release the helicopter from the claw and launch it with the given velocity."""
        self.grabbed = False
        self.thrown = True
        self.velocity = Vector2(velocity)
        # Faster throws spin faster - purely cosmetic.
        self.spin_speed = max(-37.5, min(37.5, velocity.x * 1.5))

    def grab(self):
        """Attach the helicopter to the claw, keeping it exactly where it
        currently is instead of snapping it onto the claw's center. Its
        position/angle at this moment become a fixed offset from the claw;
        as the claw's angle changes from here, that offset rotates with it,
        so the helicopter swings around the claw's pivot rather than
        popping to match it."""
        self.grabbed = True
        self.thrown = False
        self.grab_offset = self.pos - Vector2(self.claw.rect.center)
        self.grab_claw_angle = self.claw.angle
        self.grab_heli_angle = self.angle

    def respawn(self):
        """Reset the helicopter back to its starting state, off the right edge of the screen."""
        self.pos = Vector2(SPAWN_POS)
        self.rect = self.image.get_rect(center=self.pos)
        self.grabbed = False
        self.thrown = False
        self.velocity = Vector2(0, 0)
        self.angle = -10

    def update(self):
        if self.grabbed:
            # Stay at the fixed offset/angle captured at grab time, rotated
            # by however much the claw's angle has changed since then. At
            # the moment of grab that delta is zero, so there's no pop -
            # the helicopter just starts swinging around the claw's pivot
            # from wherever it was caught.
            delta_angle = self.claw.angle - self.grab_claw_angle
            self.pos = Vector2(self.claw.rect.center) + self.grab_offset.rotate(delta_angle)
            self.rect.center = self.pos
            self.angle = self.grab_heli_angle + delta_angle

        elif self.thrown:
            # Simple projectile motion: gravity pulls it down, it keeps its
            # horizontal/vertical momentum from the moment of release.
            self.velocity.y += GRAVITY
            self.pos += self.velocity
            self.rect.center = self.pos
            self.angle += self.spin_speed

            # Once it leaves the play area, send it back to start so the
            # player can grab another one.
            if not SCREENRECT.inflate(200, 200).colliderect(self.rect):
                self.respawn()

        else:
            # Idle behavior: drift left, same as the original game.
            self.pos -= Vector2(3, 0)
            self.rect.center = self.pos
            if self.pos.x < SCREENRECT.left - 100:
                self.respawn()

        self.rotate()


def main(winstyle=0):
    file_path = Path(__file__).resolve()
    robotics = file_path.parents[1] / "robotics"
    sprites_path = file_path.parent / "sprites"

    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()
    shoulder = Joint(image=str(sprites_path / "shoulder.png"), pos=(134, 440))
    forearm = Joint(image=str(sprites_path / "forearm.png"), pivot=(64, 0), length=128)
    wrist = Joint(image=str(sprites_path / "wrist.png"), pivot=(28, 2), length=100)
    static_gripper = Joint(image=str(sprites_path / "static_gripper.png"), pivot=(0, 16), length=0)
    dynamic_gripper = Joint(image=str(sprites_path / "dynamic_gripper.png"), pivot=(-20, 30))

    helicopter = Helicopter(Vector2(800, 160), claw=dynamic_gripper, image=str(sprites_path / "helicopter.png"))

    joints = [shoulder, forearm, wrist, static_gripper]
    servos = [2, 3, 4, 6]
    signs = [0.5, -0.5, -0.5, 1.0]
    offsets = [90, 185, 180, 0]

    all_sprites = pg.sprite.Group(joints, dynamic_gripper, dynamic_gripper, helicopter)
    helicopters = pg.sprite.Group(helicopter)

    bg_original = pg.image.load(str(sprites_path / "background.png")).convert()
    background = pg.transform.scale(bg_original, (640, 480))

    arm = PygameArm(leader=False, claw=6, config_path = str(robotics / "config.json"))

    # --- Gripper velocity tracking, used to compute throw speed on release ---
    gripper_positions = deque(maxlen=GRIPPER_HISTORY_LEN)
    claw_was_closed = False

    while True:
        # Quit Logic
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        """
        Old Movement Stuff
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            shoulder.pos.x += 5
        elif keys[pg.K_a]:
            shoulder.pos.x -= 5
        """

        # Joint Kinematics
        for i in range(0, len(joints) - 1):
            angle = arm.get_positions()[servos[i]]
            angle *= signs[i] * 360 / 2048
            angle += offsets[i]
            joints[i].set_rot(angle)

            joints[i + 1].pos.x = joints[i].get_tip()[0]
            joints[i + 1].pos.y = joints[i].get_tip()[1]

        # Claw points same direction as the forearm
        ang = joints[2].angle - 90
        joints[3].set_rot(ang)

        # Dynamic Gripper Movement
        dynamic_gripper.pos = joints[3].pos
        dynamic_gripper.set_rot((arm.get_position(6) / 10) + ang + 160)
        dynamic_gripper.rotate()  # make sure rect is current before we sample it below

        # --- Track gripper velocity over the last few frames ---
        gripper_positions.append(Vector2(dynamic_gripper.rect.center))
        if len(gripper_positions) >= 2:
            span = len(gripper_positions) - 1
            gripper_velocity = 1.5 * (gripper_positions[-1] - gripper_positions[0]) / span
        else:
            gripper_velocity = Vector2(0, 0)

        claw_closed = arm.is_claw_closed()

        # Collision Checks
        # Detect collisions between claw and helicopter -> pick up
        for heli in pg.sprite.spritecollide(dynamic_gripper, helicopters, 0):
            if claw_closed and not claw_was_closed and not heli.grabbed:
                heli.grab()

        # Release logic: any helicopter currently held goes airborne the
        # instant the claw opens, launched with the gripper's recent velocity.
        if claw_was_closed and not claw_closed:
            for heli in helicopters:
                if heli.grabbed:
                    throw_velocity = gripper_velocity if gripper_velocity.length() >= MIN_THROW_SPEED else Vector2(0, 0)
                    heli.throw(throw_velocity)

        claw_was_closed = claw_closed

        all_sprites.update()
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        """
        for link in joints:
            pg.draw.circle(screen, (255, 128, 0), [int(i) for i in link.pos], 3)
            pg.draw.rect(screen, (255, 128, 0), link.rect, 2)
            pg.draw.line(screen, (100, 200, 255), (0, 240), (640, 240), 1)
        """
        pg.display.flip()
        clock.tick(30)


# Call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()