#### 方法一：哈希表 / Set  
```
class Solution {
public:
    int findRepeatNumber(vector<int>& nums) {
        unordered_map<int, bool> map;
        for(int num : nums) {
            if(map[num]) return num;
            map[num] = true;
        }
        return -1;
    }
};
```
```
class Solution {
public:
    int findRepeatNumber(vector<int>& nums) {
        unordered_map<int,int> map;

        for(int num : nums){
            map[num]++;
            if(map[num] >= 2) return num;
        }
        return nums[nums.size() - 1];
    }
};


```

#### 方法二：原地交换  
```
class Solution {
public:
    int findRepeatNumber(vector<int>& nums) {
        int N = nums.size();
        for(int i=0; i<N; i++){
            while(nums[i] != i){              //发现这个坑里的萝卜不是自己家的
                int temp = nums[i];           //看看你是哪家的萝卜
                if(nums[temp] == temp)        //看看你家里有没有和你一样的萝卜
                    return temp;            //发现你家里有了和你一样的萝卜，那你就多余了，上交国家
                else                        //你家里那个萝卜和你不一样    
                    swap(nums[temp], nums[i]);  //把你送回你家去，然后把你家里的那个萝卜拿回来
            }
        }
        return -1;
    }
};

```
