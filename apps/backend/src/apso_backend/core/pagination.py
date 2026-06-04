from apso_backend.schemas.common import Page, PageMeta


def page_from_items(items: list, *, limit: int) -> Page:
    return Page(items=items, meta=PageMeta(limit=limit, count=len(items), next_cursor=None))

