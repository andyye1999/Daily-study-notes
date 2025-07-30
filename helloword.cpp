#include <bits/stdc++.h>

using namespace std;

// Simple Hello World program
int main() {
    std::cout << "Hello, World!" << std::endl;
    std::vector<int> nums;
    int num;
    while (std::cin >> num)
    {
        nums.push_back(num);
        // 读到换行符，终止循环
        if (getchar() == '\n')
        {
            break;
        }
    }

    // 验证是否读入成功
    for (int i = 0; i < nums.size(); i++)
    {
        std::cout << nums[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}