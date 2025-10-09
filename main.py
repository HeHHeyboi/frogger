class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y


p1 = Point(0, 0)
p2 = Point(1, 1)
arr1 = [Point(0, 0), Point(1, 1)]
arr2 = [Point(0, 0), Point(1, 1)]
arr3 = [p1, p2]
arr4 = [p1, p2]
arr5 = [[0, 0], [1, 1]]
arr6 = [[0, 0], [1, 1]]

print(arr1 == arr2)
print(arr3 == arr4)
print(arr5 == arr6)
