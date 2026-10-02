

#------------------------------------------------------------------ 
# 
# THIS WAS MADE FROM AI TO TELL THE DIFFERENCE AND COMPARE
# 
#------------------------------------------------------------------ 

# Smart Rockets with Neuroevolution
# Same genetic algorithm as the original example, but the "DNA" is now the
# weights of a small neural network instead of a fixed list of force vectors.
#
# Each frame, a rocket's network SEES where the target is and how fast the
# rocket is moving, and DECIDES which way to fire its booster.
#
#   inputs  (4): dx to target, dy to target, velocity x, velocity y
#   hidden  (8): tanh neurons
#   outputs (2): force x, force y (tanh, scaled by MAX_FORCE)
#
# Because the rockets sense the target, a new target position each generation
# (or a mouse click mid-flight) doesn't break them - they learn a behaviour,
# not a path.
#
# Run:  pip install pygame   then   py smart_rockets_nn.py
# Click anywhere to move the target mid-generation.

import math
import random

import pygame
from pygame.math import Vector2

WIDTH, HEIGHT = 640, 360
FPS = 60

LIFESPAN = 250
POPULATION_SIZE = 100
MUTATION_RATE = 0.1   # Chance each weight is nudged
MUTATION_SIGMA = 0.3  # Size of the nudge (Gaussian)
MAX_FORCE = 0.1
MAX_SPEED = 4.0

N_IN, N_HIDDEN, N_OUT = 4, 8, 2
N_WEIGHTS = (N_IN + 1) * N_HIDDEN + (N_HIDDEN + 1) * N_OUT  # +1 = bias each


def random_target():
    return Vector2(random.uniform(40, WIDTH - 40), random.uniform(24, HEIGHT / 2))


class Brain:
    """A tiny feed-forward network. Its flat list of weights is the 'DNA'."""

    def __init__(self, weights=None):
        self.weights = weights if weights is not None else [
            random.uniform(-1, 1) for _ in range(N_WEIGHTS)
        ]

    def think(self, inputs):
        w = self.weights
        i = 0
        hidden = []
        for _ in range(N_HIDDEN):
            total = w[i + N_IN]  # bias
            for k in range(N_IN):
                total += w[i + k] * inputs[k]
            hidden.append(math.tanh(total))
            i += N_IN + 1
        outputs = []
        for _ in range(N_OUT):
            total = w[i + N_HIDDEN]  # bias
            for k in range(N_HIDDEN):
                total += w[i + k] * hidden[k]
            outputs.append(math.tanh(total))
            i += N_HIDDEN + 1
        return outputs

    def crossover(self, partner):
        # Uniform crossover: each weight comes from either parent
        child = [a if random.random() < 0.5 else b
                 for a, b in zip(self.weights, partner.weights)]
        return Brain(child)

    def mutate(self):
        for i in range(len(self.weights)):
            if random.random() < MUTATION_RATE:
                self.weights[i] += random.gauss(0, MUTATION_SIGMA)

    def copy(self):
        return Brain(list(self.weights))


class Rocket:
    def __init__(self, position, brain, elite=False):
        self.position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.brain = brain
        self.elite = elite
        self.fitness = 0.0
        self.finish_time = LIFESPAN
        self.record_dist = 1e9
        self.hit_target = False
        self.crashed = False

    def run(self, target, frame):
        if self.hit_target or self.crashed:
            return
        # SENSE: what does the rocket know about the world?
        to_target = target - self.position
        inputs = [
            to_target.x / WIDTH,
            to_target.y / HEIGHT,
            self.velocity.x / MAX_SPEED,
            self.velocity.y / MAX_SPEED,
        ]
        # DECIDE: the network picks a force
        fx, fy = self.brain.think(inputs)
        # ACT
        self.velocity += Vector2(fx, fy) * MAX_FORCE
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity

        d = self.position.distance_to(target)
        self.record_dist = min(self.record_dist, d)
        if d < 12:
            self.hit_target = True
            self.finish_time = max(frame, 1)
        elif not (0 <= self.position.x <= WIDTH and 0 <= self.position.y <= HEIGHT):
            self.crashed = True

    def calc_fitness(self):
        dist = max(self.record_dist, 1.0)
        self.fitness = (1.0 / (self.finish_time * dist)) ** 4
        if self.hit_target:
            self.fitness *= 2

    def show(self, surface):
        r = 4
        angle = math.atan2(self.velocity.y, self.velocity.x)
        local = [(r * 2, 0), (-r * 2, -r), (-r * 2, r)]
        c, s = math.cos(angle), math.sin(angle)
        pts = [(self.position.x + x * c - y * s, self.position.y + x * s + y * c)
               for x, y in local]
        fill = (110, 160, 255) if self.elite else (200, 200, 200)
        pygame.draw.polygon(surface, fill, pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 1)


class Population:
    def __init__(self):
        self.generations = 1
        self.start = Vector2(WIDTH / 2, HEIGHT - 20)
        self.rockets = [Rocket(self.start, Brain()) for _ in range(POPULATION_SIZE)]
        self.weights = []
        self.best_brain = None
        self.last_best_dist = None

    def live(self, target, frame, surface):
        for rocket in self.rockets:
            rocket.run(target, frame)
            rocket.show(surface)

    def fitness(self):
        for rocket in self.rockets:
            rocket.calc_fitness()
        best = max(self.rockets, key=lambda r: r.fitness)
        self.best_brain = best.brain
        self.last_best_dist = best.record_dist

    def selection(self):
        max_fit = max(r.fitness for r in self.rockets)
        self.weights = ([r.fitness / max_fit for r in self.rockets]
                        if max_fit > 0 else [1.0] * len(self.rockets))

    def reproduction(self):
        # Elitism: the best brain survives unchanged (drawn in blue)
        new_rockets = [Rocket(self.start, self.best_brain.copy(), elite=True)]
        while len(new_rockets) < POPULATION_SIZE:
            mom, dad = random.choices(self.rockets, weights=self.weights, k=2)
            child = mom.brain.crossover(dad.brain)
            child.mutate()
            new_rockets.append(Rocket(self.start, child))
        self.rockets = new_rockets
        self.generations += 1


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smart Rockets - Neuroevolution")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    target = random_target()
    population = Population()
    life_counter = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                target.update(event.pos)

        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (127, 127, 127), (int(target.x), int(target.y)), 12)
        pygame.draw.circle(screen, (0, 0, 0), (int(target.x), int(target.y)), 12, 2)

        if life_counter < LIFESPAN:
            population.live(target, life_counter, screen)
            life_counter += 1
        else:
            life_counter = 0
            population.fitness()
            population.selection()
            population.reproduction()
            target = random_target()  # New target every generation

        best = ("-" if population.last_best_dist is None
                else f"{population.last_best_dist:.0f}px")
        lines = [
            f"Generation #: {population.generations}",
            f"Cycles left: {LIFESPAN - life_counter}",
            f"Best distance last gen: {best}",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (0, 0, 0)), (10, 10 + i * 16))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()