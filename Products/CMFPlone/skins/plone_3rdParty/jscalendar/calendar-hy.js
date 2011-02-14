// ** I18N

// Calendar HY language
// Author: Anoush Najarian, <a.najarian@att.net>
// Encoding: utf-8
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Կիրակի",
 "Երկուշաբթի",
 "Երեքշաբթի",
 "Չորեքշաբթի",
 "Հինգշաբթի",
 "Ուրբաթ",
 "Շաբաթ",
 "Կիրակի");

// Please note that the following array of short day names (and the same goes
// for short month names, _SMN) isn't absolutely necessary.  We give it here
// for exemplification on how one can customize the short day names, but if
// they are simply the first N letters of the full name you can simply say:
//
//   Calendar._SDN_len = N; // short day name length

Calendar._SMN_len = 4; // short month name length
//
// If N = 3 then this is not needed either since we assume a value of 3 if not
// present, to be compatible with translation files that were written before
// this feature.

// short day names
Calendar._SDN = new Array
("Կիր",
 "Երկ",
 "Երե",
 "Չոր",
 "Հին",
 "Ուր",
 "Շաբ",
 "Կիր");

// full month names
Calendar._MN = new Array
("Հունվար",
 "Փետրվար",
 "Մարտ",
 "Ապրիլ",
 "Մայիս",
 "Հունիս",
 "Հուլիս",
 "Օգոստոս",
 "Սեպտեմբեր",
 "Հոկտեմբեր",
 "Նոյեմբեր",
 "Դեկտեմբեր");

// short month names
Calendar._SMN = new Array
("Հուն",
 "Փետ",
 "Մար",
 "Ապր",
 "Մայ",
 "Հուն",
 "Հուլ",
 "Օգո",
 "Սեպ",
 "Հոկ",
 "Նով",
 "Դեկ");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Օրացույցի մասին";

Calendar._TT["ABOUT"] =
"DHTML ամսաթիվ և ժամ ընտրելու գործիք\n" +
"(c) dynarch.com 2002-2003\n" + // don't translate this this ;-)
"Վերջին տարբերակը գտնելու համար, այցելել. http://dynarch.com/mishoo/calendar.epl\n" +
"Լիցենզավորում. GNU LGPL, տեսնել http://gnu.org/licenses/lgpl.html:" +
"\n\n" +
"Ամսաթվի թնտրություն.\n" +
"- Ընտրել տարին \xab, \xbb կոճակների միջոցով\n" +
"- Ընտրել ամիսը " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " կոճակներով\n" +
"- Պահել մկնիկը կոճակի վրա արագ ընտրություն կատարելու համար";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Ընտրել ժամը.\n" +
"- Սեղմել ժամանակի տարրերի վրա ավելացնելու համար\n" +
"- կամ սեղմել Shift կոճակը պահելով\n" +
"- կամ սեղմել և քաշել:";

Calendar._TT["PREV_YEAR"] = "Նախ. տարի (պահել և տեսնել մենու)";
Calendar._TT["PREV_MONTH"] = "Հաջ. տարի (պահել և տեսնել մենու)";
Calendar._TT["GO_TODAY"] = "Այսօր";
Calendar._TT["NEXT_MONTH"] = "Հաջ. ամիս (պահել և տեսնել մենու)";
Calendar._TT["NEXT_YEAR"] = "Հաջ. տարի (պահել և տեսնել մենու)";
Calendar._TT["SEL_DATE"] = "Ընտրել ամսաթիվ";
Calendar._TT["DRAG_TO_MOVE"] = "Քաշել տեղափոխելու համար";
Calendar._TT["PART_TODAY"] = " (այսօր)";
Calendar._TT["MON_FIRST"] = "Սկսել երկուշաբթի օրվանից";
Calendar._TT["SUN_FIRST"] = "Սկսել կիրակի օրվանից";
Calendar._TT["CLOSE"] = "Փակել";
Calendar._TT["TODAY"] = "Այսօր";
Calendar._TT["TIME_PART"] = "(Shift-ը պահած) Սեղմել կամ քաշել արժեքը փոփոխելու համար";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d-%m-%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %b %e";

Calendar._TT["WK"] = "շբթ";


