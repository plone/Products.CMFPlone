(function ($) {
    if (!$.fn.tree) {
        throw "Error jqTree is not loaded.";
    }

    $.fn.jqTreeContextMenu = function (options) {
        var defaults = {
            menuFadeDuration: 250,
            selectClickedNode: true,
            onContextMenuItem: null,
            contextMenuDecider: null
        };
        var settings = $.extend({}, defaults, options);
        var $el = this;
        var $menuEl;

        // Check if useContextMenu option is set
        var jqTree = $el.data('simple_widget_tree');
        if(!jqTree || !jqTree.options.useContextMenu){
            throw 'Either jqTree was not found or useContextMenu in jqTree is set to false.';
        }

        // Check if the parameter is a jquery object
        if(settings.menu instanceof jQuery) {
            $menuEl = settings.menu;
        } else if (typeof settings.menu == "string") {
            $menuEl = $(settings.menu);
        } else {
            throw 'You must pass a menu selector string or jquery element to the jqTreeContextMenu.';
        }
        $menuEl.hide();
        if (settings.onContextMenuItem) {
            this.bind('cm-jqtree.item.click', settings.onContextMenuItem);
        }

        // Handle the contextmenu event sent from jqTree when user clicks right mouse button.
        $el.bind('tree.contextmenu', function (event) {
            var menu = $menuEl;
            if (typeof(settings.contextMenuDecider) == "function") {
                var menuChoice = settings.contextMenuDecider(event.node);
                menu = (typeof menuChoice == "string") ? $(menuChoice) : $menuEl;
            }
            var x = event.click_event.pageX;
            var y = event.click_event.pageY;
            var yPadding = 5;
            var xPadding = 5;

            var menuHeight = menu.height();
            var menuWidth = menu.width();
            var windowHeight = $(window).height();
            var windowWidth = $(window).width();

            // Make sure the whole menu is rendered within the viewport.
            if (menuHeight + y + yPadding > windowHeight) {
                y = y - menuHeight;
            }
            if (menuWidth + x + xPadding > windowWidth) {
                x = x - menuWidth;
            }

            // Must call show before we set the offset (offset can not be set on display: none elements).
            menu.fadeIn(settings.menuFadeDuration);
            menu.offset({ left: x, top: y });

            var dismissContextMenu = function () {
                $(document).unbind('click.jqtreecontextmenu');
                $el.unbind('tree.click.jqtreecontextmenu');
                menu.fadeOut(settings.menuFadeDuration);
            };

            // Make it possible to dismiss context menu by clicking somewhere in the document.
            $(document).bind('click.jqtreecontextmenu', function (e) {
                if (x != e.pageX || y != e.pageY) {
                    dismissContextMenu();
                }
            });
            // Dismiss context menu if another node in the tree is clicked.
            $el.bind('tree.click.jqtreecontextmenu', function () {
                dismissContextMenu();
            });

            // Make the selection follow the node that was right clicked on (if desired).
            if (settings.selectClickedNode && $el.tree('getSelectedNode') !== event.node) {
                $el.tree('selectNode', event.node);
            }

            // Handle click on menu items, if it's not disabled.
            menu.find('li').off('click.contextmenu').on('click.contextmenu', function (e) {
                e.stopImmediatePropagation();
                dismissContextMenu();
                $el.trigger('cm-jqtree.item.click', [event.node, $(this)]);
            });
        });

        return this;
    };
} (jQuery));
