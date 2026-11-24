

@app.exception_handler(CollectionGroupNotFoundError)
async def collection_group_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Collection group not found"})
