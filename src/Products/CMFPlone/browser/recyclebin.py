from datetime import datetime
from plone.base import PloneMessageFactory as _
from plone.base.batch import Batch
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.base.utils import human_readable_size
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from urllib.parse import urlencode
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zExceptions import NotFound
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse

import logging
import uuid


logger = logging.getLogger(__name__)


class IRecycleBinForm(Interface):
    """Schema for the recycle bin form"""

    selected_items = schema.List(
        title=_("Selected Items"),
        description=_("Selected items for operations"),
        value_type=schema.TextLine(),
        required=False,
    )


class IRecycleBinItemForm(Interface):
    """Schema for the recycle bin item form"""

    target_container = schema.TextLine(
        title=_("Target container"),
        description=_(
            "Enter the path to the container where the item should be restored (e.g., /folder1/subfolder)"
        ),
        required=False,
    )


def _is_error_result(result):
    """Helper method to check if a result is an error dictionary

    Args:
        result: The result to check

    Returns:
        Boolean indicating if the result is an error dictionary
    """
    return isinstance(result, dict) and not result.get("success", True)


class RecycleBinWorkflowMixin:
    """Mixin class providing common workflow state methods for recycle bin views"""

    def _get_workflow_state(self, item):
        """Get the workflow state that the item had when it was deleted

        Args:
            item: The recycled item data dictionary

        Returns:
            String representing the workflow state or None
        """
        # Try to get the object from the item
        obj = item.get("object")
        if not obj:
            # For RecycleBinView, we need to get the full item data first
            if hasattr(self, "recycle_bin") and "recycle_id" in item:
                full_item_data = self.recycle_bin.get_item(item.get("recycle_id"))
                if full_item_data:
                    obj = full_item_data.get("object")

        if not obj:
            return None

        # Try to get the workflow state from the object
        try:
            # Get workflow tool
            workflow_tool = getToolByName(self.context, "portal_workflow")

            # Get the workflow state
            return workflow_tool.getInfoFor(obj, "review_state", None)

        except Exception as e:
            logger.warning(
                f"Could not determine workflow state for item {item.get('id')}: {e}"
            )
            return None

    def get_workflow_state_title(self, state, portal_type=None):
        """Get user-friendly title for workflow state

        Args:
            state: The workflow state ID
            portal_type: The portal type of the object (optional)

        Returns:
            Human-readable title for the state
        """
        if not state:
            return translate(_("Unknown"), context=self.request)

        workflow_tool = getToolByName(self.context, "portal_workflow")
        title = workflow_tool.getTitleForStateOnType(state, portal_type)
        return translate(title, context=self.request)

    def get_workflow_state_class(self, state):
        """Get CSS class for workflow state badge

        Args:
            state: The workflow state ID

        Returns:
            CSS class string for styling the state badge
        """
        if not state:
            return "bg-secondary text-white"

        # Color coding for different states
        state_classes = {
            "private": "bg-danger text-white",
            "published": "bg-success text-white",
            "pending": "bg-warning text-dark",
            "visible": "bg-info text-white",
            "internal": "bg-primary text-white",
            "draft": "bg-secondary text-white",
            "review": "bg-warning text-dark",
            "rejected": "bg-danger text-white",
            "external": "bg-dark text-white",
            "retracted": "bg-secondary text-white",
        }

        return state_classes.get(state, "bg-light text-dark")

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        return human_readable_size(size_bytes)


