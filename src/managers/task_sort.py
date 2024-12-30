def task_sort(tasks):
    n = len(tasks)
    recQuickSort(tasks, 0, n - 1)


def recQuickSort(tasks, first, last):
    if first >= last:
        return
    else:
        pivot = tasks[first]
        pos = partitionTasks(tasks, first, last)

        recQuickSort(tasks, first, pos-1)
        recQuickSort(tasks, pos+1, last)


def partitionTasks(tasks, first, last):
    pivot = tasks[first]

    left = first + 1
    right = last

    while left <= right:
        while left < right and tasks[left]["timestamp"] < pivot["timestamp"]:
            left += 1

        while right >= left and tasks[right]["timestamp"] >= pivot["timestamp"]:
            right -= 1

        if left < right:
            tmp = tasks[left]
            tasks[left] = tasks[right]
            tasks[right] = tmp

    if right != first:
        tasks[first] = tasks[right]
        tasks[right] = pivot

    return right
