//*****************************************************************************
// Filename: sortTable.js
// Description: This javascript file can be applied to convert record tables
// in a HTML file to be client-side sortable by associating title columns with
// sort events. 
//
// COPYRIGHT (C) 2001 HAN J. YU, LIPING DAI 
// THIS PROGRAM IS FREE SOFTWARE; YOU CAN REDISTRIBUTE IT AND/OR MODIFY IT 
// UNDER THE TERMS OF THE GNU GENERAL PUBLIC LICENSE AS PUBLISHED BY THE FREE 
// SOFTWARE FOUNDATION; EITHER VERSION 2 OF THE LICENSE, OR (AT YOUR OPTION) 
// ANY LATER VERSION. THIS PROGRAM IS DISTRIBUTED IN THE HOPE THAT IT WILL BE 
// USEFUL, BUT WITHOUT ANY WARRANTY; WITHOUT EVEN THE IMPLIED WARRANTY OF 
// MERCHANTABILITY OF FITNESS FOR A PARTICULAR PURPOSE. SEE THE GNU GENERAL 
// PUBLIC LICENSE FOR MORE DETAILS. 
//
// YOU SHOULD HAVE RECEIVED A COPY OF THE GNU GENERAL PUBLIC LICENSE ALONG 
// WITH THIS PROGRAM; IF NOT, WRITE TO: 
//
// THE FREE SOFTWARE FOUNDATION, INC., 
// 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA 
//
// Bugs/Comments: han@velocityhsi.com
//
// Change History:
//
// 11-26-01: 
//	o Made a few more settings configurable (i.e. data delimiter etc).
//	o Added a check for the browser type/version (>= IE 5.0 allowed).
// 11-27-01:
//	o Used document.getElementById method to retrieve object
//	o Now supports both IE 5.0 or greater and Netscape 6.0 or greater
// 11-28-01:
//	o Fixed the status display for Netscape.
//	o Fixed the cursor shape for Netscape. Used pointer instead of hand.
// 11-29-01:
//	o Fixed a cursor bug for IE 5.5
// 12-03-01:
//	o Uses delete/insert cell when doing the sort.
//	o Uses delete/insert cell for the title.
// 12-04-01:
//	o Created redrawTitle function to tidy things up a bit.
// 12-09-01:
//	o Used the innerMost cell's nodeValue to display title name.
// 12-10-01:
//	o Now preserves the align property of the title cell.
//	o Allows to have multiple child nodes inside the title cell.
//	o Simulates <TH> by centeing and bold-facing title cell contents.
// 01-21-02: (Thanks to Ric Shumack ...)
//	o Added one more condition for table init call (table.tainted == false)
//	o Used the preferred method for checking the browser version
//*****************************************************************************

//*****************************************************************************
// sortTable.js
//
// This script contains useful functions that can be used to convert ordinary
// tables into sortable tables by modifying the HTML sources.
// 
// Here is how one can do that. The following assumptions are required
// for the tables to be sorted.
//
// 1. All the record columns must be the same lengh. Otherwise (i.e. the ones
//    that contain colspan) the rows will be ignored. 
//
// 2. Row spans can not happen in the record rows though column spans
//    can be one of the record rows.
//
// 3. Row-spanned single column will be considered as title.
//
// To enable the sorting, simply include this javascript source file and
// add an onLoad event to the <body> like below:
//
// <body onLoad='initTable("table1");initTable("table2");' ...>
//
// Note that all the tables that need to be sorted MUST contain ID tag. 
// So, if they do not exist, you must create one for each table that
// needs to be sorted. Also, the table names/ids MUST BE UNIQUE.
//*****************************************************************************

// Global variables
var table;				// Table object
var tableId;				// Current Table ID
var rowArray = new Array();		// Data row array
var titleRowArray = new Array();	// Contains row pointer for titles
var titleInnerHTMLArray = new Array();	// Contains innerHTML for title cells
var titleSpanCountArray = new Array();	// Contains the row-span count
var titleRowCellArray = new Array();	// Dynamically constructed title cells
var titleSpanCellArray = new Array();	// Title elelments from row-spanned
var colSpanArray = new Array();		// Rows col-spanned
var colTitleFilled = new Array();	// Indicates whether title is filled
var sortIndex;				// Selected index for sort
var descending = false;			// Descending order
var nRow, actualNRow, maxNCol;		// Various table stats
var origColor;				// Holds original default color
var isIE;				// True if IE
var linkEventString =			// What's insider <a> tag
	'onMouseOver=\'setCursor(this);' +
	'setColor(this,"selected");\' ' +
	'onMouseOut=\'setColor(this,"default");\' ' +
	'onClick=\'sortTable(';

