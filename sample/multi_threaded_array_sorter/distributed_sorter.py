import queue
import sys
from quick_sort_thread import QuickSortThread

def distributed_sorter():
    message_queue = queue.Queue()

    QuickSortThread(message_queue)

    while True:
        print("\nEnter details:")        
        data = input("Data (ex: 1,5,4,3,9): ")
        type = input("Type (1=BubbleSort,2=MergeSort,3=QuickSort): ")
        job_details = {"data": data, "type":type}

        if type == "1":
            message_queue.put(job_details)

        elif type == "2":
            message_queue.put(job_details)

        elif type == "3":
            message_queue.put(job_details)   

        elif type == "q":
            break

if "__main__" == __name__:
    sys.exit(distributed_sorter())