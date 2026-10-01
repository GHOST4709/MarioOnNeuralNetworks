
// let population = [];
class DNA{
    constructor(length){
        this.genes = [];
        
        this.fitness = 0;
        
        for(let i=0;i<length;i++){
            this.genes[i] = randomCharacter();
        }
        
        function calculateFitness(target){
            let score = 0;
            for(let i=0;i<this.genes.length;i++){
                if(this.genes[i] === target.charAt(i)){
                    score++;
                }
            }
            this.fitness = score/target.length;
        }
        
        function crossover(partner){
            let child = new DNA(this.genes.length);
            let midpoint = floor(random(this.genes.length));
            for(let i=0;i<this.genes.length;i++){
                if(i<midpoint){
                    child.genes[i] = this.genes[i];
                }else{
                    child.genes[i] = partner.genes[i];
                }
            }
            return child;
        }
        
        function mutate(mutationRate){
            for(let i=0;i<this.genes.length;i++){
                if(random(1)<mutationRate){
                    this.genes[i] = randomCharacter();
                }
            }
        }
    
    }
}

function randomCharacter() {
    let c = floor(random(32,127));
    return String.fromCharCode(c);
}
function draw(){
    for(let phase of population){
        phase.calculateFitness(target);
    }
}
function setup(){
    for(let i=0;i<100;i++){
        population[i] = new DNA(18);
    }
}
// ----------------------------------------
// THis was us deciding the mating POOL by picking larger fitness value/percentage individual.
let matingPool = [];
for(let phrase of population){
    let n=floor(phrase.fitness*100);
    for(let j=0;j<n;j++){
        matingPool.push(phrase);
    }
}
// ----------------------------------------
// Picking any 2 parents from the matin pool
let parentA = random(matingPool);
let parentB = random(matingPool);

// Yet another excellent alternative is worth exploring that similarly capitalizes on the principle of 
// fitness-proportionate selection. To understand how it works, imagine a relay race in which each member
// of the population runs a given distance tied to its fitness. The higher the fitness, the farther they run. 
// Let’s also assume that the fitness values have been normalized to all add up to 1 (just as with the wheel of fortune).
// The first step is to pick a starting line—a random distance from the finish. This distance is a random number from 0 to 1
function weightedSelection(){
    let index = 0;
    let start = random(1);
    while(start>0){
        start = start-population[index].fitness;
        index++;
    }
    index--;
    return population[index];
}

// ----------------------------------------
// Now for the mutation part!!!!
let child = parentA.crossover(parentB);
child.mutate();

//////--------------------------------------------------------------------------------
// FOR P5.js!!!!!!
// Mutation rate
let mutationRate = 0.01;
// Population Size
let populationSize = 150;

// Population array
let population = [];

// Target phrase
let target = "to be or not to be"; //Put anything here and see the magic happens!!!

function setup() {
  createCanvas(640, 240);
  //{!3} Step 1: Initialize Population
  for (let i = 0; i < populationSize; i++) {
    population[i] = new DNA(target.length);
  }
}

function draw() {
  // Step 2: Selection
  //{!3} Step 2a: Calculate fitness.
  for (let phrase of population) {
    phrase.calculateFitness(target);
  }

  // Step 2b: Build mating pool.
  let matingPool = [];

  for (let phrase of population) {
    //{!4} Add each member n times according to its fitness score.
    let n = floor(phrase.fitness * 100);
    for (let j = 0; j < n; j++) {
      matingPool.push(phrase);
    }
  }

  // Step 3: Reproduction
  for (let i = 0; i < population.length; i++) {
    let partnerA = random(matingPool);
    let partnerB = random(matingPool);
    // Step 3a: Crossover
    let child = partnerA.crossover(partnerB);
    // Step 3b: Mutation
    child.mutate(mutationRate);

    //{!1} Note that we are overwriting the population with the new
    // children.  When draw() loops, we will perform all the same
    // steps with the new population of children.
    population[i] = child;
  }

  let everything = "";
  for (let i = 0; i < population.length; i++) {
    everything += population[i].getPhrase() + "    ";
  }
  background(255);
  textFont("Courier");
  textSize(12);
  text(everything, 12, 0, width, height);
}