// Configurable constants
var ascChr = "<img src=\"img/arrowUp.gif\" alt=\"^\">";			// Symbol for ascending sort
var desChr = "<img src=\"img/arrowDown.gif\" alt=\"v\">";			// Symbol for descending sort
var selectedColor = "blue";		// Color for sort focus
var defaultColor = "black";		// Default color for sort off-focus
var recDelimiter = '|';			// Char used as a record separator
var updownColor = 'gray';		// Specified the color for up/downs 

//*****************************************************************************
// Main function. This is to be associated with onLoad event in <BODY>. 
//
// IMPORTANT: This is the only function that needs to be included in the pages
// to be sorted. The rest of the functions are simply called by this
// function.
//*****************************************************************************
function initTable(obj)
{
	// Check whether it's viewed by IE 5.0 or greater
	if (! checkBrowser()) return;

	// Local variables
	var countCol;
	var currentCell;
	var nColSpan, nRowSpannedTitleCol, colPos;
	var titleFound = false;
	var rNRowSpan, rNColSpan;

	// Initializing global table object variable
	if (obj.tagName == "TABLE")
	{
		// Assumes that the obj is THE OBJECT
		table = obj;
	}
	else
	{
		// Assumes that the obj is the id of the object
		table = document.getElementById(obj);
	}

	// Check whether it's an object
	if (table == null) return;

	// Check whether it's a table
	if (table.tagName != "TABLE") return;

	// No need to re-init if it's already done
	if (tableId == table.id && table.tainted == false) return;

	// Setting table id
	tableId = table.id;

	// Initializing the max col number with the size of last data row
	maxNCol = table.rows[table.rows.length-1].cells.length;

	// Initializing arrays
	rowArray = new Array();
	colSpanArray = new Array();
	colTitleFilled = new Array();
	titleRowArray = new Array();
	titleInnerHTMLArray = new Array();
	titleSpanCountArray = new Array();
	titleRowCellArray = new Array();
	
	for (var i=0; i<maxNCol; i++)
		colTitleFilled[i] = false;

	// Setting the number of rows
	nRow = table.rows.length;	

	// Should have at least 1 row
	if (nRow < 1) return;

	// Initialization of local variables
	actualNRow = 0;			// Number of actual data rows
	rNRowSpan = 0;			// Remaining rows in the row span
	rNColSpan = 0;			// Remaining cols in the col span
	nRowSpannedTitleCol = 0;	// Number of title cols from row span
		
	// Loop through rows
	for (var i=0; i<nRow; i++)
	{
		nColSpan = 1, colPos = 0;
		// Loop through columns
		// Initializing
		for (var j=0; j<table.rows[i].cells.length; j++)
		{
			// Do this iff title has not been found
			if (titleFound == false)
			{
				if (table.rows[i].cells[j].rowSpan > 1)
				{
					if (table.rows[i].cells[j].colSpan < 2)
					{
						titleSpanCellArray[colPos] =
							table.rows[i].cells[j];
						titleRowArray[colPos] =
							table.rows[i];
						colTitleFilled[colPos] = true;
						nRowSpannedTitleCol++;
					}
					if (table.rows[i].cells[j].rowSpan - 1 
						> rNRowSpan)
					{
						rNRowSpan = 
							table.
							rows[i].cells[j].
							rowSpan - 1;

						if (table.rows[i].
							cells[j].colSpan > 1)
							rNColSpan = 
								rNRowSpan + 1;
					}
				}
			}
			if (table.rows[i].cells[j].colSpan > 1 &&
				rNColSpan == 0)
			{ 
				nColSpan = table.rows[i].cells[j].colSpan;
				colPos += nColSpan;
			}
			else
			{
				colPos++;
			}		
		}
					
		// Setting up the title cells
		if (titleFound == false && nColSpan == 1 && 
			rNRowSpan == 0 && rNColSpan == 0 && titleFound == false)
		{
			colSpanArray[i] = true;
			titleFound = true;

			// Using indivisual cell as an array element
			countCol = 0;
			for (var j=0;
				j<table.rows[i].cells.length
					+ nRowSpannedTitleCol; j++)
			{
				if (colTitleFilled[j] != true)
				{
					titleRowCellArray[j] =
						table.rows[i].cells[countCol];
					titleRowArray[j] =
						table.rows[i];
					countCol++;
				}
				else
				{
					titleRowCellArray[j] = 
						titleSpanCellArray[j];
					
				}
				titleInnerHTMLArray[j] =
					String(titleRowCellArray[j].innerHTML);
				titleSpanCountArray[j] = 
					titleRowCellArray[j].rowSpan;
			}
		}
		// Setting up the data rows
		else if (titleFound == true && nColSpan == 1 && rNRowSpan == 0)
		{
			for (var j=0; j<table.rows[i].cells.length; j++)
			{
				// Can't have row span in record rows ...
				if (table.rows[i].cells[j].rowSpan > 1) return;

				currentCell = table.rows[i].cells[j];
				if (j == 0)
				{
					rowArray[actualNRow] = 
						String(currentCell.innerHTML);
				}
				else
				{
					rowArray[actualNRow] += recDelimiter +
						String(currentCell.innerHTML);
				}
			}
			// Inconsistent col lengh for data rows
			if (table.rows[i].cells.length > maxNCol)
				return;
			actualNRow++;
			colSpanArray[i] = false;
		}
		else if (nColSpan == 1 && rNRowSpan == 0 && 
			rNColSpan == 0 && titleFound == false)
		{
			colSpanArray[i] = false;
		}
		else
		{
			colSpanArray[i] = true;
		}
		
		// Counters for row/column spans
		if (rNRowSpan > 0) rNRowSpan--;
		if (rNColSpan > 0) rNColSpan--;
	}

	// If the row number is < 1, no need to do anything ...
	if (actualNRow < 1) return;

	// Re-drawing the title row
	redrawTitle(false);
}
//*****************************************************************************
// Function called to re-draw title row 
//*****************************************************************************
function redrawTitle(isSort)
{
	var currentRow, innerHTML, cellIndex;
	var reAnchor, reUpDown, reLabel, cellAlign, makeBold;

	cellAlign = "";
	makeBold = false;
	reAnchor = / *\<a[^\>]*\>(.*) *\<\/a\>/i;
	reUpDown = /\<font *id=.*updown.* *color\=.*\>.*\<\/font\>/i;
	reLabel = /\>([^\<]*)\</g;

	// Re-drawing the title row
	for (var j=0; j<maxNCol; j++)
	{
		currentRow = titleRowArray[j];
		innerHTML = String(titleInnerHTMLArray[j]);
		cellIndex = titleRowCellArray[j].cellIndex;
		cellAlign = titleRowCellArray[j].align;
		currentRow.deleteCell(cellIndex);
		currentRow.insertCell(cellIndex);
		if (cellAlign != "")
			currentRow.cells[cellIndex].align =
				cellAlign;
		if (titleRowCellArray[j].tagName == "TH")
		{
			currentRow.cells[cellIndex].align =
				"center";
			makeBold = true;
		}
		if (titleSpanCountArray[j] > 1)
			currentRow.cells[cellIndex].rowSpan = 
				titleSpanCountArray[j];
		newTitle = '';
		if (j == sortIndex && isSort)
		{
			newTitle = '<font id=updown color=' + 
				updownColor + '>&nbsp;';
			if (descending)
				newTitle += desChr;
			else
				newTitle += ascChr;
			newTitle += '</font>';
		} 
		// Remove carriage return, linefeed, and tab
		innerHTML = innerHTML.replace(/\r|\n|\t/g, "");
		if (makeBold)
		{
			if (innerHTML.match(reLabel))
				innerHTML = 
					innerHTML.replace(reLabel, "<b>$1</b>");
			else
				innerHTML =
					innerHTML.replace(
						/(^.*$)/, "<b>$1</b>");
		}
		innerHTML = innerHTML.replace(reUpDown, "");
		innerHTML = innerHTML.replace(reAnchor, "$1");
		currentRow.cells[cellIndex].innerHTML =
			'<a ' + linkEventString + j + ',' +
			'"' + table.id + '"' + ');\'>' + 
			innerHTML +
			'</a>' + 
			newTitle;
		titleRowCellArray[j] = currentRow.cells[cellIndex];
	}

}

