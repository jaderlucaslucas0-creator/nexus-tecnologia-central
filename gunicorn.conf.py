def post_worker_init(worker):
    # Register the optional Nexus modules after Flask has been created.
    import extra_routes  # noqa: F401
