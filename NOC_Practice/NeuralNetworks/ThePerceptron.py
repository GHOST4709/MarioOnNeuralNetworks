import random
import numpy as np
import pygame

class Perceptron:
    def __init__(self,n,lr):
        self.lr = lr
        self.weights = [random.uniform(-1,1) for _ in range(n) ]
    
    def feedForward(self,inputs):
        sum = 0
        for i in range(len(self.weights)):
            sum+= inputs[i]*self.weights[i]
        return 1 if sum > 0 else -1
    
    def train(self,inputs,desired):
        guess = self.feedForward(inputs)
        error = desired-guess
        for i in range(len(self.weights)):
            self.weights[i] += error * inputs[i] * self.lr


WIDTH , HEIGHT = 640,240
def f(x):
    return 0.5 * x+1

training = []
for _ in range(2000):
    x= random.uniform(-WIDTH/2 , WIDTH/2)
    y= random.uniform(-HEIGHT/2 , HEIGHT/2)
    training.append([x,y,1])
perceptron = Perceptron(3,0.0001) # or just use 0.001

count=0
def step():
    global count
    x,y,_ = training[count]
    desired = 1 if y>f(x) else -1
    perceptron.train(training[count], desired)
    count = (count + 1) % len(training)



def to_screen(x,y):
    return int(x+WIDTH/2) , int(HEIGHT/2-y)

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Perceptron")
clock = pygame.time.Clock()

running =  True

while running:
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    
    screen.fill((255, 255, 255))
    
    start_pos = to_screen(-WIDTH/2, f(-WIDTH/2))
    end_pos = to_screen(WIDTH/2, f(WIDTH/2))
    pygame.draw.line(screen, (0, 0, 0), start_pos, end_pos, 2)
    
    for _ in range(10):
        step()
    
    for pt in training:
        guess = perceptron.feedForward(pt)
        fill_color = (127, 127, 127) if guess > 0 else (255, 255, 255)
        pos = to_screen(pt[0], pt[1])
        pygame.draw.circle(screen, fill_color, pos, 4)
        pygame.draw.circle(screen, (0, 0, 0), pos, 4, 1)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()