def build_filters(
    metadata_filters: dict | None
):

    if not metadata_filters:
        return []

    filters = []

    for field, value in metadata_filters.items():

        if isinstance(
            value,
            (list, tuple)
        ):

            filters.append({
                "terms": {
                    field: list(value)
                }
            })

        else:

            filters.append({
                "term": {
                    field: value
                }
            })

    return filters