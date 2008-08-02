/* Mike Malloch's fixes for Internet Explorer 5 - 
 * We dont care too much about IE5,
 * But these stop if from spitting errormessages at the user 
 */
function hackPush(el){
    this[this.length] = el;
}

function hackPop(){
    var N = this.length - 1, el = this[N];
    this.length = N
    return el;
}

function hackShift(){
    var one = this[0], N = this.length;
    for (var i = 1; i < N; i++){
            this[i-1] = this[i];
    }
    this.length = N-1
    return one;
}

var testPushPop = new Array();
if (testPushPop.push){
}else{
    Array.prototype.push = hackPush
    Array.prototype.pop = hackPop
    Array.prototype.shift = hackShift;
}
