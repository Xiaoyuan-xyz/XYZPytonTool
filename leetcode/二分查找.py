from typing import List

questions = [
    {
        "nums": [-1, 0, 3, 5, 9, 12],
        "target": 9,
        "answer": 4,
    },
    {
        "nums": [-1, 0, 3, 5, 9, 12],
        "target": 2,
        "answer": -1,
    },
    {
        "nums": [-1, 0, 3, 5, 9, 12],
        "target": -3,
        "answer": -1,
    },
    {
        "nums": [-1, 0, 3, 5, 9, 12],
        "target": 0,
        "answer": 1,
    },
]

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        i = 0
        j = len(nums) - 1
        while i <= j:
            mid = (i + j) // 2
            if nums[mid] == target:
                return mid
            elif nums[mid] > target:
                j = mid - 1
            else:
                i = mid + 1
        return -1

if __name__ == '__main__':
    sol = Solution()
    for q in questions:
        answer = sol.search(q["nums"], q["target"])
        if answer == q["answer"]:
            print("PASS")
        else:
            print("FAIL")