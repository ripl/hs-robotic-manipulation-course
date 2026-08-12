# Attack of the Clones

<div class="module-summary" markdown>
**Goal:** Students extend sprite-based Pygame work into a hero, enemy, and collectible game.

**Duration:** 1-2 class hours.

**Prerequisites:** Race for the Treasure or equivalent Pygame sprite experience.
</div>

## Overview

The curriculum draft introduces Attack of the Clones after Race for the Treasure. It uses the same core Pygame ideas: sprites, keyboard movement, rectangular collision checks, score/state updates, and win/loss conditions.

Students make or choose three transparent PNG assets:

- Hero.
- Villain or clone.
- Collectible.

## Learning Objectives

- Reuse the sprite movement structure from a prior game.
- Separate hero, enemy, and collectible roles.
- Track game state over time.
- Design additional rules beyond simple two-player racing.
- Refactor repeated sprite behavior into helper functions or classes.

## Suggested Extension Rules

The draft can be taught as a design extension. Useful rule options:

- The hero collects items while avoiding clones.
- Clones move randomly or follow the hero.
- The player wins after collecting a target number of items.
- The player loses after a collision with a clone.
- More clones appear as the score increases.

## Continuity

Attack of the Clones is a good bridge from guided game implementation to student-designed projects. It also gives a natural reason to introduce classes: each moving object can remember its image, rectangle, speed, and behavior.

## Repository Code

- Pygame examples and assets: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/python/2025_ARM>
