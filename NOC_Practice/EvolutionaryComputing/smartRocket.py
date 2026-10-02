
# TO RUN THIS PROGRAM =>  pip install pygame & python smart_rockets.py
# Click anywhere to move the target; the population will adapt. 
# BUT DO KEEP IN MIND THAT THIS WILL TAKE A LOT OF TIME!!!!!

import math
import random
import pygame
from pygame.math import Vector2

WIDTH, HEIGHT = 640, 240
FPS = 60
# HOw long for each generation(by frames)
LIFESPAN = 250 #(Ideal are 250 to 350)
# The Standard Mutation rate.....        
MUTATION_RATE = 0.01  
POPULATION_SIZE = 50
# booster
MAX_FORCE = 0.1       


def random_force():
    """A random direction (like p5.Vector.random2D) with random magnitude."""
    angle = random.uniform(0, math.tau)
    return Vector2(math.cos(angle), math.sin(angle)) * random.uniform(0, MAX_FORCE)


class DNA:
    # One force vector per frame of life
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else [random_force() for _ in range(LIFESPAN)]
    
    # Take genees/a_part from self and the other part from partner and crossover them.
    def crossover(self, partner):
        mid = random.randrange(len(self.genes))
        child = [
            (self.genes[i] if i < mid else partner.genes[i]).copy()
            for i in range(len(self.genes))
        ]
        return DNA(child)
    
    def mutate(self, mutation_rate):
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] = random_force()


class Rocket:
    def __init__(self, position, dna):
        self.position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.dna = dna
        self.fitness = 0.0
        # REMEBER LEss frames to Finish = more better
        self.finish_time = LIFESPAN
        # Closest to the Target
        self.record_dist = 1e9         
        self.hit_target = False
    
    def apply_force(self, force):
        self.acceleration += force
    
    def check_target(self, target, frame):
        d = self.position.distance_to(target)
        self.record_dist = min(self.record_dist, d)
        if d < 12 and not self.hit_target:
            self.hit_target = True
            self.finish_time = max(frame, 1)
    
    def calc_fitness(self):
        # Gives them reward for getting close & fastASFuck!
        dist = max(self.record_dist, 1.0)
        self.fitness = (1.0 / (self.finish_time * dist)) ** 4
        if self.hit_target:
            # Bonus
            self.fitness *= 2  
    
    def run(self, target, frame):
        if not self.hit_target:
            self.apply_force(self.dna.genes[frame])
            self.update()
            self.check_target(target, frame)
    # Updates at each instance
    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
    
    # THis is for the dimentions for what the Rocket looks like.(i could'nt think of any shape so tringle is the Go to👍👍 if find a new shape then remember to make changes👍👍)
    def show(self, surface):
        r = 4
        angle = math.atan2(self.velocity.y, self.velocity.x)
        # Triangle pointing to velocity👍.
        local = [(r * 2, 0), (-r * 2, -r), (-r * 2, r)]
        c, s = math.cos(angle), math.sin(angle)
        points = [
            (self.position.x + x * c - y * s, self.position.y + x * s + y * c)
            for x, y in local
        ]
        pygame.draw.polygon(surface, (200, 200, 200), points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 1)


class Population:
    def __init__(self, mutation_rate, size):
        self.mutation_rate = mutation_rate
        self.generations = 1
        self.start = Vector2(WIDTH / 2, HEIGHT - 20)
        self.rockets = [Rocket(self.start, DNA()) for _ in range(size)]
        self.weights = []
    
    def live(self, target, frame, surface):
        for rocket in self.rockets:
            rocket.run(target, frame)
            rocket.show(surface)
    
    def fitness(self):
        for rocket in self.rockets:
            rocket.calc_fitness()
    
    def selection(self):
        # normalise fitness sscores
        # these are random choices, later pick rocket in propotion to weights👍.
        max_fit = max(r.fitness for r in self.rockets)
        if max_fit <= 0:
            self.weights = [1.0] * len(self.rockets)
        else:
            self.weights = [r.fitness / max_fit for r in self.rockets]
    
    def reproduction(self):
        new_rockets = []
        for _ in range(len(self.rockets)):
            mom, dad = random.choices(self.rockets, weights=self.weights, k=2)
            child_dna = mom.dna.crossover(dad.dna)
            child_dna.mutate(self.mutation_rate)
            new_rockets.append(Rocket(self.start, child_dna))
        self.rockets = new_rockets
        self.generations += 1




# THE MAIN STUFF THATS RUNNIGN👍
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smart Rockets")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)
    
    target = Vector2(WIDTH / 2, 24)
    population = Population(MUTATION_RATE, POPULATION_SIZE)
    life_counter = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Throw back to the update since the System is updating to the new position
                target.update(event.pos)
        
        # FILLING IT WITH WHITE🥵💦🥵💦🥵💦
        screen.fill((255, 255, 255))
        
        # THE CICLE (cuz i dont know what else the target could be)
        pygame.draw.circle(screen, (127, 127, 127), (int(target.x), int(target.y)), 12)
        pygame.draw.circle(screen, (0, 0, 0), (int(target.x), int(target.y)), 12, 2)
        
        if life_counter < LIFESPAN:
            # SOMEthing that i've most probbly forget but sinse it does/does'nt break the code. WE GOOD👍
            population.live(target, life_counter, screen)
            life_counter += 1
        else:
            #SAME AS ABOVE
            life_counter = 0
            population.fitness()
            population.selection()
            population.reproduction()
        
        # Display the stuff that is important👍
        lines = [
            f"Generation #: {population.generations}",
            f"Cycles left: {LIFESPAN - life_counter}",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (0, 0, 0)), (10, 10 + i * 16))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()