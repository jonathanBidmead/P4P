"""
1. Ordered list of tasks = PA 

    Queue of tasks = [task1, task2, task3....]
    

-----------------------------------------------------------------------------------
2. PA publishes tasks to MA and SA
    if(previousTask == done):
        publish nextTask
        pop(previousTask)

-------------------------------------------------------------------------------------
3. MA and SA bid for performing tasks

    Queue of tasks recieved by agents = [task1, task2, task3]
    task = queue[0]
    timer.start()
    if(task == functionalityList AND available == TRUE AND not Timeout):
        bid = True
    else if(task == functionality AND available != True and not Timeout):
        bid = False
    else if(not Timeout):
        dont do anything
    else:
        queue.pop
        timer.reset()


-----------------------------------------------------------------------------------
4. PA requests CA to find path

    for each bidder:
        request CA to find min cost path
    return values to a cost list

------------------------------------------------------------------------------------

5. PA makes a decision and rewards the selected bidder

    List of costs recieved = [(agent cost + travel cost), ,  , , ]
    find min(list of costs)
    choose bidder
    reward bidder

"""




