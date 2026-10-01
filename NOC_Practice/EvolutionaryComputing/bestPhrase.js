let target;
let popmax;
let mutationRate;
let population;

let bestPhrase;
let allPhrases;
let stats;

function setup() {
    createCanvas(640, 240);
  //createCanvas(640, 360);
    target = "To be or not to be.";// Put anything here!!!!!
    popmax = 200;
    mutationRate = 0.01;
  // Create a population with a target phrase, mutation rate, and population max
    population = new Population(target, mutationRate, popmax);
}

function draw() {
  // Generate mating pool
    population.naturalSelection();
  //Create next generation
    population.generate();
  // Calculate fitness
    population.calcFitness();
    
    population.evaluate();
    
    // If we found the target phrase, stop
    if (population.isFinished()) {
    //println(millis()/1000.0);
    noLoop();
    }
    background(255);
    let answer = population.getBest();
    fill(0);
    textFont("Courier");
    textSize(12);
    text("Best phrase:", 10, 32);
    textSize(24);
    text(answer, 10, 64);
    let statstext =
    "total generations:     " + population.getGenerations() + "\n";
    statstext +=
    "average fitness:       " + nf(population.getAverageFitness(), 0, 2) + "\n";
    statstext += "total population:      " + popmax + "\n";
    statstext += "mutation rate:         " + floor(mutationRate * 100) + "%";
    
    textSize(12);
    text(statstext, 10, 96);
    textSize(8);
    text(population.allPhrases(), width / 2, 24);
    
}   