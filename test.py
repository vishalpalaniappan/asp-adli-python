def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            if should_swap(arr[j], arr[j + 1]):
                swap(arr, j, j + 1)

def should_swap(a, b):
    """Return True if a and b need to be swapped."""
    return a > b

def swap(arr, i, j):
    """Swap the elements at index i and j in the array."""
    arr[i], arr[j] = arr[j], arr[i]

def print_array(arr):
    """Print the array elements."""
    print("Sorted array:", arr)

def main():
    arr = [64, 34, 25, 12, 22, 11, 90]
    print("Original array:", arr)
    bubble_sort(arr)
    print_array(arr)

if __name__ == "__main__":
    main()