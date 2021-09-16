# Row Level Caching for Django Models


## Overview

This module provides row-level caching support for Django models.

This works by insertion of a custom Manager for the class which handles get
requests for primary key, fetching from cache and saving to cache as necessary.
Cache is cleared via signals whenever records are updated or deleted.

Foreign keys, both many-to-one and meny-to-many are fully supported.


## Status

This django app is currently in beta status
