/*
	cssQuery, version 2.0.2 (2005-08-19)
	Copyright: 2004-2005, Dean Edwards (http://dean.edwards.name/)
	License: http://creativecommons.org/licenses/LGPL/2.1/
*/

// WARNING!!!! This file was customized from the original version!
// Changes are marked with XXX. Also consult the checkin log.

// the following functions allow querying of the DOM using CSS selectors
var cssQuery = function() {
var version = "2.0.2";

// -----------------------------------------------------------------------
// main query function
// -----------------------------------------------------------------------

var $COMMA = /\s*,\s*/;
var cssQuery = function($selector, $$from) {
try {
	var $match = [];
	var $useCache = arguments.callee.caching && !$$from;
	var $base = ($$from) ? ($$from.constructor == Array) ? $$from : [$$from] : [document];
	// process comma separated selectors
	var $$selectors = parseSelector($selector).split($COMMA), i;
	for (i = 0; i < $$selectors.length; i++) {
		// convert the selector to a stream
		$selector = _toStream($$selectors[i]);
		// faster chop if it starts with id (MSIE only)
		if (isMSIE && $selector.slice(0, 3).join("") == " *#") {
			$selector = $selector.slice(2);
			$$from = _msie_selectById([], $base, $selector[1]);
		} else $$from = $base;
		// process the stream
		var j = 0, $token, $filter, $arguments, $cacheSelector = "";
		while (j < $selector.length) {
			$token = $selector[j++];
			$filter = $selector[j++];
			$cacheSelector += $token + $filter;
			// some pseudo-classes allow arguments to be passed
			//  e.g. nth-child(even)
			$arguments = "";
			if ($selector[j] == "(") {
				while ($selector[j++] != ")" && j < $selector.length) {
					$arguments += $selector[j];
				}
				$arguments = $arguments.slice(0, -1);
				$cacheSelector += "(" + $arguments + ")";
			}
			// XXX - fschulze - shortcut for pure id selectors
			if ($token==" " && $filter=="*" && $selector[j]=="#")
				continue;
			// process a token/filter pair use cached results if possible
			$$from = ($useCache && cache[$cacheSelector]) ?
				cache[$cacheSelector] : select($$from, $token, $filter, $arguments);
			if ($useCache) cache[$cacheSelector] = $$from;
		}
		$match = $match.concat($$from);
	}
	delete cssQuery.error;
	return $match;
} catch ($error) {
	cssQuery.error = $error;
	return [];
}};

// -----------------------------------------------------------------------
// public interface
// -----------------------------------------------------------------------

cssQuery.toString = function() {
	return "function cssQuery() {\n  [version " + version + "]\n}";
};

// caching
var cache = {};
cssQuery.caching = false;
cssQuery.clearCache = function($selector) {
	if ($selector) {
		$selector = _toStream($selector).join("");
		delete cache[$selector];
	} else cache = {};
};

// allow extensions
var modules = {};
var loaded = false;
cssQuery.addModule = function($name, $script) {
	if (loaded) eval("$script=" + String($script));
	modules[$name] = new $script();;
};

// hackery
cssQuery.valueOf = function($code) {
	return $code ? eval($code) : this;
};

// -----------------------------------------------------------------------
// declarations
// -----------------------------------------------------------------------

var selectors = {};
var pseudoClasses = {};
// a safari bug means that these have to be declared here
var AttributeSelector = {match: /\[([\w-]+(\|[\w-]+)?)\s*(\W?=)?\s*([^\]]*)\]/};
var attributeSelectors = [];

// -----------------------------------------------------------------------
// selectors
// -----------------------------------------------------------------------

// descendant selector
selectors[" "] = function($results, $from, $tagName, $namespace) {
	// loop through current selection
	var $element, i, j;
	for (i = 0; i < $from.length; i++) {
		// get descendants
		var $subset = getElementsByTagName($from[i], $tagName, $namespace);
		// loop through descendants and add to results selection
		for (j = 0; ($element = $subset[j]); j++) {
			if (thisElement($element) && compareNamespace($element, $namespace))
				$results.push($element);
		}
	}
};

// ID selector
selectors["#"] = function($results, $from, $id) {
	var $element, j;
	// XXX - fschulze - Try to make this as fast as possible
	// first see whether we have a chance to optimize this
	if ($from.length==1 && $from[0]==document) {
		var $node = document.getElementById($id);
		if ($node)
			$results.push($node);
	} else {
		// loop through current selection and check ID
		for (j = 0; ($element = $from[j]); j++)
			if ($element.id == $id) {
				$results.push($element);
				break;
			}
	}
};