class RecycleBinView(RecycleBinWorkflowMixin, form.Form):
    """Form view for recycle bin management"""

    ignoreContext = True
    template = ViewPageTemplateFile("templates/recyclebin.pt")

    # Add an ID for the form
    id = "recyclebin-form"

    def __init__(self, context, request):
        super().__init__(context, request)
        self.recycle_bin = getUtility(IRecycleBin)
        self._batch = None

    @button.buttonAndHandler(_("Restore Selected"), name="restore")
    def handle_restore(self, action):
        """Restore selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            message = translate(
                _("No items selected for restoration."), context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        restored_count = 0
        missing_parents_count = 0
        missing_parent_items = []

        for item_id in selected_items:
            result = self.recycle_bin.restore_item(item_id)

            # Handle different types of return values
            if _is_error_result(result):
                # This is a failed restoration with an error message
                missing_parents_count += 1
                # Get the item title for better user feedback
                item_data = self.recycle_bin.get_item(item_id)
                if item_data:
                    missing_parent_items.append(
                        {
                            "id": item_id,
                            "title": item_data.get("title", "Unknown"),
                            "parent_path": item_data.get("parent_path", "Unknown"),
                            "error": result.get("error", "Unknown error"),
                        }
                    )
            elif result:
                # Successful restoration
                restored_count += 1

        # Success message for restored items
        if restored_count > 0:
            message = translate(
                _(
                    "${count} item(s) restored successfully.",
                    mapping={"count": restored_count},
                ),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")

        # Error message for items with missing parents
        if missing_parents_count > 0:
            if len(missing_parent_items) == 1:
                # Single item message
                item = missing_parent_items[0]
                message = translate(
                    _(
                        "The item '${title}' could not be restored because its original location no longer exists. "
                        "Please choose a different location.",
                        mapping={"title": item["title"]},
                    ),
                    context=self.request,
                )
                # Redirect to the item's detail page if only one item had this issue
                self.request.response.redirect(
                    f"{self.context.absolute_url()}/@@recyclebin-item/{item['id']}"
                )
            else:
                # Multiple items message
                message = translate(
                    _(
                        "${count} items could not be restored because their original locations no longer exist. "
                        "Please visit each item's detail page to specify a new location.",
                        mapping={"count": missing_parents_count},
                    ),
                    context=self.request,
                )

            IStatusMessage(self.request).addStatusMessage(message, type="error")

    @button.buttonAndHandler(_("Delete selected"), name="delete")
    def handle_delete(self, action):
        """Delete selected items handler"""
        data, errors = self.extractData()

        # Get the selected items from the request directly
        selected_items = self.request.form.get("selected_items", [])
        if not isinstance(selected_items, list):
            selected_items = [selected_items]

        if not selected_items:
            message = translate(
                _("No items selected for deletion."), context=self.request
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")
            return

        deleted_count = 0
        for item_id in selected_items:
            if self.recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = translate(
            _(
                "${count} item(s) permanently deleted.",
                mapping={"count": deleted_count},
            ),
            context=self.request,
        )
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    @button.buttonAndHandler(_("Empty Recycle Bin"), name="empty")
    def handle_empty(self, action):
        """Empty recycle bin handler"""
        data, errors = self.extractData()

        items = self.recycle_bin.get_items()
        deleted_count = 0

        for item in items:
            item_id = item["recycle_id"]
            if self.recycle_bin.purge_item(item_id):
                deleted_count += 1

        message = translate(
            _(
                "Recycle bin emptied. ${count} item(s) permanently deleted.",
                mapping={"count": deleted_count},
            ),
            context=self.request,
        )
        IStatusMessage(self.request).addStatusMessage(message, type="info")

    def get_search_query(self):
        """Get the search query from the request"""
        return self.request.form.get("search_query", "")

    def get_sort_option(self):
        """Get the current sort option from the request"""
        return self.request.form.get("sort_by", "date_desc")

    def get_filter_type(self):
        """Get the content type filter from the request"""
        return self.request.form.get("filter_type", "")

    def get_date_from(self):
        """Get the start date filter from the request"""
        date_str = self.request.form.get("date_from", "")
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%d").date()

        return None

    def get_date_to(self):
        """Get the end date filter from the request"""
        date_str = self.request.form.get("date_to", "")
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%d").date()

        return None

    def get_date_from_str(self):
        """Get the start date filter as string from the request"""
        return self.request.form.get("date_from", "")

    def get_date_to_str(self):
        """Get the end date filter as string from the request"""
        return self.request.form.get("date_to", "")

    def get_filter_deleted_by(self):
        """Get the deleted by user filter from the request"""
        return self.request.form.get("filter_deleted_by", "")

    def get_filter_has_subitems(self):
        """Get the has sub-items filter from the request"""
        return self.request.form.get("filter_has_subitems", "")

    def get_filter_language(self):
        """Get the language filter from the request"""
        return self.request.form.get("filter_language", "")

    def get_filter_workflow_state(self):
        """Get the workflow state filter from the request"""
        return self.request.form.get("filter_workflow_state", "")

    def get_b_start(self):
        """Get the batch start index from the request"""
        return int(self.request.form.get("b_start", 0))

    def get_b_size(self):
        """Get the batch size from the request (default 20)"""
        return int(self.request.form.get("b_size", 20))

    def get_batch(self):
        """Get a batch of items for pagination"""
        if self._batch is None:
            # Get all items first (this applies filters and sorting)
            all_items = self.get_items()

            # Create batch with pagination
            b_start = self.get_b_start()
            b_size = self.get_b_size()

            self._batch = Batch(all_items, size=b_size, start=b_start, orphan=1)

        return self._batch

    def get_page_size_options(self):
        """Get available page size options"""
        return [10, 20, 50, 100]

    def get_sort_labels(self):
        """Get a dictionary of human-readable sort option labels"""
        return {
            "date_desc": _("Newest first (default)"),
            "date_asc": _("Oldest first"),
            "title_asc": _("Title (A-Z)"),
            "title_desc": _("Title (Z-A)"),
            "type_asc": _("Type (A-Z)"),
            "type_desc": _("Type (Z-A)"),
            "path_asc": _("Path (A-Z)"),
            "path_desc": _("Path (Z-A)"),
            "size_asc": _("Size (smallest first)"),
            "size_desc": _("Size (largest first)"),
            "workflow_asc": _("Workflow state (A-Z)"),
            "workflow_desc": _("Workflow state (Z-A)"),
        }

    def get_clear_url(self, param_to_remove):
        """Generate a URL that clears a specific filter parameter while preserving others

        Args:
            param_to_remove: The parameter name to remove from the URL

        Returns:
            URL string with the specified parameter removed
        """
        base_url = f"{self.context.absolute_url()}/@@recyclebin"
        params = {}

        # Add search query if it exists and is not being removed
        if param_to_remove != "search_query" and self.get_search_query():
            params["search_query"] = self.get_search_query()

        # Add filter type if it exists and is not being removed
        if param_to_remove != "filter_type" and self.get_filter_type():
            params["filter_type"] = self.get_filter_type()

        # Add date from filter if it exists and is not being removed
        date_from = self.get_date_from()
        if param_to_remove != "date_from" and date_from:
            params["date_from"] = date_from.strftime("%Y-%m-%d")

        # Add date to filter if it exists and is not being removed
        date_to = self.get_date_to()
        if param_to_remove != "date_to" and date_to:
            params["date_to"] = date_to.strftime("%Y-%m-%d")

        # Add deleted by filter if it exists and is not being removed
        if param_to_remove != "filter_deleted_by" and self.get_filter_deleted_by():
            params["filter_deleted_by"] = self.get_filter_deleted_by()

        # Add has sub-items filter if it exists and is not being removed
        if param_to_remove != "filter_has_subitems" and self.get_filter_has_subitems():
            params["filter_has_subitems"] = self.get_filter_has_subitems()

        # Add language filter if it exists and is not being removed
        if param_to_remove != "filter_language" and self.get_filter_language():
            params["filter_language"] = self.get_filter_language()

        # Add workflow state filter if it exists and is not being removed
        if (
            param_to_remove != "filter_workflow_state"
            and self.get_filter_workflow_state()
        ):
            params["filter_workflow_state"] = self.get_filter_workflow_state()

        # Add sort option if it exists, is not default, and is not being removed
        sort_option = self.get_sort_option()
        if param_to_remove != "sort_by" and sort_option != "date_desc":
            params["sort_by"] = sort_option

        # Construct final URL using urlencode for proper URL encoding
        if params:
            query_string = urlencode(params)
            return f"{base_url}?{query_string}"
        return base_url

    def get_available_types(self, items):
        """Get a list of all content types present in the recycle bin"""
        types = set()
        for item in items:
            item_type = item.get("type")
            if item_type:
                types.add(item_type)
        return sorted(list(types))

    def get_available_deleted_by_users(self, items):
        """Get a list of all users who have deleted items in the recycle bin"""
        users = set()
        for item in items:
            deleted_by = item.get("deleted_by")
            if deleted_by:
                users.add(deleted_by)
        return sorted(list(users))

    def get_available_languages(self, items):
        """Get a list of all languages present in the recycle bin"""
        languages = set()
        for item in items:
            language = item.get("language")
            if language:
                languages.add(language)
        return sorted(list(languages))

    def get_available_workflow_states(self, items):
        """Get a list of all workflow states present in the recycle bin"""
        states = set()
        for item in items:
            workflow_state = item.get("workflow_state")
            if workflow_state:
                states.add(workflow_state)
        return sorted(list(states))

    def _check_item_matches_search(self, item, search_query):
        """Check if an item matches the search query.

        Args:
            item: The item to check
            search_query: The search query string (lowercase)

        Returns:
            Boolean indicating if the item matches
        """
        # Search in title
        if search_query in item.get("title", "").lower():
            return True

        # Search in path
        if search_query in item.get("path", "").lower():
            return True

        # Search in parent path
        if search_query in item.get("parent_path", "").lower():
            return True

        # Search in ID
        if search_query in item.get("id", "").lower():
            return True

        # Search in type
        if search_query in item.get("type", "").lower():
            return True

        return False

    def _check_item_matches_date_range(self, item, date_from, date_to):
        """Check if an item's deletion date falls within the specified date range.

        Args:
            item: The item to check
            date_from: Start date as date object or None
            date_to: End date as date object or None

        Returns:
            Boolean indicating if the item matches the date range
        """
        if not date_from and not date_to:
            return True  # No date filter applied

        deletion_date = item.get("deletion_date")
        if not deletion_date:
            return False  # Can't filter items without deletion date

        # Convert deletion_date to date object for comparison
        if hasattr(deletion_date, "date"):
            item_date = deletion_date.date()
        else:
            # If it's already a date object
            item_date = deletion_date

        # Check date range (dates are already parsed)
        if date_from and item_date < date_from:
            return False

        if date_to and item_date > date_to:
            return False

        return True

    def _find_matching_children(self, item, search_query):
        """Find children of an item that match the search query.

        Args:
            item: The parent item to check children of
            search_query: The search query string (lowercase)

        Returns:
            List of matching children or None if no matches
        """
        if "children" in item and isinstance(item["children"], dict):
            child_matches = []

            for child_id, child_data in item["children"].items():
                # Check each child for matches
                if (
                    search_query in child_data.get("title", "").lower()
                    or search_query in child_data.get("path", "").lower()
                    or search_query in child_data.get("id", "").lower()
                    or search_query in child_data.get("type", "").lower()
                ):
                    child_matches.append(child_data)

            if child_matches:
                return child_matches

        return None

    def _apply_sorting(self, items, sort_option):
        """Apply sorting to the items list.

        Args:
            items: List of items to sort
            sort_option: The sort option to apply

        Returns:
            Sorted list of items
        """
        match sort_option:
            case "title_asc":
                items.sort(key=lambda x: x.get("title", "").lower())
            case "title_desc":
                items.sort(key=lambda x: x.get("title", "").lower(), reverse=True)
            case "type_asc":
                items.sort(key=lambda x: x.get("type", "").lower())
            case "type_desc":
                items.sort(key=lambda x: x.get("type", "").lower(), reverse=True)
            case "path_asc":
                items.sort(key=lambda x: x.get("path", "").lower())
            case "path_desc":
                items.sort(key=lambda x: x.get("path", "").lower(), reverse=True)
            case "size_asc":
                items.sort(key=lambda x: x.get("size", 0))
            case "size_desc":
                items.sort(key=lambda x: x.get("size", 0), reverse=True)
            case "date_asc":
                items.sort(key=lambda x: x.get("deletion_date", datetime.now()))
            case "workflow_asc":
                items.sort(key=lambda x: (x.get("workflow_state") or "").lower())
            case "workflow_desc":
                items.sort(
                    key=lambda x: (x.get("workflow_state") or "").lower(), reverse=True
                )
            case _:
                # Default: date_desc
                items.sort(
                    key=lambda x: x.get("deletion_date", datetime.now()), reverse=True
                )
        return items

    def get_items(self):
        """Get all items in the recycle bin"""
        items = self.recycle_bin.get_items()

        # Get filters early to avoid multiple lookups during the loop
        filter_type = self.get_filter_type()
        search_query = self.get_search_query().lower()
        date_from = self.get_date_from()
        date_to = self.get_date_to()
        filter_deleted_by = self.get_filter_deleted_by()
        filter_has_subitems = self.get_filter_has_subitems()
        filter_language = self.get_filter_language()
        filter_workflow_state = self.get_filter_workflow_state()

        # Create a list of all items that are children of a parent in the recycle bin
        child_items_to_exclude = []
        for item in items:
            # If this item is a parent with children, add its children to exclusion list
            if "children" in item:
                for child_id in item.get("children", {}):
                    child_items_to_exclude.append(child_id)

        logger.debug(f"Child items to exclude: {child_items_to_exclude}")

        # Process items with direct matches
        filtered_items = []
        items_with_matching_children = []

        for item in items:
            if item.get("id") not in child_items_to_exclude:
                # Apply type filtering
                if filter_type and item.get("type") != filter_type:
                    continue

                # Apply date range filtering
                if not self._check_item_matches_date_range(item, date_from, date_to):
                    continue

                # Apply deleted by filtering
                if filter_deleted_by and item.get("deleted_by") != filter_deleted_by:
                    continue

                # Apply has sub-items filtering
                if filter_has_subitems:
                    has_children = "children" in item and item["children"]
                    if filter_has_subitems == "with_subitems" and not has_children:
                        continue
                    elif filter_has_subitems == "without_subitems" and has_children:
                        continue

                # Apply language filtering
                if filter_language and item.get("language") != filter_language:
                    continue

                # Apply workflow state filtering
                if (
                    filter_workflow_state
                    and item.get("workflow_state") != filter_workflow_state
                ):
                    continue

                # Add children count information
                if "children" in item:
                    item["children_count"] = len(item["children"])

                # Apply search query filtering
                if search_query:
                    # Check for direct matches
                    if self._check_item_matches_search(item, search_query):
                        filtered_items.append(item)
                        continue

                    # Check for matches in children
                    matching_children = self._find_matching_children(item, search_query)
                    if matching_children:
                        # Make a copy of the item so we don't modify the original
                        parent_item = item.copy()
                        parent_item["matching_children"] = matching_children
                        parent_item["matching_children_count"] = len(matching_children)
                        items_with_matching_children.append(parent_item)
                else:
                    # No search query, include all items
                    filtered_items.append(item)

        # Combine results based on whether we're searching or not
        if search_query:
            items = filtered_items + items_with_matching_children
        else:
            items = filtered_items

        # Apply sorting
        return self._apply_sorting(items, self.get_sort_option())


@implementer(IPublishTraverse)
class RecycleBinItemView(RecycleBinWorkflowMixin, form.Form):
    """View for managing individual recycled items"""

    ignoreContext = True
    template = ViewPageTemplateFile("templates/recyclebin_item.pt")
    item_id = None
    fields = field.Fields(IRecycleBinItemForm)

    def __init__(self, context, request):
        super().__init__(context, request)
        self.recycle_bin = getUtility(IRecycleBin)

    def publishTraverse(self, request, name):
        """Handle URLs like /recyclebin-item/[item_id]"""
        logger.debug(f"RecycleBinItemView.publishTraverse called with name: {name}")
        if self.item_id is None:  # First traversal
            self.item_id = name
            logger.debug(f"Set item_id to: {self.item_id}")
            return self
        logger.debug(f"Additional traversal attempted with name: {name}")
        raise NotFound(self, name, request)

    def update(self):
        super().update()

        # Check if we have a valid item before proceeding
        if self.item_id is None:
            logger.debug("No item_id set, redirecting to main recyclebin view")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
            return

        # Handle restoration of children
        if "restore.child" in self.request.form:
            self._handle_child_restoration()

    @button.buttonAndHandler(_("Restore item"), name="restore")
    def handle_restore(self, action):
        """Restore this item"""
        data, errors = self.extractData()
        if errors:
            return

        # Get target container if specified
        target_path = data.get("target_container", "")
        target_container = None

        if target_path:
            try:
                target_container = self.context.unrestrictedTraverse(target_path)
            except (KeyError, AttributeError):
                message = translate(
                    _(
                        "The folder '${path}' where you are trying to restore this item cannot be found. It may have been moved or deleted. Please choose a different location.",
                        mapping={"path": target_path},
                    ),
                    context=self.request,
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")
                return

        # Restore the item
        item = self.get_item()
        if not item:
            message = translate(
                _("Item not found. It may have been already restored or deleted."),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )
            return

        result = self.recycle_bin.restore_item(self.item_id, target_container)

        # Check if we got an error dictionary using helper method
        if _is_error_result(result):
            # Show the error message
            error_message = result.get(
                "error", "Unknown error occurred during restoration"
            )
            IStatusMessage(self.request).addStatusMessage(error_message, type="error")

            # Redirect back to the item view to allow selecting a different target
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin-item/{self.item_id}"
            )
            return

        restored_obj = result

        if restored_obj:
            message = translate(
                _(
                    "Item '${title}' successfully restored.",
                    mapping={"title": restored_obj.Title()},
                ),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="info")

            # Determine the appropriate URL to redirect to after restoration
            context_state = getMultiAdapter(
                (restored_obj, self.request), name="plone_context_state"
            )
            redirect_url = context_state.view_url()

            self.request.response.redirect(redirect_url)
        else:
            message = translate(
                _(
                    "Failed to restore item. It may have been already restored or deleted."
                ),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            self.request.response.redirect(
                f"{self.context.absolute_url()}/@@recyclebin"
            )

    @button.buttonAndHandler(_("Permanently delete"), name="delete")
    def handle_delete(self, action):
        """Permanently delete this item"""
        data, errors = self.extractData()

        # Get item info before deletion
        item = self.get_item()
        if item:
            item_title = item.get("title", "Unknown")

            if self.recycle_bin.purge_item(self.item_id):
                message = translate(
                    _(
                        "Item '${title}' permanently deleted.",
                        mapping={"title": item_title},
                    ),
                    context=self.request,
                )
                IStatusMessage(self.request).addStatusMessage(message, type="info")
            else:
                message = translate(
                    _(
                        "Failed to delete item '${title}'.",
                        mapping={"title": item_title},
                    ),
                    context=self.request,
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")
        else:
            message = translate(
                _("Item not found. It may have been already deleted."),
                context=self.request,
            )
            IStatusMessage(self.request).addStatusMessage(message, type="error")

        self.request.response.redirect(f"{self.context.absolute_url()}/@@recyclebin")

    def _handle_child_restoration(self):
        """Extract child restoration logic to separate method for clarity"""
        child_id = self.request.form.get("child_id")
        target_path = self.request.form.get("target_path")

        if child_id and target_path:
            try:
                # Get item data
                item_data = self.recycle_bin.get_item(self.item_id)

                if item_data and "children" in item_data:
                    child_data = item_data["children"].get(child_id)
                    if child_data:
                        # Try to get target container
                        try:
                            target_container = self.context.unrestrictedTraverse(
                                target_path
                            )

                            # Create a temporary storage entry for the child
                            temp_id = str(uuid.uuid4())
                            self.recycle_bin.storage[temp_id] = child_data

                            # Restore the child
                            result = self.recycle_bin.restore_item(
                                temp_id, target_container
                            )

                            # Check if we got an error dictionary
                            if _is_error_result(result):
                                error_message = result.get(
                                    "error", "Unknown error during child restoration"
                                )
                                IStatusMessage(self.request).addStatusMessage(
                                    error_message, type="error"
                                )
                                return

                            restored_obj = result

                            if restored_obj:
                                # Remove child from parent's children dict
                                del item_data["children"][child_id]
                                item_data["children_count"] = len(item_data["children"])

                                # Persist the changes to ZODB
                                self.recycle_bin.storage[self.item_id] = item_data

                                message = translate(
                                    _(
                                        "Child item '${title}' successfully restored.",
                                        mapping={"title": child_data["title"]},
                                    ),
                                    context=self.request,
                                )
                                IStatusMessage(self.request).addStatusMessage(
                                    message, type="info"
                                )
                                self.request.response.redirect(
                                    restored_obj.absolute_url()
                                )
                                return
                        except (KeyError, AttributeError):
                            message = translate(
                                _(
                                    "Target location not found: ${path}",
                                    mapping={"path": target_path},
                                ),
                                context=self.request,
                            )
                            IStatusMessage(self.request).addStatusMessage(
                                message, type="error"
                            )
            except Exception as e:
                logger.error(f"Error restoring child item: {e}")

                message = translate(
                    _("Failed to restore child item."), context=self.request
                )
                IStatusMessage(self.request).addStatusMessage(message, type="error")

    def get_item(self):
        """Get the specific recycled item"""
        if not self.item_id:
            return None

        item = self.recycle_bin.get_item(self.item_id)
        if item is None:
            logger.debug(f"No item found in recycle bin with ID: {self.item_id}")
        else:
            logger.debug(
                f"Found item: {item.get('title', 'Unknown')} of type {item.get('type', 'Unknown')}"
            )
            # Add children count information if not already present
            if "children" in item and "children_count" not in item:
                item["children_count"] = len(item["children"])

        return item

    def get_children(self):
        """Get the children of this item if it's a folder or collection"""
        item = self.get_item()
        if item and "children" in item:
            return list(item["children"].values())
        return []


class RecycleBinEnabled(BrowserView):
    """View to check if the recycle bin is enabled"""

    def __call__(self):
        """Return True if the recycle bin is enabled, False otherwise"""
        recycle_bin = getUtility(IRecycleBin)
        return recycle_bin.is_enabled()
