
// and finally : Mike Malloch's fixes for Internet Explorer 5 - 
// These should be considered temporary, as they actually add functionality to IE5, while we just want it to not blurt errormessages... 
//

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
        Array.prototype.shift =hackShift;
}

