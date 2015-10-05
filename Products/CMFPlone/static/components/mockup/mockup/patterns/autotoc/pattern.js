/* Autotoc pattern.
 *
 * Options:
 *    IDPrefix(string): Prefix used to generate ID. ('autotoc-item-')
 *    classActiveName(string): Class used for active level. ('active')
 *    classLevelPrefixName(string): Class prefix used for the TOC levels. ('autotoc-level-')
 *    classSectionName(string): Class used for section in TOC. ('autotoc-section')
 *    classTOCName(string): Class used for the TOC. ('autotoc-nav')
 *    levels(string): Selectors used to find levels. ('h1,h2,h3')
 *    scrollDuration(string): Speed of scrolling. ('slow')
 *    scrollEasing(string): Easing to use while scrolling. ('swing')
 *    section(string): Tag type to use for TOC. ('section')
 *
 * Documentation:
 *    # TOC
 *    {{ example-1 }}
 *
 *    # Tabs
 *    {{ example-2-tabs }}
 *
 * Example: example-1
 *    <div class="pat-autotoc"
 *          data-pat-autotoc="scrollDuration:slow;levels:h4,h5,h6;">
 *      <h4>Title 1</h4>
 *      <p>Mr. Zuckerkorn, you've been warned about touching. You said
 *         spanking. It walked on my pillow! How about a turtle? I've always
 *         loved those leathery little snappy faces.</p>
 *      <h5>Title 1.1</h5>
 *      <p>Ah coodle doodle do Caw ca caw, caw ca caw. Butterscotch!</p>
 *      <h6>Title 1.1.1</h6>
 *      <p>Want a lick? Okay, Lindsay, are you forgetting that I was
 *         a professional twice over - an analyst and a therapist.</p>
 *      <h4>Title 2</h4>
 *      <p>You boys know how to shovel coal? Don't worry, these young
 *      beauties have been nowhere near the bananas. I thought the two of
 *      us could talk man-on-man.</p>
 *    </div>
 *
 * Example: example-2-tabs
 *    <div class="pat-autotoc autotabs"
 *          data-pat-autotoc="section:fieldset;levels:legend;">
 *        <fieldset>
 *          <legend>Tab 1</legend>
 *          <div>
 *            Lorem ipsum dolor sit amet, ex nam odio ceteros fastidii,
 *            id porro lorem pro, homero facilisis in cum.
 *            At doming voluptua indoctum mel, natum noster similique ne mel.
 *          </div>
 *        </fieldset>
 *        <fieldset>
 *          <legend>Tab 2</legend>
 *          <div>
 *            Reque repudiare eum et. Prompta expetendis percipitur eu eam,
 *            et graece mandamus pro, eu vim harum audire tractatos.
 *            Ad perpetua salutandi mea, soluta delicata aliquando eam ne.
 *            Qui nostrum lucilius perpetua ut, eum suas stet oblique ut.
 *          </div>
 *        </fieldset>
 *        <fieldset>
 *          <legend>Tab 3</legend>
 *          <div>
 *            Vis mazim harum deterruisset ex, duo nemore nostro civibus ad,
 *            eros vituperata id cum. Vim at erat solet soleat,
 *            eum et iuvaret luptatum, pro an esse dolorum maiestatis.
 *          </div>
 *        </fieldset>
 *    </div>
 *
 */


define([
  'jquery',
  'mockup-patterns-base'
], function($, Base) {
  'use strict';

  var AutoTOC = Base.extend({
    name: 'autotoc',
    trigger: '.pat-autotoc',
    defaults: {
      section: 'section',
      levels: 'h1,h2,h3',
      IDPrefix: 'autotoc-item-',
      classTOCName: 'autotoc-nav',
      classSectionName: 'autotoc-section',
      classLevelPrefixName: 'autotoc-level-',
      classActiveName: 'active',
      scrollDuration: 'slow',
      scrollEasing: 'swing'
    },
    init: function() {
      var self = this;

      self.$toc = $('<nav/>').addClass(self.options.classTOCName);

      if (self.options.prependTo) {
        self.$toc.prependTo(self.options.prependTo);
      } else if (self.options.appendTo) {
        self.$toc.appendTo(self.options.appendTo);
      } else {
        self.$toc.prependTo(self.$el);
      }

      if (self.options.className) {
        self.$el.addClass(self.options.className);
      }

      $(self.options.section, self.$el).addClass(self.options.classSectionName);

      var asTabs = self.$el.hasClass('autotabs');

      var activeId = null;

      $(self.options.levels, self.$el).each(function(i) {
        var $level = $(this),
            id = $level.prop('id') ? $level.prop('id') :
                 $level.parents(self.options.section).prop('id');
        if (!id || $('#' + id).length > 0) {
          id = self.options.IDPrefix + self.name + '-' + i;
        }
        if(window.location.hash === '#' + id){
          activeId = id;
        }
        $('<a/>')
          .appendTo(self.$toc)
          .text($level.text())
          .attr('id', id)
          .attr('href', '#' + id)
          .addClass(self.options.classLevelPrefixName + self.getLevel($level))
          .on('click', function(e, options) {
            e.stopPropagation();
            e.preventDefault();
            if(!options){
              options = {
                doScroll: true,
                skipHash: false
              };
            }
            var $el = $(this);
            self.$toc.children('.' + self.options.classActiveName).removeClass(self.options.classActiveName);
            self.$el.children('.' + self.options.classActiveName).removeClass(self.options.classActiveName);
            $(e.target).addClass(self.options.classActiveName);
            $level.parents(self.options.section).addClass(self.options.classActiveName);
            if (options.doScroll !== false &&
                self.options.scrollDuration &&
                $level &&
                !asTabs) {
              $('body,html').animate({
                scrollTop: $level.offset().top
              }, self.options.scrollDuration, self.options.scrollEasing);
            }
            if (self.$el.parents('.plone-modal').size() !== 0) {
              self.$el.trigger('resize.plone-modal.patterns');
            }
            $(this).trigger('clicked');
            if(!options.skipHash){
              window.location.hash = $el.attr('id');
            }
          });
      });

      if(activeId){
        $('a#' + activeId).trigger('click', {
          doScroll: true,
          skipHash: true
        });
      }else{
        self.$toc.find('a').first().trigger('click', {
          doScroll: false,
          skipHash: true});
      }
    },
    getLevel: function($el) {
      var elementLevel = 0;
      $.each(this.options.levels.split(','), function(level, levelSelector) {
        if ($el.filter(levelSelector).size() === 1) {
          elementLevel = level + 1;
          return false;
        }
      });
      return elementLevel;
    }
  });

  return AutoTOC;

});
