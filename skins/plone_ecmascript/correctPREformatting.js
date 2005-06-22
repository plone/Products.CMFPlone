
function correctPREformatting(){
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

        // small utility thing to correct formatting for PRE-elements and some others
        // thanks to Michael Zeltner for CSS-guruness and research ;) 
		// currently not activated
        contentarea = getContentArea();
        if (! contentarea){return false}
        
        pres = contentarea.getElementsByTagName('pre');
        for (i=0;i<pres.length;i++){
           wrapNode(pres[i],'div','visualOverflow')
			}
               
        //tables = contentarea.getElementsByTagName('table');
        // for (i=0;i<tables.length;i++){
        //   if (tables[i].className=="listing"){
        //   wrapNode(tables[i],'div','visualOverflow')
		//  }
        //}      
}
//registerPloneFunction(correctPREformatting);
