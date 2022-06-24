```cpp
class Solution {
public:
    string reverseLeftWords(string s, int n) {
        int tmp = s.size()-n;
        reverse(s.begin(),s.end());
        reverse(s.begin(),s.begin()+tmp);
        reverse(s.begin()+tmp,s.end());
        return s;
    }
};
```
reverse 和容器的begin end