//*****************************************************************************
// Function called when user clicks on a title to sort
//*****************************************************************************
function sortTable(index,obj)
{
	// Re-inializing the table object
	initTable(obj);

	// Local variables
	var rowContent;
	var rowCount;
	
	// Can't sort past the max allowed column size
	if (index < 0 || index >= maxNCol) return;
	
	// Assignment of sort index
	sortIndex = index;
	// Doing the sort using JavaScript generic function for an Array
	rowArray.sort(compare);

	// Re-drawing the title row
	redrawTitle(true);

	// Re-drawing the table
	rowCount = 0;
	for (var i=0; i<nRow; i++)
	{
		if (! colSpanArray[i])
		{
			for (var j=0; j<maxNCol; j++)
			{
				rowContent = rowArray[rowCount].
					split(recDelimiter);
				table.rows[i].deleteCell(j);
				table.rows[i].insertCell(j);
				table.rows[i].cells[j].innerHTML =
					rowContent[j];
			}
			rowCount++;
		}
	}

	// Switching btw descending/ascending sort
	if (descending)
		descending = false;
	else
		descending = true;
}

//*****************************************************************************
// Function to be used for Array sorting
//*****************************************************************************
function compare(a, b)
{
	// Getting the element array for inputs (a,b)
	var aRowContent = a.split(recDelimiter);
	var bRowContent = b.split(recDelimiter);
	
	// Needed in case the data conversion is necessary
	var aToBeCompared, bToBeCompared;

	if (! isNaN(aRowContent[sortIndex]))
		aToBeCompared = parseInt(aRowContent[sortIndex], 10);
	else
		aToBeCompared = aRowContent[sortIndex];

	if (! isNaN(bRowContent[sortIndex]))
		bToBeCompared = parseInt(bRowContent[sortIndex], 10);
	else
		bToBeCompared = bRowContent[sortIndex];

	if (aToBeCompared < bToBeCompared)
		if (!descending)
		{
			return -1;
		}
		else
		{
			return 1;
		}
	if (aToBeCompared > bToBeCompared)
		if (!descending)
		{
			return 1;
		}
		else
		{
			return -1;
		}
	return 0;
}

