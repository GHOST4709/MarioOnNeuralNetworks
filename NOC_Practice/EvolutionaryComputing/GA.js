
let population = [];
class DNA{
    constructor(length){
        this.genes = [];
        for(let i=0;i<length;i++){
            this.genes[i] = randomCharacter();
        }
    }
}
function randomCharacter() {
    let c = floor(random(32,127));
    return String.fromCharCode(c);
}



