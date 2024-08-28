from typing import List

class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        left = 0
        right = 0
        now_sum = 0
        while now_sum < target and right < len(nums):
            now_sum += nums[right]
            right += 1
        if now_sum < target:
            return 0
        min_len = right - left
        while True:
            if now_sum - nums[left] >= target:
                left += 1
                now_sum -= nums[left]
                if right - left < min_len:
                    min_len = right - left
            elif right == len(nums):
                return min_len
            else:
                now_sum += nums[right]
                right += 1
            
        

if __name__ == '__main__':
    s = Solution()
    print(s.minSubArrayLen(213, [12,28,83,4,25,26,25,2,25,25,25,12]))