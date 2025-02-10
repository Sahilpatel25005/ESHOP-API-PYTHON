import multiprocessing
import uvicorn
from product import app1

def run_app1():
    uvicorn.run("app1/main.py", host="0.0.0.0", port=8000, reload=True)

def run_app2():
    uvicorn.run("app2/main.py", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_app1)
    p2 = multiprocessing.Process(target=run_app2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
