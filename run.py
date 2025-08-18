import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:create_app",  # import string (module:function)
        host="127.0.0.1",
        port=8000,
        reload=True,
        factory=True
    )