//*****************************************************************************
// Function to set the cursor
//*****************************************************************************
function setCursor(obj)
{
	var rowText, reRowText;

	reRowText = /\< *[^\>]*\>/g;
	// Show hint text at the browser status bar
	rowText = String(obj.innerHTML);

	// Remove HTML tags
	rowText = rowText.replace(reRowText, "");
	// Remove carriage return, linefeed, and tab
	rowText = rowText.replace(/\r|\n|\t/g, "");
	// Remove leading/trailing white spaces
	rowText = rowText.replace(/ *([^ ]*) */g, "$1");
	
	// Setting window's status bar
	window.status = "Sort by " + String(rowText);

	// Change the mouse cursor to pointer or hand 
	if (isIE)
		obj.style.cursor = "hand";
	else
		obj.style.cursor = "pointer";
}

//*****************************************************************************
// Function to set the title color
//*****************************************************************************
function setColor(obj,mode)
{
	if (mode == "selected")
	{
		// Remember the original color
		if (obj.style.color != selectedColor) 
			defaultColor = obj.style.color;
		obj.style.color = selectedColor;
	}
	else
	{	
		// Restoring original color and re-setting the status bar
		obj.style.color = defaultColor;
		window.status = '';
	}
}

//*****************************************************************************
// Function to check browser type/version
//*****************************************************************************
function checkBrowser()
{
	if (navigator.appName == "Microsoft Internet Explorer"
		&& parseInt(navigator.appVersion) >= 4)
	{
		isIE = true;
		return true;
	}
	// For some reason, appVersion returns 5 for Netscape 6.2 ...
	else if (navigator.appName == "Netscape"
		&& navigator.appVersion.indexOf("5.") >= 0)
	{
		isIE = false;
		return true;
	}
	else
		return false;
}