// class selector
selectors["."] = function($results, $from, $className) {
	// create a RegExp version of the class
	$className = new RegExp("(^|\\s)" + $className + "(\\s|$)");
	// loop through current selection and check class
	var $element, i;
	for (i = 0; ($element = $from[i]); i++)
		if ($className.test($element.className)) $results.push($element);
};

// pseudo-class selector
selectors[":"] = function($results, $from, $pseudoClass, $arguments) {
	// retrieve the cssQuery pseudo-class function
	var $test = pseudoClasses[$pseudoClass], $element, i;
	// loop through current selection and apply pseudo-class filter
	if ($test) for (i = 0; ($element = $from[i]); i++)
		// if the cssQuery pseudo-class function returns "true" add the element
		if ($test($element, $arguments)) $results.push($element);
};

// -----------------------------------------------------------------------
// pseudo-classes
// -----------------------------------------------------------------------

pseudoClasses["link"] = function($element) {
	var $document = getDocument($element);
	if ($document.links) for (var i = 0; i < $document.links.length; i++) {
		if ($document.links[i] == $element) return true;
	}
};

pseudoClasses["visited"] = function($element) {
	// can't do this without jiggery-pokery
};

// -----------------------------------------------------------------------
// DOM traversal
// -----------------------------------------------------------------------

// IE5/6 includes comments (LOL) in it's elements collections.
// so we have to check for this. the test is tagName != "!". LOL (again).
var thisElement = function($element) {
	return ($element && $element.nodeType == 1 && $element.tagName != "!") ? $element : null;
};

// return the previous element to the supplied element
//  previousSibling is not good enough as it might return a text or comment node
var previousElementSibling = function($element) {
	while ($element && ($element = $element.previousSibling) && !thisElement($element)) continue;
	return $element;
};

// return the next element to the supplied element
var nextElementSibling = function($element) {
	while ($element && ($element = $element.nextSibling) && !thisElement($element)) continue;
	return $element;
};

// return the first child ELEMENT of an element
//  NOT the first child node (though they may be the same thing)
var firstElementChild = function($element) {
	return thisElement($element.firstChild) || nextElementSibling($element.firstChild);
};

var lastElementChild = function($element) {
	return thisElement($element.lastChild) || previousElementSibling($element.lastChild);
};

// return child elements of an element (not child nodes)
var childElements = function($element) {
	var $childElements = [];
	$element = firstElementChild($element);
	while ($element) {
		$childElements.push($element);
		$element = nextElementSibling($element);
	}
	return $childElements;
};

// -----------------------------------------------------------------------
// browser compatibility
// -----------------------------------------------------------------------

// all of the functions in this section can be overwritten. the default
//  configuration is for IE. The functions below reflect this. standard
//  methods are included in a separate module. It would probably be better
//  the other way round of course but this makes it easier to keep IE7 trim.

var isMSIE = true;

var isXML = function($element) {
	var $document = getDocument($element);
	return (typeof $document.mimeType == "unknown") ?
		/\.xml$/i.test($document.URL) :
		Boolean($document.mimeType == "XML Document");
};

// return the element's containing document
var getDocument = function($element) {
	return $element.ownerDocument || $element.document;
};

var getElementsByTagName = function($element, $tagName) {
	return ($tagName == "*" && $element.all) ? $element.all : $element.getElementsByTagName($tagName);
};

var compareTagName = function($element, $tagName, $namespace) {
	if ($tagName == "*") return thisElement($element);
	if (!compareNamespace($element, $namespace)) return false;
	// XXX - fschulze - this fixes problems with content inserted from an
	// XMLHTTPRequest. The content is originally XML and then inserted into
	// the HTML document, this causes some elements to have lowercase tagNames
	if (!isXML($element))
	    return $element.tagName.toUpperCase() == $tagName.toUpperCase();
	return $element.tagName == $tagName;
};

var compareNamespace = function($element, $namespace) {
	return !$namespace || ($namespace == "*") || ($element.scopeName == $namespace);
};

var getTextContent = function($element) {
	return $element.innerText;
};

function _msie_selectById($results, $from, id) {
	var $match, i, j;
	for (i = 0; i < $from.length; i++) {
		if ($match = $from[i].all.item(id)) {
			if ($match.id == id) $results.push($match);
			else if ($match.length != null) {
				for (j = 0; j < $match.length; j++) {
					if ($match[j].id == id) $results.push($match[j]);
				}
			}
		}
	}
	return $results;
};

