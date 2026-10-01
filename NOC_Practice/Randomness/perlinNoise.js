
// let x = random(0,width);
let x = noise(0,width);
circle(x,180,16);

let n = noise(3);
// let t = 3;
// function draw(){
    // let n = noise(t);
    // print(n);
// }
let t =0;
function draw(){
    let n = noise(t);
    print(n);
    t+=0.01; 
}


let walker;
function setup() {
  createCanvas(640, 240); // creating canvas of size 640 x 240
  walker = new Walker(); // creating an instance/object of class Walker
  background(255);
}

function draw() {
  walker.step();
  walker.show();
}

class Walker {
  constructor() {
    this.x = width / 2;
    this.y = height / 2;
    this.oldx = this.x;
    this.oldy = this.y;
    this.tx = 0;
    this.ty = 10000;
  }

  step() {
    this.x += map(noise(this.tx), 0, 1, -1, 1);
    this.y += map(noise(this.ty), 0, 1, -1, 1);

    this.tx += 0.01;
    this.ty += 0.01;
  }

  show() {
    stroke(0);
    line(this.oldx, this.oldy, this.x, this.y);
    this.oldx = this.x;
    this.oldy = this.y;
  }
}

