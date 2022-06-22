```cpp
class Solution {
public:
    string replaceSpace(string s) {
        int count = 0;
        int n = s.size();
        for(int i = 0;i<n;i++)
        {
            if(s[i] == ' ')
            {
                count++;
            }
        }
        s.resize(n + count * 2);
        int nsize = s.size();
        for (int i = n - 1, j = nsize - 1; i>=0; i--, j--)
        {
            if(s[i] != ' ')
            {
                s[j] = s[i];
            }
            else
            {
                s[j] = '0';
                s[j - 1] = '2';
                s[j - 2] = '%';
                j-=2;
            }
            
        }
        return s;
    }
};
```
从前向后填充就是O(n^2)的算法了，因为每次添加元素都要将添加元素之后的所有元素向后移动。

**其实很多数组填充类的问题，都可以先预先给数组扩容带填充后的大小，然后在从后向前进行操作。**

这么做有两个好处：

1.  不用申请新数组。
2.  从后向前填充元素，避免了从前先后填充元素要来的 每次添加元素都要将添加元素之后的所有元素向后移动。
s.resize 函数，扩充长度