// for IE5.0
if (![].push) Array.prototype.push = function() {
	for (var i = 0; i < arguments.length; i++) {
		this[this.length] = arguments[i];
	}
	return this.length;
};

// -----------------------------------------------------------------------
// query support
// -----------------------------------------------------------------------

// select a set of matching elements.
// "from" is an array of elements.
// "token" is a character representing the type of filter
//  e.g. ">" means child selector
// "filter" represents the tag name, id or class name that is being selected
// the function returns an array of matching elements
var $NAMESPACE = /\|/;
function select($$from, $token, $filter, $arguments) {
	if ($NAMESPACE.test($filter)) {
		$filter = $filter.split($NAMESPACE);
		$arguments = $filter[0];
		$filter = $filter[1];
	}
	var $results = [];
	if (selectors[$token]) {
		selectors[$token]($results, $$from, $filter, $arguments);
	}
	return $results;
};

// -----------------------------------------------------------------------
// parsing
// -----------------------------------------------------------------------

// convert css selectors to a stream of tokens and filters
//  it's not a real stream. it's just an array of strings.
var $STANDARD_SELECT = /^[^\s>+~]/;
var $$STREAM = /[\s#.:>+~()@]|[^\s#.:>+~()@]+/g;
function _toStream($selector) {
	if ($STANDARD_SELECT.test($selector)) $selector = " " + $selector;
	return $selector.match($$STREAM) || [];
};

var $WHITESPACE = /\s*([\s>+~(),]|^|$)\s*/g;
var $IMPLIED_ALL = /([\s>+~,]|[^(]\+|^)([#.:@])/g;
var parseSelector = function($selector) {
	return $selector
	// trim whitespace
	.replace($WHITESPACE, "$1")
	// e.g. ".class1" --> "*.class1"
	.replace($IMPLIED_ALL, "$1*$2");
};

var Quote = {
	toString: function() {return "'"},
	match: /^('[^']*')|("[^"]*")$/,
	test: function($string) {
		return this.match.test($string);
	},
	add: function($string) {
		return this.test($string) ? $string : this + $string + this;
	},
	remove: function($string) {
		return this.test($string) ? $string.slice(1, -1) : $string;
	}
};

var getText = function($text) {
	return Quote.remove($text);
};

var $ESCAPE = /([\/()[\]?{}|*+-])/g;
function regEscape($string) {
	return $string.replace($ESCAPE, "\\$1");
};

// -----------------------------------------------------------------------
// modules
// -----------------------------------------------------------------------

/*
	cssQuery, version 2.0.2 (2005-08-19)
	Copyright: 2004-2005, Dean Edwards (http://dean.edwards.name/)
	License: http://creativecommons.org/licenses/LGPL/2.1/
*/

cssQuery.addModule("css-standard", function() { // override IE optimisation

// cssQuery was originally written as the CSS engine for IE7. It is
//  optimised (in terms of size not speed) for IE so this module is
//  provided separately to provide cross-browser support.

// -----------------------------------------------------------------------
// browser compatibility
// -----------------------------------------------------------------------

// sniff for Win32 Explorer
isMSIE = eval("false;/*@cc_on@if(@\x5fwin32)isMSIE=true@end@*/");

if (!isMSIE) {
	getElementsByTagName = function($element, $tagName, $namespace) {
		return $namespace ? $element.getElementsByTagNameNS("*", $tagName) :
			$element.getElementsByTagName($tagName);
	};

	compareNamespace = function($element, $namespace) {
		return !$namespace || ($namespace == "*") || ($element.prefix == $namespace);
	};

	isXML = document.contentType ? function($element) {
		return /xml/i.test(getDocument($element).contentType);
	} : function($element) {
		return getDocument($element).documentElement.tagName != "HTML";
	};

	getTextContent = function($element) {
		// mozilla || opera || other
		return $element.textContent || $element.innerText || _getTextContent($element);
	};

	function _getTextContent($element) {
		var $textContent = "", $node, i;
		for (i = 0; ($node = $element.childNodes[i]); i++) {
			switch ($node.nodeType) {
				case 11: // document fragment
				case 1: $textContent += _getTextContent($node); break;
				case 3: $textContent += $node.nodeValue; break;
			}
		}
		return $textContent;
	};
}
}); // addModule

/*
	cssQuery, version 2.0.2 (2005-08-19)
	Copyright: 2004-2005, Dean Edwards (http://dean.edwards.name/)
	License: http://creativecommons.org/licenses/LGPL/2.1/
*/

cssQuery.addModule("css-level2", function() {

// -----------------------------------------------------------------------
// selectors
// -----------------------------------------------------------------------

// child selector
selectors[">"] = function($results, $from, $tagName, $namespace) {
	var $element, i, j;
	for (i = 0; i < $from.length; i++) {
		var $subset = childElements($from[i]);
		for (j = 0; ($element = $subset[j]); j++)
			if (compareTagName($element, $tagName, $namespace))
				$results.push($element);
	}
};

// sibling selector
selectors["+"] = function($results, $from, $tagName, $namespace) {
	for (var i = 0; i < $from.length; i++) {
		var $element = nextElementSibling($from[i]);
		if ($element && compareTagName($element, $tagName, $namespace))
			$results.push($element);
	}
};

// attribute selector
selectors["@"] = function($results, $from, $attributeSelectorID) {
	var $test = attributeSelectors[$attributeSelectorID].test;
	var $element, i;
	for (i = 0; ($element = $from[i]); i++)
		if ($test($element)) $results.push($element);
};

// -----------------------------------------------------------------------
// pseudo-classes
// -----------------------------------------------------------------------

pseudoClasses["first-child"] = function($element) {
	return !previousElementSibling($element);
};

pseudoClasses["lang"] = function($element, $code) {
	$code = new RegExp("^" + $code, "i");
	while ($element && !$element.getAttribute("lang")) $element = $element.parentNode;
	return $element && $code.test($element.getAttribute("lang"));
};

// -----------------------------------------------------------------------
//  attribute selectors
// -----------------------------------------------------------------------

// constants
AttributeSelector.NS_IE = /\\:/g;
AttributeSelector.PREFIX = "@";
// properties
AttributeSelector.tests = {};
// methods
AttributeSelector.replace = function($match, $attribute, $namespace, $compare, $value) {
	var $key = this.PREFIX + $match;
	if (!attributeSelectors[$key]) {
		$attribute = this.create($attribute, $compare || "", $value || "");
		// store the selector
		attributeSelectors[$key] = $attribute;
		attributeSelectors.push($attribute);
	}
	return attributeSelectors[$key].id;
};
AttributeSelector.parse = function($selector) {
	$selector = $selector.replace(this.NS_IE, "|");
	var $match;
	while ($match = $selector.match(this.match)) {
		var $replace = this.replace($match[0], $match[1], $match[2], $match[3], $match[4]);
		$selector = $selector.replace(this.match, $replace);
	}
	return $selector;
};
AttributeSelector.create = function($propertyName, $test, $value) {
	var $attributeSelector = {};
	$attributeSelector.id = this.PREFIX + attributeSelectors.length;
	$attributeSelector.name = $propertyName;
	$test = this.tests[$test];
	$test = $test ? $test(this.getAttribute($propertyName), getText($value)) : false;
	$attributeSelector.test = new Function("e", "return " + $test);
	return $attributeSelector;
};
AttributeSelector.getAttribute = function($name) {
	switch ($name.toLowerCase()) {
		case "id":
			return "e.id";
		case "class":
			return "e.className";
		case "for":
			return "e.htmlFor";
		case "href":
			if (isMSIE) {
				// IE always returns the full path not the fragment in the href attribute
				//  so we RegExp it out of outerHTML. Opera does the same thing but there
				//  is no way to get the original attribute.
				return "String((e.outerHTML.match(/href=\\x22?([^\\s\\x22]*)\\x22?/)||[])[1]||'')";
			}
	}
	return "e.getAttribute('" + $name.replace($NAMESPACE, ":") + "')";
};

// -----------------------------------------------------------------------
//  attribute selector tests
// -----------------------------------------------------------------------

AttributeSelector.tests[""] = function($attribute) {
	return $attribute;
};

AttributeSelector.tests["="] = function($attribute, $value) {
	return $attribute + "==" + Quote.add($value);
};

AttributeSelector.tests["~="] = function($attribute, $value) {
	return "/(^| )" + regEscape($value) + "( |$)/.test(" + $attribute + ")";
};

AttributeSelector.tests["|="] = function($attribute, $value) {
	return "/^" + regEscape($value) + "(-|$)/.test(" + $attribute + ")";
};

// -----------------------------------------------------------------------
//  parsing
// -----------------------------------------------------------------------

// override parseSelector to parse out attribute selectors
var _parseSelector = parseSelector;
parseSelector = function($selector) {
	return _parseSelector(AttributeSelector.parse($selector));
};

}); // addModule

/*
	cssQuery, version 2.0.2 (2005-08-19)
	Copyright: 2004-2005, Dean Edwards (http://dean.edwards.name/)
	License: http://creativecommons.org/licenses/LGPL/2.1/
*/

/* Thanks to Bill Edney */

cssQuery.addModule("css-level3", function() {

// -----------------------------------------------------------------------
// selectors
// -----------------------------------------------------------------------

// indirect sibling selector
selectors["~"] = function($results, $from, $tagName, $namespace) {
	var $element, i;
	for (i = 0; ($element = $from[i]); i++) {
		while ($element = nextElementSibling($element)) {
			if (compareTagName($element, $tagName, $namespace))
				$results.push($element);
		}
	}
};

// -----------------------------------------------------------------------
// pseudo-classes
// -----------------------------------------------------------------------

// I'm hoping these pseudo-classes are pretty readable. Let me know if
//  any need explanation.

pseudoClasses["contains"] = function($element, $text) {
	$text = new RegExp(regEscape(getText($text)));
	return $text.test(getTextContent($element));
};

pseudoClasses["root"] = function($element) {
	return $element == getDocument($element).documentElement;
};

pseudoClasses["empty"] = function($element) {
	var $node, i;
	for (i = 0; ($node = $element.childNodes[i]); i++) {
		if (thisElement($node) || $node.nodeType == 3) return false;
	}
	return true;
};

pseudoClasses["last-child"] = function($element) {
	return !nextElementSibling($element);
};

pseudoClasses["only-child"] = function($element) {
	$element = $element.parentNode;
	return firstElementChild($element) == lastElementChild($element);
};

pseudoClasses["not"] = function($element, $selector) {
	var $negated = cssQuery($selector, getDocument($element));
	for (var i = 0; i < $negated.length; i++) {
		if ($negated[i] == $element) return false;
	}
	return true;
};

pseudoClasses["nth-child"] = function($element, $arguments) {
	return nthChild($element, $arguments, previousElementSibling);
};

pseudoClasses["nth-last-child"] = function($element, $arguments) {
	return nthChild($element, $arguments, nextElementSibling);
};

pseudoClasses["target"] = function($element) {
	return $element.id == location.hash.slice(1);
};

// UI element states

pseudoClasses["checked"] = function($element) {
	return $element.checked;
};

pseudoClasses["enabled"] = function($element) {
	return $element.disabled === false;
};

pseudoClasses["disabled"] = function($element) {
	return $element.disabled;
};

pseudoClasses["indeterminate"] = function($element) {
	return $element.indeterminate;
};

// -----------------------------------------------------------------------
//  attribute selector tests
// -----------------------------------------------------------------------

AttributeSelector.tests["^="] = function($attribute, $value) {
	return "/^" + regEscape($value) + "/.test(" + $attribute + ")";
};

AttributeSelector.tests["$="] = function($attribute, $value) {
	return "/" + regEscape($value) + "$/.test(" + $attribute + ")";
};

AttributeSelector.tests["*="] = function($attribute, $value) {
	return "/" + regEscape($value) + "/.test(" + $attribute + ")";
};

// -----------------------------------------------------------------------
//  nth child support (Bill Edney)
// -----------------------------------------------------------------------

function nthChild($element, $arguments, $traverse) {
	switch ($arguments) {
		case "n": return true;
		case "even": $arguments = "2n"; break;
		case "odd": $arguments = "2n+1";
	}

	var $$children = childElements($element.parentNode);
	function _checkIndex($index) {
		var $index = ($traverse == nextElementSibling) ? $$children.length - $index : $index - 1;
		return $$children[$index] == $element;
	};

	//	it was just a number (no "n")
	if (!isNaN($arguments)) return _checkIndex($arguments);

	$arguments = $arguments.split("n");
	var $multiplier = parseInt($arguments[0]);
	var $step = parseInt($arguments[1]);

	if ((isNaN($multiplier) || $multiplier == 1) && $step == 0) return true;
	if ($multiplier == 0 && !isNaN($step)) return _checkIndex($step);
	if (isNaN($step)) $step = 0;

	var $count = 1;
	while ($element = $traverse($element)) $count++;

	if (isNaN($multiplier) || $multiplier == 1)
		return ($traverse == nextElementSibling) ? ($count <= $step) : ($step >= $count);

	return ($count % $multiplier) == $step;
};

}); // addModule

// -------- >>      insert modules here for packaging       << -------- \\

loaded = true;

// -----------------------------------------------------------------------
// return the query function
// -----------------------------------------------------------------------

return cssQuery;

}(); // cssQuery
