import math
import random
import pygame
from pygame.math import Vector2

# -----------------------------------------------------------------------------------------------------------------------
# MOST OF THE stuf is same except the Obstacle Class and Also i changed the target from cicle to square, just for FUN!!!
# -----------------------------------------------------------------------------------------------------------------------

WIDTH, HEIGHT = 640, 240
FPS = 60
LIFESPAN = 250          
MUTATION_RATE = 0.01    
POPULATION_SIZE = 150
MAX_FORCE = 0.1        

def random_force():
    angle = random.uniform(0, math.tau)
    return Vector2(math.cos(angle), math.sin(angle)) * random.uniform(0, MAX_FORCE)

class Obstacle:
    # THE OBstacle that is rectangle in shape(cuz i don'nt know what other shape will be good (other tha cicle))
    def __init__(self, x, y, w, h):
        self.position = Vector2(x, y)
        self.w = w
        self.h = h
    
    @property
    def center(self):
        return Vector2(self.position.x + self.w / 2, self.position.y + self.h / 2)
    
    def contains(self, p):
        return (self.position.x < p.x < self.position.x + self.w and
                self.position.y < p.y < self.position.y + self.h)
    
    def show(self, surface):
        rect = pygame.Rect(self.position.x, self.position.y, self.w, self.h)
        pygame.draw.rect(surface, (175, 175, 175), rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)


class DNA:
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else [random_force() for _ in range(LIFESPAN)]
    
    def crossover(self, partner):
        mid = random.randrange(len(self.genes))
        child = [(self.genes[i] if i < mid else partner.genes[i]).copy()
                    for i in range(len(self.genes))]
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
        self.gene_counter = 0
        self.fitness = 0.0
        self.record_dist = 10000.0   
        self.finish_time = 0         
        self.hit_obstacle = False
        self.hit_target = False
    
    def check_target(self, target):
        d = self.position.distance_to(target.center)
        self.record_dist = min(self.record_dist, d)
        
        if target.contains(self.position) and not self.hit_target:
            self.hit_target = True
        elif not self.hit_target:
            self.finish_time += 1
    
    def calc_fitness(self):
        dist = self.record_dist
        if dist < 12:
            dist = 1.0  
        self.fitness = (1.0 / (max(self.finish_time, 1) * dist)) ** 4
        
        if self.hit_obstacle:
            # Lose 90% of fitness for hitting an obstacle
            self.fitness *= 0.1   
        if self.hit_target:
            # Double the fitness for reaching the target
            self.fitness *= 2    
    
    def run(self, obstacles, target):
        self.check_target(target)
        
        if not self.hit_obstacle and not self.hit_target:
            self.apply_force(self.dna.genes[self.gene_counter])
            self.gene_counter = (self.gene_counter + 1) % len(self.dna.genes)
            self.update()
            self.check_obstacles(obstacles)
    
    def check_obstacles(self, obstacles):
        # walls of the window count as obstacles too cuz why not
        p = self.position
        if p.x < 1 or p.x > WIDTH - 1 or p.y < 1 or p.y > HEIGHT - 1:
            self.hit_obstacle = True
            return
        for obs in obstacles:
            if obs.contains(p):
                self.hit_obstacle = True
                return
    
    def apply_force(self, force):
        self.acceleration += force
    
    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
    
    def show(self, surface):
        r = 4
        angle = math.atan2(self.velocity.y, self.velocity.x)
        local = [(r * 2, 0), (-r * 2, -r), (-r * 2, r)]
        c, s = math.cos(angle), math.sin(angle)
        pts = [(self.position.x + x * c - y * s, self.position.y + x * s + y * c)
                    for x, y in local]
        pygame.draw.polygon(surface, (200, 200, 200), pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 1)

class Population:
    def __init__(self, mutation_rate, size):
        self.mutation_rate = mutation_rate
        self.generations = 1
        self.start = Vector2(WIDTH / 2, HEIGHT - 20)
        self.rockets = [Rocket(self.start, DNA()) for _ in range(size)]
        self.weights = []
    
    def live(self, obstacles, target, surface):
        for rocket in self.rockets:
            rocket.run(obstacles, target)
            if not rocket.hit_obstacle:  # Crashed rockets disappear
                rocket.show(surface)
    
    def target_reached(self):
        return any(r.hit_target for r in self.rockets)
    
    def calculate_fitness(self):
        for rocket in self.rockets:
            rocket.calc_fitness()
    
    def selection(self):
        # Fitness-proportionate selection: normalise fitness to 0..1;
        # random.choices later uses these as weights
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smart Rockets - Obstacles")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)
    
    life_counter = 0
    record_time = LIFESPAN  # Fastest time to target
    
    target = Obstacle(WIDTH / 2 - 12, 24, 24, 24)
    population = Population(MUTATION_RATE, POPULATION_SIZE)
    
    # The obstacle course
    obstacles = [Obstacle(WIDTH / 2 - 75, HEIGHT / 2, 150, 10)]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Move the target
                target.position.update(event.pos[0] - target.w / 2,
                                        event.pos[1] - target.h / 2)
                record_time = LIFESPAN
        
        screen.fill((255, 255, 255))
        target.show(screen)
        
        if life_counter < LIFESPAN:
            population.live(obstacles, target, screen)
            if population.target_reached() and life_counter < record_time:
                record_time = life_counter
            else:
                life_counter += 1
        else:
            life_counter = 0
            population.calculate_fitness()
            population.selection()
            population.reproduction()
        
        for obs in obstacles:
            obs.show(screen)
        
        lines = [
            f"Generation #: {population.generations}",
            f"Cycles left: {LIFESPAN - life_counter}",
            f"Record cycles: {record_time}",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (0, 0, 0)), (10, 8 + i * 18))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    
if __name__ == "__main__":
    main()